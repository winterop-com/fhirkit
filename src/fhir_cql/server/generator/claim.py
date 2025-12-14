"""Claim resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ClaimGenerator(FHIRResourceGenerator):
    """Generator for FHIR Claim resources."""

    # Claim types
    CLAIM_TYPES = [
        {"code": "institutional", "display": "Institutional", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "oral", "display": "Oral", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "pharmacy", "display": "Pharmacy", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "professional", "display": "Professional", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
        {"code": "vision", "display": "Vision", "system": "http://terminology.hl7.org/CodeSystem/claim-type"},
    ]

    # Claim use codes
    USE_CODES = ["claim", "preauthorization", "predetermination"]

    # Priority codes
    PRIORITY_CODES = [
        {"code": "stat", "display": "Immediate", "system": "http://terminology.hl7.org/CodeSystem/processpriority"},
        {"code": "normal", "display": "Normal", "system": "http://terminology.hl7.org/CodeSystem/processpriority"},
        {"code": "deferred", "display": "Deferred", "system": "http://terminology.hl7.org/CodeSystem/processpriority"},
    ]

    # CPT procedure codes
    CPT_CODES = [
        {"code": "99213", "display": "Office visit, established patient", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "99214", "display": "Office visit, established patient, moderate", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "99203", "display": "Office visit, new patient", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "99385", "display": "Preventive visit, 18-39 years", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "90471", "display": "Immunization administration", "system": "http://www.ama-assn.org/go/cpt"},
        {"code": "36415", "display": "Venipuncture", "system": "http://www.ama-assn.org/go/cpt"},
    ]

    # ICD-10 diagnosis codes
    ICD10_CODES = [
        {"code": "Z00.00", "display": "General adult medical examination", "system": "http://hl7.org/fhir/sid/icd-10-cm"},
        {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications", "system": "http://hl7.org/fhir/sid/icd-10-cm"},
        {"code": "I10", "display": "Essential hypertension", "system": "http://hl7.org/fhir/sid/icd-10-cm"},
        {"code": "J06.9", "display": "Acute upper respiratory infection", "system": "http://hl7.org/fhir/sid/icd-10-cm"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        claim_id: str | None = None,
        patient_ref: str | None = None,
        provider_ref: str | None = None,
        insurer_ref: str | None = None,
        coverage_ref: str | None = None,
        status: str = "active",
        use: str = "claim",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Claim resource.

        Args:
            claim_id: Claim ID (generates UUID if None)
            patient_ref: Reference to Patient
            provider_ref: Reference to Practitioner or Organization
            insurer_ref: Reference to Organization (insurer)
            coverage_ref: Reference to Coverage
            status: Claim status
            use: Claim use (claim, preauthorization, predetermination)

        Returns:
            Claim FHIR resource
        """
        if claim_id is None:
            claim_id = self._generate_id()

        claim_type = self.faker.random_element(self.CLAIM_TYPES)
        priority = self.faker.random_element(self.PRIORITY_CODES)
        diagnosis = self.faker.random_element(self.ICD10_CODES)
        procedure = self.faker.random_element(self.CPT_CODES)

        # Generate amounts
        unit_price = round(self.faker.random.uniform(50, 500), 2)
        quantity = self.faker.random_int(min=1, max=3)
        total = round(unit_price * quantity, 2)

        claim: dict[str, Any] = {
            "resourceType": "Claim",
            "id": claim_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/claim-ids",
                    value=f"CLM-{self.faker.numerify('############')}",
                ),
            ],
            "status": status,
            "type": {"coding": [claim_type], "text": claim_type["display"]},
            "use": use,
            "created": self._generate_datetime(),
            "priority": {"coding": [priority]},
            "diagnosis": [
                {
                    "sequence": 1,
                    "diagnosisCodeableConcept": {
                        "coding": [diagnosis],
                        "text": diagnosis["display"],
                    },
                }
            ],
            "insurance": [
                {
                    "sequence": 1,
                    "focal": True,
                    "coverage": {"reference": coverage_ref} if coverage_ref else {"display": "Primary Coverage"},
                }
            ],
            "item": [
                {
                    "sequence": 1,
                    "productOrService": {"coding": [procedure], "text": procedure["display"]},
                    "servicedDate": self._generate_date(),
                    "quantity": {"value": quantity},
                    "unitPrice": {"value": unit_price, "currency": "USD"},
                    "net": {"value": total, "currency": "USD"},
                }
            ],
            "total": {"value": total, "currency": "USD"},
        }

        if patient_ref:
            claim["patient"] = {"reference": patient_ref}

        if provider_ref:
            claim["provider"] = {"reference": provider_ref}

        if insurer_ref:
            claim["insurer"] = {"reference": insurer_ref}

        return claim
