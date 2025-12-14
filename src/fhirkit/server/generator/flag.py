"""Flag resource generator."""

from datetime import timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class FlagGenerator(FHIRResourceGenerator):
    """Generator for FHIR Flag resources.

    Flag is used to convey alerts and warnings to healthcare providers.
    Common uses include fall risk, allergy alerts, infection control,
    and advance directives (DNR).
    """

    # Flag categories
    FLAG_CATEGORIES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/flag-category", "code": "clinical", "display": "Clinical"},
        {"system": "http://terminology.hl7.org/CodeSystem/flag-category", "code": "safety", "display": "Safety"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/flag-category",
            "code": "behavioral",
            "display": "Behavioral",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/flag-category", "code": "admin", "display": "Administrative"},
    ]

    # Common flag codes with their categories
    FLAG_TEMPLATES: list[dict[str, Any]] = [
        {
            "code": {"system": "http://snomed.info/sct", "code": "129839007", "display": "At risk for falls"},
            "category": "safety",
            "description": "Patient at risk for falls",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "390790000", "display": "Drug allergy"},
            "category": "clinical",
            "description": "Patient has known drug allergies",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "40733004", "display": "Infectious disease"},
            "category": "safety",
            "description": "Patient requires infection control precautions",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "304253006", "display": "Do not resuscitate"},
            "category": "clinical",
            "description": "Patient has DNR order",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "89138009", "display": "Cardiomyopathy"},
            "category": "clinical",
            "description": "Patient has history of cardiomyopathy",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "86302004", "display": "Violent behavior"},
            "category": "behavioral",
            "description": "Patient has history of violent behavior",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225469004", "display": "High suicide risk"},
            "category": "safety",
            "description": "Patient at high risk for suicide",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "414285001", "display": "Food allergy"},
            "category": "clinical",
            "description": "Patient has food allergies",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "161648003", "display": "Diabetic patient"},
            "category": "clinical",
            "description": "Patient is diabetic - monitor glucose",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "13644009", "display": "Hypoglycemia risk"},
            "category": "safety",
            "description": "Patient at risk for hypoglycemia",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        flag_id: str | None = None,
        patient_ref: str | None = None,
        author_ref: str | None = None,
        encounter_ref: str | None = None,
        status: str | None = None,
        template: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Flag resource.

        Args:
            flag_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            author_ref: Practitioner who created the flag
            encounter_ref: Encounter reference
            status: Flag status (active, inactive, entered-in-error)
            template: Specific flag template to use

        Returns:
            Flag FHIR resource
        """
        if flag_id is None:
            flag_id = self._generate_id()

        # Select template
        if template is None:
            template = self.faker.random_element(self.FLAG_TEMPLATES)

        # Determine status (weighted towards active)
        if status is None:
            status = self.faker.random_element(
                elements=["active", "inactive", "active", "active"]  # 75% active
            )

        # Find category for this flag
        category_code = template.get("category", "clinical")
        category = next((c for c in self.FLAG_CATEGORIES if c["code"] == category_code), self.FLAG_CATEGORIES[0])

        # Generate period
        start_date = self.faker.date_time_between(
            start_date="-1y",
            end_date="-7d",
            tzinfo=timezone.utc,
        )

        flag: dict[str, Any] = {
            "resourceType": "Flag",
            "id": flag_id,
            "meta": self._generate_meta(),
            "status": status,
            "category": [make_codeable_concept(category)],
            "code": make_codeable_concept(template["code"]),
            "period": {
                "start": start_date.isoformat(),
            },
        }

        # Add end date for inactive flags
        if status == "inactive":
            end_date = start_date + timedelta(days=self.faker.random_int(30, 180))
            flag["period"]["end"] = end_date.isoformat()

        if patient_ref:
            flag["subject"] = {"reference": patient_ref}

        if author_ref:
            flag["author"] = {"reference": author_ref}

        if encounter_ref:
            flag["encounter"] = {"reference": encounter_ref}

        return flag
