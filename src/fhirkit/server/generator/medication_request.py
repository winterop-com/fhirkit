"""MedicationRequest resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import MEDICATIONS_RXNORM, CodingTemplate, make_codeable_concept


class MedicationRequestGenerator(FHIRResourceGenerator):
    """Generator for FHIR MedicationRequest resources."""

    # Common dosage instructions
    DOSAGE_INSTRUCTIONS = [
        "Take 1 tablet by mouth once daily",
        "Take 1 tablet by mouth twice daily",
        "Take 1 tablet by mouth three times daily",
        "Take 1 tablet by mouth every morning",
        "Take 1 tablet by mouth at bedtime",
        "Take 2 tablets by mouth once daily",
        "Take as needed for pain",
        "Apply topically twice daily",
        "Inhale 2 puffs as needed",
    ]

    # Common routes
    ROUTES = [
        {"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"},
        {"system": "http://snomed.info/sct", "code": "47625008", "display": "Intravenous route"},
        {"system": "http://snomed.info/sct", "code": "78421000", "display": "Intramuscular route"},
        {"system": "http://snomed.info/sct", "code": "6064005", "display": "Topical route"},
        {"system": "http://snomed.info/sct", "code": "46713006", "display": "Nasal route"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        medication_request_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        encounter_ref: str | None = None,
        medication_code: CodingTemplate | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MedicationRequest resource.

        Args:
            medication_request_id: MedicationRequest ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            practitioner_ref: Practitioner reference
            encounter_ref: Encounter reference
            medication_code: Specific medication coding (random if None)

        Returns:
            MedicationRequest FHIR resource
        """
        if medication_request_id is None:
            medication_request_id = self._generate_id()

        # Select medication
        if medication_code is None:
            medication_code = self.faker.random_element(MEDICATIONS_RXNORM)

        # Generate authored date
        authored_on = self.faker.date_time_between(
            start_date="-1y",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Select status (weighted towards active)
        status_weights = [
            ("active", 0.6),
            ("completed", 0.25),
            ("cancelled", 0.05),
            ("stopped", 0.1),
        ]
        roll = self.faker.random.random()
        cumulative = 0.0
        status = "active"
        for s, weight in status_weights:
            cumulative += weight
            if roll < cumulative:
                status = s
                break

        # Generate dosage instruction
        dosage_text = self.faker.random_element(self.DOSAGE_INSTRUCTIONS)
        route = self.faker.random_element(self.ROUTES)

        medication_request: dict[str, Any] = {
            "resourceType": "MedicationRequest",
            "id": medication_request_id,
            "meta": self._generate_meta(),
            "status": status,
            "intent": "order",
            "medicationCodeableConcept": make_codeable_concept(medication_code),
            "authoredOn": authored_on.isoformat(),
            "dosageInstruction": [
                {
                    "text": dosage_text,
                    "route": make_codeable_concept(route),
                    "timing": {
                        "repeat": {
                            "frequency": self.faker.random_element([1, 2, 3, 4]),
                            "period": 1,
                            "periodUnit": "d",
                        }
                    },
                }
            ],
            "dispenseRequest": {
                "numberOfRepeatsAllowed": self.faker.random_int(min=0, max=11),
                "quantity": {
                    "value": self.faker.random_element([30, 60, 90]),
                    "unit": "tablets",
                    "system": "http://unitsofmeasure.org",
                    "code": "{tbl}",
                },
                "expectedSupplyDuration": {
                    "value": 30,
                    "unit": "days",
                    "system": "http://unitsofmeasure.org",
                    "code": "d",
                },
            },
        }

        if patient_ref:
            medication_request["subject"] = {"reference": patient_ref}

        if practitioner_ref:
            medication_request["requester"] = {"reference": practitioner_ref}

        if encounter_ref:
            medication_request["encounter"] = {"reference": encounter_ref}

        return medication_request
