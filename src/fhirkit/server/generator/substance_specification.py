"""SubstanceSpecification resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceSpecificationGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstanceSpecification resources."""

    DOMAIN_CODES = [
        {
            "system": "http://hl7.org/fhir/substance-domain",
            "code": "Human",
            "display": "Human use",
        },
        {
            "system": "http://hl7.org/fhir/substance-domain",
            "code": "Veterinary",
            "display": "Veterinary use",
        },
    ]

    STATUS_CODES = [
        {
            "system": "http://hl7.org/fhir/substance-status",
            "code": "active",
            "display": "Active",
        },
        {
            "system": "http://hl7.org/fhir/substance-status",
            "code": "inactive",
            "display": "Inactive",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        specification_id: str | None = None,
        identifier: dict[str, Any] | None = None,
        status: dict[str, Any] | None = None,
        domain: dict[str, Any] | None = None,
        description: str | None = None,
        comment: str | None = None,
        name: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstanceSpecification resource.

        Args:
            specification_id: Resource ID (generates UUID if None)
            identifier: Substance identifier
            status: Substance status
            domain: Domain of substance (human, veterinary)
            description: Substance description
            comment: General comment
            name: Substance names

        Returns:
            SubstanceSpecification FHIR resource
        """
        if specification_id is None:
            specification_id = self._generate_id()

        substance_spec: dict[str, Any] = {
            "resourceType": "SubstanceSpecification",
            "id": specification_id,
            "meta": self._generate_meta(),
        }

        # Add identifier
        if identifier:
            substance_spec["identifier"] = identifier
        else:
            substance_spec["identifier"] = {
                "system": "http://example.org/substances",
                "value": f"SUB-{self.faker.random_number(digits=6, fix_len=True)}",
            }

        # Add status
        if status:
            substance_spec["status"] = status
        else:
            s_status = self.faker.random_element(self.STATUS_CODES)
            substance_spec["status"] = {
                "coding": [s_status],
                "text": s_status["display"],
            }

        # Add domain
        if domain:
            substance_spec["domain"] = domain
        else:
            s_domain = self.faker.random_element(self.DOMAIN_CODES)
            substance_spec["domain"] = {
                "coding": [s_domain],
                "text": s_domain["display"],
            }

        # Add description
        if description:
            substance_spec["description"] = description
        else:
            substance_spec["description"] = f"Specification for {self.faker.word().title()} compound"

        # Add comment
        if comment:
            substance_spec["comment"] = comment

        # Add name
        if name:
            substance_spec["name"] = name
        else:
            substance_spec["name"] = [
                {
                    "name": self.faker.word().title(),
                    "preferred": True,
                }
            ]

        return substance_spec
