"""MedicationStatement resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import MEDICATIONS_RXNORM, CodingTemplate, make_codeable_concept


class MedicationStatementGenerator(FHIRResourceGenerator):
    """Generator for FHIR MedicationStatement resources.

    MedicationStatement records what a patient reports they are taking,
    which may differ from what was prescribed (MedicationRequest) or
    what was actually given (MedicationAdministration).
    """

    # Information sources
    INFORMATION_SOURCES: list[dict[str, str]] = [
        {
            "code": "patient",
            "display": "Patient",
            "system": "http://terminology.hl7.org/CodeSystem/medication-statement-source",
        },
        {
            "code": "patient-family",
            "display": "Patient family member",
            "system": "http://terminology.hl7.org/CodeSystem/medication-statement-source",
        },
        {
            "code": "practitioner",
            "display": "Practitioner",
            "system": "http://terminology.hl7.org/CodeSystem/medication-statement-source",
        },
        {
            "code": "pharmacy",
            "display": "Pharmacy",
            "system": "http://terminology.hl7.org/CodeSystem/medication-statement-source",
        },
    ]

    # Reason codes for taking medication
    REASON_CODES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "73211009", "display": "Diabetes mellitus"},
        {"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertensive disorder"},
        {"system": "http://snomed.info/sct", "code": "25064002", "display": "Headache"},
        {"system": "http://snomed.info/sct", "code": "82423001", "display": "Chronic pain"},
        {"system": "http://snomed.info/sct", "code": "195967001", "display": "Asthma"},
        {"system": "http://snomed.info/sct", "code": "35489007", "display": "Depression"},
    ]

    # Status reason for not taking
    NOT_TAKEN_REASONS: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "266711001", "display": "Not tolerated"},
        {"system": "http://snomed.info/sct", "code": "182856006", "display": "Patient refused"},
        {"system": "http://snomed.info/sct", "code": "410536001", "display": "Contraindicated"},
        {"system": "http://snomed.info/sct", "code": "105480006", "display": "Side effects"},
        {"system": "http://snomed.info/sct", "code": "266710000", "display": "Forgot to take"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        statement_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        medication_request_ref: str | None = None,
        medication_code: CodingTemplate | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MedicationStatement resource.

        Args:
            statement_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            medication_request_ref: Reference to the MedicationRequest
            medication_code: Specific medication coding (random if None)
            status: Statement status (random if None)

        Returns:
            MedicationStatement FHIR resource
        """
        if statement_id is None:
            statement_id = self._generate_id()

        # Select medication
        if medication_code is None:
            medication_code = self.faker.random_element(MEDICATIONS_RXNORM)

        # Generate status (weighted towards active)
        if status is None:
            status_weights = [
                ("active", 0.50),
                ("completed", 0.30),
                ("stopped", 0.10),
                ("not-taken", 0.05),
                ("on-hold", 0.05),
            ]
            roll = self.faker.random.random()
            cumulative = 0.0
            status = "active"
            for s, weight in status_weights:
                cumulative += weight
                if roll < cumulative:
                    status = s
                    break

        # Generate effective period
        start_date = self.faker.date_time_between(
            start_date="-2y",
            end_date="-30d",
            tzinfo=timezone.utc,
        )

        statement: dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "id": statement_id,
            "meta": self._generate_meta(),
            "status": status,
            "medicationCodeableConcept": make_codeable_concept(medication_code),
            "effectivePeriod": {
                "start": start_date.isoformat(),
            },
            "dateAsserted": self._generate_datetime(),
            "informationSource": {
                "type": "Patient" if self.faker.boolean(chance_of_getting_true=70) else "Practitioner",
            },
            "dosage": [
                {
                    "text": self.faker.random_element(
                        [
                            "Take 1 tablet daily",
                            "Take 1 tablet twice daily",
                            "Take as needed",
                            "Apply twice daily",
                            "1 tablet in the morning",
                        ]
                    ),
                    "timing": {
                        "repeat": {
                            "frequency": self.faker.random_element([1, 2, 3]),
                            "period": 1,
                            "periodUnit": "d",
                        }
                    },
                }
            ],
        }

        # Add end date for completed/stopped
        if status in ["completed", "stopped"]:
            end_date = self.faker.date_time_between(
                start_date=start_date,
                end_date="now",
                tzinfo=timezone.utc,
            )
            statement["effectivePeriod"]["end"] = end_date.isoformat()

        # Add reason for taking
        if self.faker.boolean(chance_of_getting_true=60):
            statement["reasonCode"] = [make_codeable_concept(self.faker.random_element(self.REASON_CODES))]

        # Add status reason for not-taken
        if status == "not-taken":
            statement["statusReason"] = [make_codeable_concept(self.faker.random_element(self.NOT_TAKEN_REASONS))]

        if patient_ref:
            statement["subject"] = {"reference": patient_ref}
            # Default information source to patient
            statement["informationSource"] = {"reference": patient_ref}

        if encounter_ref:
            statement["context"] = {"reference": encounter_ref}

        if medication_request_ref:
            statement["basedOn"] = [{"reference": medication_request_ref}]

        return statement
