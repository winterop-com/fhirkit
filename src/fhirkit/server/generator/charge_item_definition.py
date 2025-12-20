"""ChargeItemDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ChargeItemDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ChargeItemDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        url: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        code: dict[str, Any] | None = None,
        applicability: list[dict[str, Any]] | None = None,
        property_group: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ChargeItemDefinition resource.

        Args:
            definition_id: Resource ID (generates UUID if None)
            url: Canonical identifier
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            code: Billing code
            applicability: Conditions for applicability
            property_group: Property groups

        Returns:
            ChargeItemDefinition FHIR resource
        """
        if definition_id is None:
            definition_id = self._generate_id()

        if url is None:
            url = f"http://example.org/fhir/ChargeItemDefinition/{definition_id}"

        if title is None:
            title = f"{self.faker.word().title()} Charge Definition"

        charge_item_definition: dict[str, Any] = {
            "resourceType": "ChargeItemDefinition",
            "id": definition_id,
            "meta": self._generate_meta(),
            "url": url,
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        # Add description
        if description:
            charge_item_definition["description"] = description
        else:
            charge_item_definition["description"] = f"Charge item definition for {self.faker.word()} services"

        # Add code
        if code:
            charge_item_definition["code"] = code
        else:
            charge_item_definition["code"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/chargeitem-billingcodes",
                        "code": f"code-{self.faker.random_number(digits=4, fix_len=True)}",
                        "display": f"{self.faker.word().title()} Service",
                    }
                ]
            }

        # Add applicability
        if applicability:
            charge_item_definition["applicability"] = applicability

        # Add property group
        if property_group:
            charge_item_definition["propertyGroup"] = property_group
        else:
            charge_item_definition["propertyGroup"] = [
                {
                    "priceComponent": [
                        {
                            "type": "base",
                            "amount": {
                                "value": float(self.faker.random_int(50, 500)),
                                "currency": "USD",
                            },
                        }
                    ]
                }
            ]

        return charge_item_definition
