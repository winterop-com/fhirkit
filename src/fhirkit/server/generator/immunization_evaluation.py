"""ImmunizationEvaluation resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ImmunizationEvaluationGenerator(FHIRResourceGenerator):
    """Generator for FHIR ImmunizationEvaluation resources."""

    STATUS_CODES = ["completed", "entered-in-error"]

    DOSE_STATUS_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status",
            "code": "valid",
            "display": "Valid",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status",
            "code": "notvalid",
            "display": "Not Valid",
        },
    ]

    DOSE_STATUS_REASONS = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status-reason",
            "code": "advstorage",
            "display": "Adverse storage condition",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status-reason",
            "code": "coldchbrk",
            "display": "Cold chain break",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status-reason",
            "code": "explot",
            "display": "Expired lot",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status-reason",
            "code": "prodrecall",
            "display": "Product recall",
        },
    ]

    VACCINE_CODES = [
        {"system": "http://hl7.org/fhir/sid/cvx", "code": "03", "display": "MMR"},
        {"system": "http://hl7.org/fhir/sid/cvx", "code": "08", "display": "Hep B"},
        {"system": "http://hl7.org/fhir/sid/cvx", "code": "20", "display": "DTaP"},
        {"system": "http://hl7.org/fhir/sid/cvx", "code": "21", "display": "Varicella"},
        {"system": "http://hl7.org/fhir/sid/cvx", "code": "115", "display": "Tdap"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        evaluation_id: str | None = None,
        status: str = "completed",
        patient_reference: str | None = None,
        immunization_event_reference: str | None = None,
        target_disease: dict[str, Any] | None = None,
        dose_status: dict[str, Any] | None = None,
        dose_status_reason: list[dict[str, Any]] | None = None,
        series: str | None = None,
        dose_number: int | None = None,
        series_doses: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ImmunizationEvaluation resource.

        Args:
            evaluation_id: Resource ID (generates UUID if None)
            status: Evaluation status
            patient_reference: Reference to Patient
            immunization_event_reference: Reference to Immunization
            target_disease: Disease being evaluated against
            dose_status: Status of dose
            dose_status_reason: Reason for dose status
            series: Vaccine series
            dose_number: Dose number in series
            series_doses: Total doses in series

        Returns:
            ImmunizationEvaluation FHIR resource
        """
        if evaluation_id is None:
            evaluation_id = self._generate_id()

        vaccine = self.faker.random_element(self.VACCINE_CODES)

        evaluation: dict[str, Any] = {
            "resourceType": "ImmunizationEvaluation",
            "id": evaluation_id,
            "meta": self._generate_meta(),
            "status": status,
            "date": datetime.now(timezone.utc).isoformat(),
        }

        # Add identifier
        evaluation["identifier"] = [
            {
                "system": "http://example.org/immunization-evaluations",
                "value": f"EVAL-{self.faker.random_number(digits=8, fix_len=True)}",
            }
        ]

        # Add patient
        if patient_reference:
            evaluation["patient"] = {"reference": patient_reference}
        else:
            evaluation["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add immunization event
        if immunization_event_reference:
            evaluation["immunizationEvent"] = {"reference": immunization_event_reference}
        else:
            evaluation["immunizationEvent"] = {"reference": f"Immunization/{self._generate_id()}"}

        # Add target disease
        if target_disease:
            evaluation["targetDisease"] = target_disease
        else:
            evaluation["targetDisease"] = {
                "coding": [vaccine],
                "text": vaccine["display"],
            }

        # Add dose status
        if dose_status:
            evaluation["doseStatus"] = dose_status
        else:
            status_code = self.faker.random_element(self.DOSE_STATUS_CODES)
            evaluation["doseStatus"] = {
                "coding": [status_code],
                "text": status_code["display"],
            }

        # Add dose status reason if not valid
        dose_status = evaluation.get("doseStatus")
        if isinstance(dose_status, dict):
            coding_list = dose_status.get("coding")
            if isinstance(coding_list, list) and len(coding_list) > 0:
                first_coding = coding_list[0]
                if isinstance(first_coding, dict) and first_coding.get("code") == "notvalid":
                    if dose_status_reason:
                        evaluation["doseStatusReason"] = dose_status_reason
                    else:
                        reason = self.faker.random_element(self.DOSE_STATUS_REASONS)
                        evaluation["doseStatusReason"] = [{"coding": [reason], "text": reason["display"]}]

        # Add series info
        if series:
            evaluation["series"] = series
        else:
            evaluation["series"] = f"{vaccine['display']} Series"

        if dose_number:
            evaluation["doseNumberPositiveInt"] = dose_number
        else:
            evaluation["doseNumberPositiveInt"] = self.faker.random_int(1, 4)

        if series_doses:
            evaluation["seriesDosesPositiveInt"] = series_doses
        else:
            evaluation["seriesDosesPositiveInt"] = self.faker.random_int(evaluation["doseNumberPositiveInt"], 5)

        return evaluation

    def generate_for_patient(
        self,
        patient_id: str,
        immunization_id: str | None = None,
        is_valid: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ImmunizationEvaluation for a specific patient.

        Args:
            patient_id: Patient ID
            immunization_id: Immunization ID
            is_valid: Whether the dose is valid

        Returns:
            ImmunizationEvaluation FHIR resource
        """
        dose_status = self.DOSE_STATUS_CODES[0] if is_valid else self.DOSE_STATUS_CODES[1]

        return self.generate(
            patient_reference=f"Patient/{patient_id}",
            immunization_event_reference=f"Immunization/{immunization_id}" if immunization_id else None,
            dose_status={"coding": [dose_status], "text": dose_status["display"]},
            **kwargs,
        )
