"""CoverageEligibilityRequest resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CoverageEligibilityRequestGenerator(FHIRResourceGenerator):
    """Generator for FHIR CoverageEligibilityRequest resources."""

    PURPOSE_CODES = [
        "auth-requirements",
        "benefits",
        "discovery",
        "validation",
    ]

    SERVICE_CATEGORIES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "1",
            "display": "Medical Care",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "2",
            "display": "Surgical",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "3",
            "display": "Consultation",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "4",
            "display": "Diagnostic XRay",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "5",
            "display": "Diagnostic Lab",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "14",
            "display": "Renal Supplies",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "23",
            "display": "Diagnostic Dental",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "24",
            "display": "Periodontics",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-benefitcategory",
            "code": "30",
            "display": "Health Benefit Plan Coverage",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        request_id: str | None = None,
        status: str = "active",
        purpose: list[str] | None = None,
        patient_reference: str | None = None,
        created: str | None = None,
        insurer_reference: str | None = None,
        provider_reference: str | None = None,
        serviced_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CoverageEligibilityRequest resource.

        Args:
            request_id: Resource ID (generates UUID if None)
            status: Request status
            purpose: Purpose codes
            patient_reference: Reference to Patient
            created: Creation date
            insurer_reference: Reference to insurer Organization
            provider_reference: Reference to provider Practitioner/Organization
            serviced_date: Date of service

        Returns:
            CoverageEligibilityRequest FHIR resource
        """
        if request_id is None:
            request_id = self._generate_id()

        if purpose is None:
            purpose = [self.faker.random_element(self.PURPOSE_CODES)]

        if created is None:
            created = datetime.now().isoformat()

        if serviced_date is None:
            serviced_date = self.faker.date_between(start_date="today", end_date="+30d").isoformat()

        request: dict[str, Any] = {
            "resourceType": "CoverageEligibilityRequest",
            "id": request_id,
            "status": status,
            "purpose": purpose,
            "created": created,
            "servicedDate": serviced_date,
        }

        # Add patient reference
        if patient_reference:
            request["patient"] = {"reference": patient_reference}
        else:
            request["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add insurer reference
        if insurer_reference:
            request["insurer"] = {"reference": insurer_reference}
        else:
            request["insurer"] = {"reference": f"Organization/{self._generate_id()}"}

        # Add provider reference
        if provider_reference:
            request["provider"] = {"reference": provider_reference}

        # Add item with service category
        category = self.faker.random_element(self.SERVICE_CATEGORIES)
        request["item"] = [
            {
                "category": {
                    "coding": [category],
                    "text": category["display"],
                }
            }
        ]

        return request

    def generate_for_patient(
        self,
        patient_id: str,
        insurer_id: str | None = None,
        purpose: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CoverageEligibilityRequest for a specific patient.

        Args:
            patient_id: Patient ID
            insurer_id: Optional insurer organization ID
            purpose: Purpose codes

        Returns:
            CoverageEligibilityRequest FHIR resource
        """
        return self.generate(
            patient_reference=f"Patient/{patient_id}",
            insurer_reference=f"Organization/{insurer_id}" if insurer_id else None,
            purpose=purpose,
            **kwargs,
        )
