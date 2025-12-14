"""ClinicalImpression resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import CONDITIONS_SNOMED, make_codeable_concept


class ClinicalImpressionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ClinicalImpression resources.

    ClinicalImpression represents a clinical assessment/diagnosis made by
    a practitioner based on their evaluation of a patient's condition.
    """

    # Investigation types
    INVESTIGATION_CODES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "271336007", "display": "Examination findings"},
        {"system": "http://snomed.info/sct", "code": "363787002", "display": "Test result"},
        {"system": "http://snomed.info/sct", "code": "309465005", "display": "Clinical history"},
        {"system": "http://snomed.info/sct", "code": "276339004", "display": "Assessment"},
    ]

    # Prognosis codes
    PROGNOSIS_CODES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "170968001", "display": "Prognosis good"},
        {"system": "http://snomed.info/sct", "code": "65872000", "display": "Prognosis fair"},
        {"system": "http://snomed.info/sct", "code": "67334001", "display": "Prognosis guarded"},
        {"system": "http://snomed.info/sct", "code": "159857006", "display": "Prognosis poor"},
        {"system": "http://snomed.info/sct", "code": "271593001", "display": "Prognosis uncertain"},
    ]

    # Summary templates
    SUMMARY_TEMPLATES: list[str] = [
        "Patient presents with {condition}. Assessment indicates {prognosis} prognosis with appropriate treatment.",
        "Clinical evaluation reveals {condition}. Recommend continued monitoring and follow-up.",
        "Based on examination findings, patient diagnosed with {condition}. Treatment plan initiated.",
        "Assessment completed for {condition}. Patient stable with current management.",
        "Comprehensive evaluation for {condition}. Further workup recommended.",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        impression_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        assessor_ref: str | None = None,
        condition_ref: str | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ClinicalImpression resource.

        Args:
            impression_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            assessor_ref: Practitioner who made the assessment
            condition_ref: Reference to related Condition
            status: Assessment status (in-progress, completed, entered-in-error)

        Returns:
            ClinicalImpression FHIR resource
        """
        if impression_id is None:
            impression_id = self._generate_id()

        # Generate status (weighted towards completed)
        if status is None:
            status = self.faker.random_element(elements=["completed", "completed", "completed", "in-progress"])

        # Select a condition for the finding
        condition = self.faker.random_element(CONDITIONS_SNOMED)
        prognosis = self.faker.random_element(self.PROGNOSIS_CODES)

        # Generate effective time
        effective_time = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Generate summary
        summary = self.faker.random_element(self.SUMMARY_TEMPLATES).format(
            condition=condition["display"].lower(),
            prognosis=prognosis["display"].lower().replace("prognosis ", ""),
        )

        impression: dict[str, Any] = {
            "resourceType": "ClinicalImpression",
            "id": impression_id,
            "meta": self._generate_meta(),
            "status": status,
            "effectiveDateTime": effective_time.isoformat(),
            "date": effective_time.isoformat(),
            "summary": summary,
            "finding": [
                {
                    "itemCodeableConcept": make_codeable_concept(condition),
                    "basis": "Clinical examination and patient history",
                }
            ],
            "prognosisCodeableConcept": [make_codeable_concept(prognosis)],
        }

        # Add investigation
        if self.faker.boolean(chance_of_getting_true=60):
            investigation_code = self.faker.random_element(self.INVESTIGATION_CODES)
            impression["investigation"] = [
                {
                    "code": make_codeable_concept(investigation_code),
                }
            ]

        if patient_ref:
            impression["subject"] = {"reference": patient_ref}

        if encounter_ref:
            impression["encounter"] = {"reference": encounter_ref}

        if assessor_ref:
            impression["assessor"] = {"reference": assessor_ref}

        if condition_ref:
            impression["problem"] = [{"reference": condition_ref}]
            impression["finding"][0]["itemReference"] = {"reference": condition_ref}

        return impression
