"""Substance resource generator."""

from datetime import datetime, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceGenerator(FHIRResourceGenerator):
    """Generator for FHIR Substance resources."""

    SUBSTANCE_CODES = [
        {
            "system": "http://snomed.info/sct",
            "code": "387517004",
            "display": "Paracetamol",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387458008",
            "display": "Aspirin",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387530003",
            "display": "Morphine",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387207008",
            "display": "Ibuprofen",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "372687004",
            "display": "Amoxicillin",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387173000",
            "display": "Metformin",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387362001",
            "display": "Atorvastatin",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "767559000",
            "display": "Saline solution",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "11713004",
            "display": "Water",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "256307007",
            "display": "Glucose",
        },
    ]

    SUBSTANCE_CATEGORIES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/substance-category",
            "code": "drug",
            "display": "Drug or Medicament",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/substance-category",
            "code": "food",
            "display": "Dietary Substance",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/substance-category",
            "code": "biological",
            "display": "Biological Substance",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/substance-category",
            "code": "chemical",
            "display": "Chemical",
        },
    ]

    STATUS_CODES = ["active", "inactive", "entered-in-error"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        substance_id: str | None = None,
        status: str | None = None,
        category: list[dict[str, Any]] | None = None,
        code: dict[str, Any] | None = None,
        description: str | None = None,
        instance_identifier: str | None = None,
        instance_expiry: str | None = None,
        instance_quantity: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Substance resource.

        Args:
            substance_id: Resource ID (generates UUID if None)
            status: Substance status
            category: Substance categories
            code: Substance code
            description: Description of the substance
            instance_identifier: Instance identifier
            instance_expiry: Expiry date
            instance_quantity: Quantity

        Returns:
            Substance FHIR resource
        """
        if substance_id is None:
            substance_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:1])

        if code is None:
            code = self.faker.random_element(self.SUBSTANCE_CODES)

        substance: dict[str, Any] = {
            "resourceType": "Substance",
            "id": substance_id,
            "status": status,
            "code": {
                "coding": [code],
                "text": code["display"],
            },
        }

        # Add category
        if category:
            substance["category"] = category
        else:
            cat = self.faker.random_element(self.SUBSTANCE_CATEGORIES)
            substance["category"] = [{"coding": [cat], "text": cat["display"]}]

        # Add description
        if description:
            substance["description"] = description
        else:
            substance["description"] = f"{code['display']} substance"

        # Add instance information
        if self.faker.boolean(chance_of_getting_true=60):
            instance: dict[str, Any] = {}

            if instance_identifier:
                instance["identifier"] = {
                    "system": "http://example.org/substance-lots",
                    "value": instance_identifier,
                }
            else:
                instance["identifier"] = {
                    "system": "http://example.org/substance-lots",
                    "value": f"LOT-{self.faker.random_number(digits=8, fix_len=True)}",
                }

            if instance_expiry:
                instance["expiry"] = instance_expiry
            else:
                expiry_date = datetime.now() + timedelta(days=self.faker.random_int(30, 730))
                instance["expiry"] = expiry_date.strftime("%Y-%m-%d")

            if instance_quantity:
                instance["quantity"] = instance_quantity
            else:
                instance["quantity"] = {
                    "value": float(self.faker.random_int(1, 1000)),
                    "unit": self.faker.random_element(["mg", "g", "mL", "L"]),
                    "system": "http://unitsofmeasure.org",
                }

            substance["instance"] = [instance]

        return substance

    def generate_medication_substance(
        self,
        medication_code: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Substance for a medication.

        Args:
            medication_code: Medication code

        Returns:
            Substance FHIR resource
        """
        drug_category = {
            "system": "http://terminology.hl7.org/CodeSystem/substance-category",
            "code": "drug",
            "display": "Drug or Medicament",
        }

        return self.generate(
            category=[{"coding": [drug_category], "text": drug_category["display"]}],
            code=medication_code,
            **kwargs,
        )
