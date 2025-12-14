"""Procedure resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import PROCEDURES_SNOMED, CodingTemplate, make_codeable_concept


class ProcedureGenerator(FHIRResourceGenerator):
    """Generator for FHIR Procedure resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        procedure_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        encounter_ref: str | None = None,
        procedure_code: CodingTemplate | None = None,
        performed_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Procedure resource.

        Args:
            procedure_id: Procedure ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            practitioner_ref: Practitioner reference
            encounter_ref: Encounter reference
            procedure_code: Specific procedure coding (random if None)
            performed_date: Performed datetime (random if None)

        Returns:
            Procedure FHIR resource
        """
        if procedure_id is None:
            procedure_id = self._generate_id()

        # Select procedure code
        if procedure_code is None:
            procedure_code = self.faker.random_element(PROCEDURES_SNOMED)

        # Generate performed date
        if performed_date is None:
            performed_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            performed_date = performed_dt.isoformat()

        # Select status (mostly completed)
        status = self.faker.random_element(
            ["completed"] * 9 + ["in-progress"]  # 90% completed
        )

        # Select category
        categories = [
            {"system": "http://snomed.info/sct", "code": "387713003", "display": "Surgical procedure"},
            {"system": "http://snomed.info/sct", "code": "103693007", "display": "Diagnostic procedure"},
            {"system": "http://snomed.info/sct", "code": "410606002", "display": "Social service procedure"},
        ]
        category = self.faker.random_element(categories)

        procedure: dict[str, Any] = {
            "resourceType": "Procedure",
            "id": procedure_id,
            "meta": self._generate_meta(),
            "status": status,
            "category": make_codeable_concept(category),
            "code": make_codeable_concept(procedure_code),
            "performedDateTime": performed_date,
        }

        if patient_ref:
            procedure["subject"] = {"reference": patient_ref}

        if encounter_ref:
            procedure["encounter"] = {"reference": encounter_ref}

        if practitioner_ref:
            procedure["performer"] = [
                {
                    "actor": {"reference": practitioner_ref},
                }
            ]

        # Add reason reference or code sometimes
        if self.faker.random.random() < 0.3:
            reason_codes = [
                {"system": "http://snomed.info/sct", "code": "404684003", "display": "Clinical finding"},
                {"system": "http://snomed.info/sct", "code": "64572001", "display": "Disease"},
            ]
            procedure["reasonCode"] = [make_codeable_concept(self.faker.random_element(reason_codes))]

        return procedure
