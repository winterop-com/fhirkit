"""MedicationAdministration resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import MEDICATIONS_RXNORM, CodingTemplate, make_codeable_concept


class MedicationAdministrationGenerator(FHIRResourceGenerator):
    """Generator for FHIR MedicationAdministration resources.

    MedicationAdministration records when a medication is actually given to a patient,
    typically in inpatient or clinical settings. This is distinct from MedicationRequest
    (the order) and MedicationStatement (what patient reports taking).
    """

    # Administration routes
    ROUTES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"},
        {"system": "http://snomed.info/sct", "code": "47625008", "display": "Intravenous route"},
        {"system": "http://snomed.info/sct", "code": "78421000", "display": "Intramuscular route"},
        {"system": "http://snomed.info/sct", "code": "34206005", "display": "Subcutaneous route"},
        {"system": "http://snomed.info/sct", "code": "6064005", "display": "Topical route"},
    ]

    # Body sites for administration
    BODY_SITES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "368208006", "display": "Left upper arm"},
        {"system": "http://snomed.info/sct", "code": "368209003", "display": "Right upper arm"},
        {"system": "http://snomed.info/sct", "code": "61396006", "display": "Left thigh"},
        {"system": "http://snomed.info/sct", "code": "11207009", "display": "Right thigh"},
        {"system": "http://snomed.info/sct", "code": "42859004", "display": "Gluteal region"},
    ]

    # Status reasons for not-done
    NOT_DONE_REASONS: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "182856006", "display": "Patient refused medication"},
        {"system": "http://snomed.info/sct", "code": "266711001", "display": "NPO (nil per os)"},
        {"system": "http://snomed.info/sct", "code": "275929009", "display": "Patient asleep"},
        {"system": "http://snomed.info/sct", "code": "410536001", "display": "Contraindicated"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        administration_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        practitioner_ref: str | None = None,
        medication_request_ref: str | None = None,
        medication_code: CodingTemplate | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MedicationAdministration resource.

        Args:
            administration_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            practitioner_ref: Practitioner who administered
            medication_request_ref: Reference to the MedicationRequest
            medication_code: Specific medication coding (random if None)
            status: Administration status (random if None)

        Returns:
            MedicationAdministration FHIR resource
        """
        if administration_id is None:
            administration_id = self._generate_id()

        # Select medication
        if medication_code is None:
            medication_code = self.faker.random_element(MEDICATIONS_RXNORM)

        # Generate status (weighted towards completed)
        if status is None:
            status_weights = [
                ("completed", 0.75),
                ("in-progress", 0.10),
                ("not-done", 0.05),
                ("on-hold", 0.05),
                ("stopped", 0.05),
            ]
            roll = self.faker.random.random()
            cumulative = 0.0
            status = "completed"
            for s, weight in status_weights:
                cumulative += weight
                if roll < cumulative:
                    status = s
                    break

        # Generate effective time
        effective_time = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        route = self.faker.random_element(self.ROUTES)

        administration: dict[str, Any] = {
            "resourceType": "MedicationAdministration",
            "id": administration_id,
            "meta": self._generate_meta(),
            "status": status,
            "medicationCodeableConcept": make_codeable_concept(medication_code),
            "effectiveDateTime": effective_time.isoformat(),
            "dosage": {
                "route": make_codeable_concept(route),
                "dose": {
                    "value": self.faker.random_element([1, 2, 5, 10, 25, 50, 100, 250, 500]),
                    "unit": self.faker.random_element(["mg", "mL", "mcg", "units"]),
                    "system": "http://unitsofmeasure.org",
                    "code": self.faker.random_element(["mg", "mL", "[IU]", "ug"]),
                },
            },
        }

        # Add body site for injections
        if route["code"] in ["78421000", "34206005"]:  # IM or SC
            administration["dosage"]["site"] = make_codeable_concept(self.faker.random_element(self.BODY_SITES))

        # Add reason for not-done status
        if status == "not-done":
            administration["statusReason"] = [make_codeable_concept(self.faker.random_element(self.NOT_DONE_REASONS))]

        if patient_ref:
            administration["subject"] = {"reference": patient_ref}

        if encounter_ref:
            administration["context"] = {"reference": encounter_ref}

        if practitioner_ref:
            administration["performer"] = [
                {
                    "actor": {"reference": practitioner_ref},
                    "function": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/med-admin-perform-function",
                                "code": "performer",
                                "display": "Performer",
                            }
                        ]
                    },
                }
            ]

        if medication_request_ref:
            administration["request"] = {"reference": medication_request_ref}

        return administration
