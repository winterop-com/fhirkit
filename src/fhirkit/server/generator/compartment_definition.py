"""CompartmentDefinition resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CompartmentDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR CompartmentDefinition resources."""

    COMPARTMENT_CODES = ["Patient", "Encounter", "RelatedPerson", "Practitioner", "Device"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        url: str | None = None,
        name: str | None = None,
        status: str = "active",
        code: str | None = None,
        search: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CompartmentDefinition resource."""
        if definition_id is None:
            definition_id = self._generate_id()

        if code is None:
            code = self.faker.random_element(self.COMPARTMENT_CODES)

        if name is None:
            name = f"{code}Compartment"

        if url is None:
            url = f"http://example.org/fhir/CompartmentDefinition/{definition_id}"

        definition: dict[str, Any] = {
            "resourceType": "CompartmentDefinition",
            "id": definition_id,
            "url": url,
            "name": name,
            "status": status,
            "code": code,
            "search": search,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "description": f"Compartment definition for {code}",
        }

        return definition
