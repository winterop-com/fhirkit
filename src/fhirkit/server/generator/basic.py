"""Basic resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class BasicGenerator(FHIRResourceGenerator):
    """Generator for FHIR Basic resources."""

    BASIC_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/basic-resource-type",
            "code": "referral",
            "display": "Referral",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/basic-resource-type",
            "code": "diet",
            "display": "Diet",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/basic-resource-type",
            "code": "drugpresc",
            "display": "Drug Prescription",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/basic-resource-type",
            "code": "adminact",
            "display": "Administrative Activity",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/basic-resource-type",
            "code": "study",
            "display": "Study",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        basic_id: str | None = None,
        code: dict[str, Any] | None = None,
        subject_reference: str | None = None,
        created: str | None = None,
        author_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Basic resource."""
        if basic_id is None:
            basic_id = self._generate_id()

        if code is None:
            code = self.faker.random_element(self.BASIC_CODES)

        if created is None:
            created = datetime.now().strftime("%Y-%m-%d")

        basic: dict[str, Any] = {
            "resourceType": "Basic",
            "id": basic_id,
            "code": {"coding": [code], "text": code["display"]},
            "created": created,
        }

        if subject_reference:
            basic["subject"] = {"reference": subject_reference}

        if author_reference:
            basic["author"] = {"reference": author_reference}

        return basic
