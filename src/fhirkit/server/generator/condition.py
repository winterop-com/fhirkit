"""Condition resource generator."""

from datetime import date, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    CONDITION_CLINICAL_STATUS,
    CONDITION_VERIFICATION_STATUS,
    CONDITIONS_SNOMED,
    CodingTemplate,
    make_codeable_concept,
)


class ConditionGenerator(FHIRResourceGenerator):
    """Generator for FHIR Condition resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        condition_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        condition_code: CodingTemplate | None = None,
        onset_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Condition resource.

        Args:
            condition_id: Condition ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            condition_code: Specific condition coding (random if None)
            onset_date: Onset date (random if None)

        Returns:
            Condition FHIR resource
        """
        if condition_id is None:
            condition_id = self._generate_id()

        # Select condition code
        if condition_code is None:
            condition_code = self.faker.random_element(CONDITIONS_SNOMED)

        # Generate onset date (within past 10 years)
        if onset_date is None:
            today = date.today()
            onset_date = self._generate_date(
                start_date=today - timedelta(days=365 * 10),
                end_date=today,
            )

        # Select clinical status (weighted towards active)
        status_weights = [
            ("active", 0.6),
            ("resolved", 0.2),
            ("inactive", 0.1),
            ("remission", 0.1),
        ]
        roll = self.faker.random.random()
        cumulative = 0.0
        clinical_status_code = "active"
        for code, weight in status_weights:
            cumulative += weight
            if roll < cumulative:
                clinical_status_code = code
                break

        clinical_status = next(
            (s for s in CONDITION_CLINICAL_STATUS if s.get("code") == clinical_status_code),
            CONDITION_CLINICAL_STATUS[0],
        )

        # Select verification status (weighted towards confirmed)
        verification_status = self.faker.random_element(
            [CONDITION_VERIFICATION_STATUS[3]] * 8  # confirmed (80%)
            + [CONDITION_VERIFICATION_STATUS[1]] * 2  # provisional (20%)
        )

        # Select category
        category = self.faker.random_element(
            [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "problem-list-item",
                    "display": "Problem List Item",
                },
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "encounter-diagnosis",
                    "display": "Encounter Diagnosis",
                },
            ]
        )

        condition: dict[str, Any] = {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": self._generate_meta(),
            "clinicalStatus": make_codeable_concept(clinical_status),
            "verificationStatus": make_codeable_concept(verification_status),
            "category": [make_codeable_concept(category)],
            "code": make_codeable_concept(condition_code),
            "onsetDateTime": onset_date,
        }

        if patient_ref:
            condition["subject"] = {"reference": patient_ref}

        if encounter_ref:
            condition["encounter"] = {"reference": encounter_ref}

        # Add abatement date for resolved conditions
        if clinical_status_code in ("resolved", "inactive", "remission"):
            onset = date.fromisoformat(onset_date)
            min_abatement = onset + timedelta(days=30)
            today = date.today()
            # Only add abatement if enough time has passed
            if min_abatement <= today:
                abatement_date = self._generate_date(
                    start_date=min_abatement,
                    end_date=today,
                )
                condition["abatementDateTime"] = abatement_date
            else:
                # Condition resolved recently, use today's date
                condition["abatementDateTime"] = today.isoformat()

        # Add severity for some conditions
        if self.faker.random.random() < 0.3:
            severities = [
                {"system": "http://snomed.info/sct", "code": "24484000", "display": "Severe"},
                {"system": "http://snomed.info/sct", "code": "6736007", "display": "Moderate"},
                {"system": "http://snomed.info/sct", "code": "255604002", "display": "Mild"},
            ]
            condition["severity"] = make_codeable_concept(self.faker.random_element(severities))

        return condition
