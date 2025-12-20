"""CoverageEligibilityResponse resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CoverageEligibilityResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR CoverageEligibilityResponse resources."""

    PURPOSE_CODES = [
        "auth-requirements",
        "benefits",
        "discovery",
        "validation",
    ]

    OUTCOME_CODES = ["queued", "complete", "error", "partial"]

    BENEFIT_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
            "code": "benefit",
            "display": "Benefit",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
            "code": "deductible",
            "display": "Deductible",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
            "code": "copay",
            "display": "Copayment per service",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
            "code": "copay-percent",
            "display": "Copayment Percent per service",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
            "code": "copay-maximum",
            "display": "Copayment maximum per service",
        },
    ]

    NETWORK_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-network",
            "code": "in",
            "display": "In Network",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/benefit-network",
            "code": "out",
            "display": "Out of Network",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        status: str = "active",
        purpose: list[str] | None = None,
        patient_reference: str | None = None,
        created: str | None = None,
        request_reference: str | None = None,
        insurer_reference: str | None = None,
        outcome: str | None = None,
        serviced_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CoverageEligibilityResponse resource.

        Args:
            response_id: Resource ID (generates UUID if None)
            status: Response status
            purpose: Purpose codes
            patient_reference: Reference to Patient
            created: Creation date
            request_reference: Reference to CoverageEligibilityRequest
            insurer_reference: Reference to insurer Organization
            outcome: Response outcome
            serviced_date: Date of service

        Returns:
            CoverageEligibilityResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        if purpose is None:
            purpose = [self.faker.random_element(self.PURPOSE_CODES)]

        if outcome is None:
            outcome = self.faker.random_element(self.OUTCOME_CODES[:2])

        if created is None:
            created = datetime.now().isoformat()

        if serviced_date is None:
            serviced_date = self.faker.date_between(start_date="today", end_date="+30d").isoformat()

        response: dict[str, Any] = {
            "resourceType": "CoverageEligibilityResponse",
            "id": response_id,
            "status": status,
            "purpose": purpose,
            "created": created,
            "outcome": outcome,
            "servicedDate": serviced_date,
        }

        # Add patient reference
        if patient_reference:
            response["patient"] = {"reference": patient_reference}
        else:
            response["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add request reference
        if request_reference:
            response["request"] = {"reference": request_reference}
        else:
            response["request"] = {"reference": f"CoverageEligibilityRequest/{self._generate_id()}"}

        # Add insurer reference
        if insurer_reference:
            response["insurer"] = {"reference": insurer_reference}
        else:
            response["insurer"] = {"reference": f"Organization/{self._generate_id()}"}

        # Add insurance benefits info for complete outcomes
        if outcome == "complete":
            network = self.faker.random_element(self.NETWORK_TYPES)
            benefit_type = self.faker.random_element(self.BENEFIT_TYPES)

            response["insurance"] = [
                {
                    "coverage": {"reference": f"Coverage/{self._generate_id()}"},
                    "inforce": True,
                    "item": [
                        {
                            "network": {
                                "coding": [network],
                            },
                            "benefit": [
                                {
                                    "type": {
                                        "coding": [benefit_type],
                                    },
                                    "allowedMoney": {
                                        "value": float(self.faker.random_int(1000, 100000)),
                                        "currency": "USD",
                                    },
                                    "usedMoney": {
                                        "value": float(self.faker.random_int(0, 10000)),
                                        "currency": "USD",
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]

        return response

    def generate_for_request(
        self,
        request_id: str,
        patient_id: str,
        outcome: str = "complete",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CoverageEligibilityResponse for a specific request.

        Args:
            request_id: CoverageEligibilityRequest ID
            patient_id: Patient ID
            outcome: Response outcome

        Returns:
            CoverageEligibilityResponse FHIR resource
        """
        return self.generate(
            request_reference=f"CoverageEligibilityRequest/{request_id}",
            patient_reference=f"Patient/{patient_id}",
            outcome=outcome,
            **kwargs,
        )
