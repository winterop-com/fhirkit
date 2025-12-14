"""Coverage resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CoverageGenerator(FHIRResourceGenerator):
    """Generator for FHIR Coverage resources."""

    # Coverage types
    COVERAGE_TYPES = [
        {
            "code": "HIP",
            "display": "Health insurance plan policy",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "EHCPOL",
            "display": "Extended healthcare",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "HSAPOL",
            "display": "Health spending account",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {"code": "DENTPRG", "display": "Dental program", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
        {"code": "DRUGPOL", "display": "Drug policy", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
        {
            "code": "MCPOL",
            "display": "Managed care policy",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "MENTPOL",
            "display": "Mental health policy",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "VISPOL",
            "display": "Vision care policy",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
    ]

    # Subscriber relationships
    RELATIONSHIPS = [
        {"code": "self", "display": "Self", "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship"},
        {
            "code": "spouse",
            "display": "Spouse",
            "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
        },
        {
            "code": "child",
            "display": "Child",
            "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
        },
        {
            "code": "parent",
            "display": "Parent",
            "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
        },
        {
            "code": "other",
            "display": "Other",
            "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
        },
    ]

    # Insurance company names
    INSURERS = [
        "Blue Cross Blue Shield",
        "Aetna",
        "UnitedHealth",
        "Cigna",
        "Humana",
        "Kaiser Permanente",
        "Anthem",
        "Molina Healthcare",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        coverage_id: str | None = None,
        patient_ref: str | None = None,
        payor_ref: str | None = None,
        status: str = "active",
        coverage_type: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Coverage resource.

        Args:
            coverage_id: Coverage ID (generates UUID if None)
            patient_ref: Reference to Patient (beneficiary)
            payor_ref: Reference to Organization (payor)
            status: Coverage status (active, cancelled, draft, entered-in-error)
            coverage_type: Coverage type code (random if None)

        Returns:
            Coverage FHIR resource
        """
        if coverage_id is None:
            coverage_id = self._generate_id()

        # Select coverage type
        if coverage_type is None:
            type_coding = self.faker.random_element(self.COVERAGE_TYPES)
        else:
            type_coding = next(
                (t for t in self.COVERAGE_TYPES if t["code"] == coverage_type),
                self.COVERAGE_TYPES[0],
            )

        relationship = self.faker.random_element(self.RELATIONSHIPS)
        insurer_name = self.faker.random_element(self.INSURERS)

        coverage: dict[str, Any] = {
            "resourceType": "Coverage",
            "id": coverage_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/coverage-ids",
                    value=f"COV-{self.faker.numerify('############')}",
                ),
            ],
            "status": status,
            "type": {
                "coding": [type_coding],
                "text": type_coding["display"],
            },
            "subscriberId": self.faker.numerify("SUB-########"),
            "relationship": {
                "coding": [relationship],
                "text": relationship["display"],
            },
            "period": {
                "start": f"{self.faker.random_int(min=2020, max=2024)}-01-01",
                "end": f"{self.faker.random_int(min=2025, max=2027)}-12-31",
            },
            "class": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                "code": "group",
                            }
                        ],
                    },
                    "value": f"GRP-{self.faker.numerify('####')}",
                    "name": "Employer Group Plan",
                },
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                "code": "plan",
                            }
                        ],
                    },
                    "value": self.faker.random_element(["GOLD", "SILVER", "BRONZE", "PLATINUM"]),
                    "name": f"{type_coding['display']} Plan",
                },
            ],
            "network": self.faker.random_element(["PPO Network", "HMO Network", "EPO Network"]),
        }

        if patient_ref:
            coverage["beneficiary"] = {"reference": patient_ref}
            coverage["subscriber"] = {"reference": patient_ref}

        if payor_ref:
            coverage["payor"] = [{"reference": payor_ref, "display": insurer_name}]
        else:
            coverage["payor"] = [{"display": insurer_name}]

        return coverage
