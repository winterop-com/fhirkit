"""SubstanceSourceMaterial resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceSourceMaterialGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstanceSourceMaterial resources."""

    SOURCE_TYPES = [
        {
            "system": "http://hl7.org/fhir/substance-source-material-type",
            "code": "Animal",
            "display": "Animal source",
        },
        {
            "system": "http://hl7.org/fhir/substance-source-material-type",
            "code": "Plant",
            "display": "Plant source",
        },
        {
            "system": "http://hl7.org/fhir/substance-source-material-type",
            "code": "Mineral",
            "display": "Mineral source",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        source_material_id: str | None = None,
        source_material_class: dict[str, Any] | None = None,
        source_material_type: dict[str, Any] | None = None,
        source_material_state: dict[str, Any] | None = None,
        organism_id: dict[str, Any] | None = None,
        organism_name: str | None = None,
        country_of_origin: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstanceSourceMaterial resource.

        Args:
            source_material_id: Resource ID (generates UUID if None)
            source_material_class: Class of source material
            source_material_type: Type of source material
            source_material_state: State of source material
            organism_id: Organism identifier
            organism_name: Organism name
            country_of_origin: Countries of origin

        Returns:
            SubstanceSourceMaterial FHIR resource
        """
        if source_material_id is None:
            source_material_id = self._generate_id()

        substance_source: dict[str, Any] = {
            "resourceType": "SubstanceSourceMaterial",
            "id": source_material_id,
            "meta": self._generate_meta(),
        }

        # Add source material class
        if source_material_class:
            substance_source["sourceMaterialClass"] = source_material_class
        else:
            s_type = self.faker.random_element(self.SOURCE_TYPES)
            substance_source["sourceMaterialClass"] = {
                "coding": [s_type],
                "text": s_type["display"],
            }

        # Add source material type
        if source_material_type:
            substance_source["sourceMaterialType"] = source_material_type

        # Add source material state
        if source_material_state:
            substance_source["sourceMaterialState"] = source_material_state

        # Add organism name
        if organism_name:
            substance_source["organismName"] = organism_name
        else:
            # Generate a scientific-sounding organism name
            substance_source["organismName"] = f"{self.faker.word().title()} {self.faker.word()}"

        # Add country of origin
        if country_of_origin:
            substance_source["countryOfOrigin"] = country_of_origin
        else:
            country = self.faker.country_code()
            substance_source["countryOfOrigin"] = [
                {
                    "coding": [
                        {
                            "system": "urn:iso:std:iso:3166",
                            "code": country,
                        }
                    ]
                }
            ]

        return substance_source
