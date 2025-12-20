"""Contract resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ContractGenerator(FHIRResourceGenerator):
    """Generator for FHIR Contract resources."""

    STATUS_CODES = [
        "amended",
        "appended",
        "cancelled",
        "disputed",
        "entered-in-error",
        "executable",
        "executed",
        "negotiable",
        "offered",
        "policy",
        "rejected",
        "renewed",
        "revoked",
        "resolved",
        "terminated",
    ]

    CONTRACT_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/contract-type",
            "code": "privacy",
            "display": "Privacy",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/contract-type",
            "code": "disclosure",
            "display": "Disclosure",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/contract-type",
            "code": "healthinsurance",
            "display": "Health Insurance",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/contract-type",
            "code": "consent",
            "display": "Consent",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        contract_id: str | None = None,
        status: str | None = None,
        contract_type: dict[str, Any] | None = None,
        subject_reference: str | None = None,
        issued: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Contract resource."""
        if contract_id is None:
            contract_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(["executable", "executed", "offered"])

        if contract_type is None:
            contract_type = self.faker.random_element(self.CONTRACT_TYPES)

        if issued is None:
            issued = datetime.now().isoformat()

        contract: dict[str, Any] = {
            "resourceType": "Contract",
            "id": contract_id,
            "status": status,
            "issued": issued,
            "type": {
                "coding": [contract_type],
                "text": contract_type["display"],
            },
        }

        if subject_reference:
            contract["subject"] = [{"reference": subject_reference}]

        return contract
