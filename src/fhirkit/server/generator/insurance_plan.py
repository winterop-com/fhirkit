"""InsurancePlan resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class InsurancePlanGenerator(FHIRResourceGenerator):
    """Generator for FHIR InsurancePlan resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    PLAN_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
            "code": "medical",
            "display": "Medical",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
            "code": "dental",
            "display": "Dental",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
            "code": "vision",
            "display": "Vision",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
            "code": "pharmacy",
            "display": "Pharmacy",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
            "code": "mental",
            "display": "Mental Health",
        },
    ]

    COVERAGE_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "plan",
            "display": "Plan",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "subplan",
            "display": "SubPlan",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        plan_id: str | None = None,
        status: str = "active",
        plan_type: dict[str, Any] | None = None,
        name: str | None = None,
        alias: list[str] | None = None,
        owned_by_reference: str | None = None,
        administered_by_reference: str | None = None,
        coverage_area_references: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an InsurancePlan resource.

        Args:
            plan_id: Resource ID (generates UUID if None)
            status: Plan status
            plan_type: Type of insurance plan
            name: Official name of the plan
            alias: Alternative names
            owned_by_reference: Reference to owning organization
            administered_by_reference: Reference to administering organization
            coverage_area_references: References to coverage area locations

        Returns:
            InsurancePlan FHIR resource
        """
        if plan_id is None:
            plan_id = self._generate_id()

        if plan_type is None:
            plan_type = self.faker.random_element(self.PLAN_TYPES)

        if name is None:
            plan_name = self.faker.random_element(
                ["Premium", "Standard", "Basic", "Gold", "Silver", "Bronze", "Platinum"]
            )
            name = f"{self.faker.company()} {plan_name} {plan_type['display']} Plan"

        insurance_plan: dict[str, Any] = {
            "resourceType": "InsurancePlan",
            "id": plan_id,
            "meta": self._generate_meta(),
            "status": status,
            "type": [{"coding": [plan_type], "text": plan_type["display"]}],
            "name": name,
        }

        # Add identifier
        insurance_plan["identifier"] = [
            {
                "system": "http://example.org/insurance-plans",
                "value": f"PLAN-{self.faker.random_number(digits=6, fix_len=True)}",
            }
        ]

        # Add alias
        if alias:
            insurance_plan["alias"] = alias
        elif self.faker.boolean(chance_of_getting_true=50):
            insurance_plan["alias"] = [f"Plan {self.faker.random_number(digits=4, fix_len=True)}"]

        # Add period
        start_year = self.faker.random_int(2020, 2024)
        insurance_plan["period"] = {
            "start": f"{start_year}-01-01",
            "end": f"{start_year + 1}-12-31",
        }

        # Add owned by organization
        if owned_by_reference:
            insurance_plan["ownedBy"] = {"reference": owned_by_reference}
        else:
            insurance_plan["ownedBy"] = {
                "reference": f"Organization/{self._generate_id()}",
                "display": f"{self.faker.company()} Insurance",
            }

        # Add administered by organization
        if administered_by_reference:
            insurance_plan["administeredBy"] = {"reference": administered_by_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            insurance_plan["administeredBy"] = insurance_plan["ownedBy"]

        # Add coverage area
        if coverage_area_references:
            insurance_plan["coverageArea"] = [{"reference": ref} for ref in coverage_area_references]

        # Add contact
        insurance_plan["contact"] = [
            {
                "purpose": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/contactentity-type",
                            "code": "ADMIN",
                            "display": "Administrative",
                        }
                    ]
                },
                "telecom": [
                    {"system": "phone", "value": self.faker.phone_number()},
                    {"system": "email", "value": self.faker.email()},
                ],
            }
        ]

        return insurance_plan

    def generate_with_coverage(
        self,
        plan_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an InsurancePlan with detailed coverage.

        Args:
            plan_type: Type of insurance plan

        Returns:
            InsurancePlan FHIR resource
        """
        plan = self.generate(plan_type=plan_type, **kwargs)

        # Add coverage details
        plan["coverage"] = [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                            "code": "plan",
                            "display": "Plan",
                        }
                    ]
                },
                "benefit": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
                                    "code": "preventive",
                                    "display": "Preventive Care",
                                }
                            ]
                        },
                    },
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/benefit-type",
                                    "code": "emergency",
                                    "display": "Emergency Services",
                                }
                            ]
                        },
                    },
                ],
            }
        ]

        return plan
