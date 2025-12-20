"""SubstancePolymer resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstancePolymerGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstancePolymer resources."""

    POLYMER_CLASSES = [
        {
            "system": "http://hl7.org/fhir/substance-polymer-class",
            "code": "natural",
            "display": "Natural polymer",
        },
        {
            "system": "http://hl7.org/fhir/substance-polymer-class",
            "code": "synthetic",
            "display": "Synthetic polymer",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        polymer_id: str | None = None,
        polymer_class: dict[str, Any] | None = None,
        geometry: dict[str, Any] | None = None,
        modification: list[str] | None = None,
        monomer_set: list[dict[str, Any]] | None = None,
        repeat: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstancePolymer resource.

        Args:
            polymer_id: Resource ID (generates UUID if None)
            polymer_class: Class of polymer
            geometry: Polymer geometry
            modification: Modifications to polymer
            monomer_set: Monomer set information
            repeat: Repeat unit information

        Returns:
            SubstancePolymer FHIR resource
        """
        if polymer_id is None:
            polymer_id = self._generate_id()

        substance_polymer: dict[str, Any] = {
            "resourceType": "SubstancePolymer",
            "id": polymer_id,
            "meta": self._generate_meta(),
        }

        # Add polymer class
        if polymer_class:
            substance_polymer["class"] = polymer_class
        else:
            p_class = self.faker.random_element(self.POLYMER_CLASSES)
            substance_polymer["class"] = {
                "coding": [p_class],
                "text": p_class["display"],
            }

        # Add modification
        if modification:
            substance_polymer["modification"] = modification

        # Add repeat units if provided
        if repeat:
            substance_polymer["repeat"] = repeat

        return substance_polymer
