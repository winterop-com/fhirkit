"""Linkage resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class LinkageGenerator(FHIRResourceGenerator):
    """Generator for FHIR Linkage resources."""

    LINKAGE_TYPES = ["source", "alternate", "historical"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        linkage_id: str | None = None,
        active: bool = True,
        author_reference: str | None = None,
        items: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Linkage resource.

        Args:
            linkage_id: Resource ID (generates UUID if None)
            active: Whether linkage is active
            author_reference: Reference to author (Practitioner/Organization)
            items: Linkage item definitions

        Returns:
            Linkage FHIR resource
        """
        if linkage_id is None:
            linkage_id = self._generate_id()

        linkage: dict[str, Any] = {
            "resourceType": "Linkage",
            "id": linkage_id,
            "meta": self._generate_meta(),
            "active": active,
        }

        # Add author
        if author_reference:
            linkage["author"] = {"reference": author_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            linkage["author"] = {
                "reference": f"Practitioner/{self._generate_id()}",
                "display": f"Dr. {self.faker.last_name()}",
            }

        # Add items
        if items:
            linkage["item"] = items
        else:
            linkage["item"] = self._generate_default_items()

        return linkage

    def _generate_default_items(self) -> list[dict[str, Any]]:
        """Generate default linkage items."""
        source_patient_id = self._generate_id()
        alternate_patient_id = self._generate_id()

        return [
            {
                "type": "source",
                "resource": {"reference": f"Patient/{source_patient_id}"},
            },
            {
                "type": "alternate",
                "resource": {"reference": f"Patient/{alternate_patient_id}"},
            },
        ]

    def generate_patient_linkage(
        self,
        source_patient_id: str,
        alternate_patient_ids: list[str],
        author_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Linkage between Patient resources.

        Args:
            source_patient_id: Source patient ID
            alternate_patient_ids: Alternate patient IDs
            author_reference: Reference to author

        Returns:
            Linkage FHIR resource
        """
        items = [
            {
                "type": "source",
                "resource": {"reference": f"Patient/{source_patient_id}"},
            }
        ]

        for alt_id in alternate_patient_ids:
            items.append(
                {
                    "type": "alternate",
                    "resource": {"reference": f"Patient/{alt_id}"},
                }
            )

        return self.generate(
            author_reference=author_reference,
            items=items,
            **kwargs,
        )
