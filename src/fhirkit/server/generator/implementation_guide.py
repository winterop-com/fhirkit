"""ImplementationGuide resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ImplementationGuideGenerator(FHIRResourceGenerator):
    """Generator for FHIR ImplementationGuide resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        ig_id: str | None = None,
        url: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        version: str | None = None,
        package_id: str | None = None,
        fhir_version: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ImplementationGuide resource."""
        if ig_id is None:
            ig_id = self._generate_id()

        if name is None:
            name = f"IG{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Implementation Guide"

        if url is None:
            url = f"http://example.org/fhir/ImplementationGuide/{ig_id}"

        if version is None:
            version = f"{self.faker.random_int(1, 5)}.{self.faker.random_int(0, 9)}.0"

        if package_id is None:
            package_id = f"example.fhir.{name.lower()}"

        if fhir_version is None:
            fhir_version = ["4.0.1"]

        ig: dict[str, Any] = {
            "resourceType": "ImplementationGuide",
            "id": ig_id,
            "url": url,
            "name": name,
            "title": title,
            "status": status,
            "version": version,
            "packageId": package_id,
            "fhirVersion": fhir_version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        return ig
