"""ClaimResponse resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ClaimResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR ClaimResponse resources."""

    OUTCOME_CODES = ["queued", "complete", "error", "partial"]

    USE_CODES = ["claim", "preauthorization", "predetermination"]

    ADJUDICATION_CATEGORIES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "submitted",
            "display": "Submitted Amount",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "copay",
            "display": "CoPay",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "eligible",
            "display": "Eligible Amount",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "deductible",
            "display": "Deductible",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "benefit",
            "display": "Benefit Amount",
        },
    ]

    CLAIM_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
            "code": "institutional",
            "display": "Institutional",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
            "code": "oral",
            "display": "Oral",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
            "code": "pharmacy",
            "display": "Pharmacy",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
            "code": "professional",
            "display": "Professional",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
            "code": "vision",
            "display": "Vision",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        status: str = "active",
        claim_type: dict[str, Any] | None = None,
        use: str | None = None,
        patient_reference: str | None = None,
        claim_reference: str | None = None,
        insurer_reference: str | None = None,
        outcome: str | None = None,
        created: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ClaimResponse resource.

        Args:
            response_id: Resource ID (generates UUID if None)
            status: Response status
            claim_type: Type of claim
            use: Claim use (claim, preauthorization, predetermination)
            patient_reference: Reference to Patient
            claim_reference: Reference to original Claim
            insurer_reference: Reference to insurer Organization
            outcome: Adjudication outcome
            created: Creation date

        Returns:
            ClaimResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        if claim_type is None:
            claim_type = self.faker.random_element(self.CLAIM_TYPES)

        if use is None:
            use = self.faker.random_element(self.USE_CODES)

        if outcome is None:
            outcome = self.faker.random_element(self.OUTCOME_CODES)

        if created is None:
            created = datetime.now().isoformat()

        response: dict[str, Any] = {
            "resourceType": "ClaimResponse",
            "id": response_id,
            "status": status,
            "type": {
                "coding": [claim_type],
                "text": claim_type["display"],
            },
            "use": use,
            "created": created,
            "outcome": outcome,
        }

        # Add patient reference
        if patient_reference:
            response["patient"] = {"reference": patient_reference}
        else:
            response["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add claim reference
        if claim_reference:
            response["request"] = {"reference": claim_reference}

        # Add insurer reference
        if insurer_reference:
            response["insurer"] = {"reference": insurer_reference}
        else:
            response["insurer"] = {"reference": f"Organization/{self._generate_id()}"}

        # Add payment info for complete outcomes
        if outcome == "complete":
            response["payment"] = {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/ex-paymenttype",
                            "code": "complete",
                            "display": "Complete",
                        }
                    ]
                },
                "date": created[:10] if "T" in created else created,
                "amount": {
                    "value": float(self.faker.random_int(100, 5000)),
                    "currency": "USD",
                },
            }

        # Add total amounts
        response["total"] = [
            {
                "category": {
                    "coding": [self.ADJUDICATION_CATEGORIES[0]],
                },
                "amount": {
                    "value": float(self.faker.random_int(500, 10000)),
                    "currency": "USD",
                },
            },
            {
                "category": {
                    "coding": [self.ADJUDICATION_CATEGORIES[4]],
                },
                "amount": {
                    "value": float(self.faker.random_int(100, 5000)),
                    "currency": "USD",
                },
            },
        ]

        return response

    def generate_for_claim(
        self,
        claim_id: str,
        patient_id: str,
        outcome: str = "complete",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ClaimResponse for a specific claim.

        Args:
            claim_id: Claim ID
            patient_id: Patient ID
            outcome: Adjudication outcome

        Returns:
            ClaimResponse FHIR resource
        """
        return self.generate(
            claim_reference=f"Claim/{claim_id}",
            patient_reference=f"Patient/{patient_id}",
            outcome=outcome,
            **kwargs,
        )
