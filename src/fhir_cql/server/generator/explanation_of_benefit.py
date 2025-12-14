"""ExplanationOfBenefit resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ExplanationOfBenefitGenerator(FHIRResourceGenerator):
    """Generator for FHIR ExplanationOfBenefit resources."""

    # Claim types
    CLAIM_TYPES = [
        {"code": "institutional", "display": "Institutional", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "professional", "display": "Professional", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "pharmacy", "display": "Pharmacy", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
    ]

    # Outcome codes
    OUTCOME_CODES = ["queued", "complete", "error", "partial"]

    # Adjudication categories
    ADJUDICATION_CATEGORIES = [
        {"code": "submitted", "display": "Submitted Amount", "system": "http://terminology.hl7.org/CodeSystem/adjudication"},
        {"code": "copay", "display": "CoPay", "system": "http://terminology.hl7.org/CodeSystem/adjudication"},
        {"code": "eligible", "display": "Eligible Amount", "system": "http://terminology.hl7.org/CodeSystem/adjudication"},
        {"code": "deductible", "display": "Deductible", "system": "http://terminology.hl7.org/CodeSystem/adjudication"},
        {"code": "benefit", "display": "Benefit Amount", "system": "http://terminology.hl7.org/CodeSystem/adjudication"},
    ]

    # CPT codes
    CPT_CODES = [
        {"code": "99213", "display": "Office visit, established patient", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "99214", "display": "Office visit, moderate complexity", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "99385", "display": "Preventive visit", "system": "http://www.ama-assn.org/go/cpt"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        eob_id: str | None = None,
        patient_ref: str | None = None,
        provider_ref: str | None = None,
        insurer_ref: str | None = None,
        coverage_ref: str | None = None,
        claim_ref: str | None = None,
        status: str = "active",
        outcome: str = "complete",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ExplanationOfBenefit resource.

        Args:
            eob_id: EOB ID (generates UUID if None)
            patient_ref: Reference to Patient
            provider_ref: Reference to Practitioner or Organization
            insurer_ref: Reference to Organization (insurer)
            coverage_ref: Reference to Coverage
            claim_ref: Reference to Claim
            status: EOB status
            outcome: Processing outcome

        Returns:
            ExplanationOfBenefit FHIR resource
        """
        if eob_id is None:
            eob_id = self._generate_id()

        claim_type = self.faker.random_element(self.CLAIM_TYPES)
        procedure = self.faker.random_element(self.CPT_CODES)

        # Generate financial amounts
        submitted = round(self.faker.random.uniform(100, 1000), 2)
        eligible = round(submitted * 0.9, 2)
        copay = round(self.faker.random.uniform(20, 50), 2)
        deductible = round(self.faker.random.uniform(0, 100), 2)
        benefit = round(eligible - copay - deductible, 2)
        if benefit < 0:
            benefit = 0

        eob: dict[str, Any] = {
            "resourceType": "ExplanationOfBenefit",
            "id": eob_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/eob-ids",
                    value=f"EOB-{self.faker.numerify('############')}",
                ),
            ],
            "status": status,
            "type": {"coding": [claim_type], "text": claim_type["display"]},
            "use": "claim",
            "created": self._generate_datetime(),
            "outcome": outcome,
            "disposition": "Claim processed successfully" if outcome == "complete" else "Claim processing",
            "insurance": [
                {
                    "focal": True,
                    "coverage": {"reference": coverage_ref} if coverage_ref else {"display": "Primary Coverage"},
                }
            ],
            "item": [
                {
                    "sequence": 1,
                    "productOrService": {"coding": [procedure], "text": procedure["display"]},
                    "servicedDate": self._generate_date(),
                    "adjudication": [
                        {
                            "category": {"coding": [self.ADJUDICATION_CATEGORIES[0]]},
                            "amount": {"value": submitted, "currency": "USD"},
                        },
                        {
                            "category": {"coding": [self.ADJUDICATION_CATEGORIES[2]]},
                            "amount": {"value": eligible, "currency": "USD"},
                        },
                        {
                            "category": {"coding": [self.ADJUDICATION_CATEGORIES[1]]},
                            "amount": {"value": copay, "currency": "USD"},
                        },
                        {
                            "category": {"coding": [self.ADJUDICATION_CATEGORIES[4]]},
                            "amount": {"value": benefit, "currency": "USD"},
                        },
                    ],
                }
            ],
            "total": [
                {
                    "category": {"coding": [self.ADJUDICATION_CATEGORIES[0]]},
                    "amount": {"value": submitted, "currency": "USD"},
                },
                {
                    "category": {"coding": [self.ADJUDICATION_CATEGORIES[4]]},
                    "amount": {"value": benefit, "currency": "USD"},
                },
            ],
            "payment": {
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/ex-paymenttype",
                        "code": "complete" if outcome == "complete" else "partial",
                    }],
                },
                "date": self._generate_date(),
                "amount": {"value": benefit, "currency": "USD"},
            },
        }

        if patient_ref:
            eob["patient"] = {"reference": patient_ref}

        if provider_ref:
            eob["provider"] = {"reference": provider_ref}

        if insurer_ref:
            eob["insurer"] = {"reference": insurer_ref}

        if claim_ref:
            eob["claim"] = {"reference": claim_ref}

        return eob
