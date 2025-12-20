"""StructureMap resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class StructureMapGenerator(FHIRResourceGenerator):
    """Generator for FHIR StructureMap resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Group type modes
    GROUP_TYPE_MODES = ["none", "types", "type-and-types"]

    # Transform modes
    TRANSFORM_MODES = [
        "create",
        "copy",
        "truncate",
        "escape",
        "cast",
        "append",
        "translate",
        "reference",
        "dateOp",
        "uuid",
        "pointer",
        "evaluate",
        "cc",
        "c",
        "qty",
        "id",
        "cp",
    ]

    # Input modes
    INPUT_MODES = ["source", "target"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        map_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        structure: list[dict[str, Any]] | None = None,
        imports: list[str] | None = None,
        groups: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a StructureMap resource.

        Args:
            map_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            structure: Structure definitions used by this map
            imports: Other maps to import
            groups: Named transformation groups

        Returns:
            StructureMap FHIR resource
        """
        if map_id is None:
            map_id = self._generate_id()

        if name is None:
            name = f"StructureMap{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            source_type = self.faker.random_element(["Patient", "Observation", "Encounter", "Condition"])
            target_type = self.faker.random_element(["Bundle", "Patient", "Observation"])
            title = f"Transform {source_type} to {target_type}"

        structure_map: dict[str, Any] = {
            "resourceType": "StructureMap",
            "id": map_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/StructureMap/{map_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            structure_map["description"] = description
        else:
            structure_map["description"] = "Transforms data from one structure to another"

        # Add structure definitions
        if structure:
            structure_map["structure"] = structure
        else:
            structure_map["structure"] = self._generate_structures()

        # Add imports
        if imports:
            structure_map["import"] = imports

        # Add groups
        if groups:
            structure_map["group"] = groups
        else:
            structure_map["group"] = self._generate_groups()

        return structure_map

    def _generate_structures(self) -> list[dict[str, Any]]:
        """Generate structure definitions."""
        return [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/Patient",
                "mode": "source",
                "alias": "PatientSource",
            },
            {
                "url": "http://hl7.org/fhir/StructureDefinition/Patient",
                "mode": "target",
                "alias": "PatientTarget",
            },
        ]

    def _generate_groups(self) -> list[dict[str, Any]]:
        """Generate transformation groups."""
        return [
            {
                "name": "PatientTransform",
                "typeMode": "none",
                "input": [
                    {
                        "name": "source",
                        "type": "Patient",
                        "mode": "source",
                    },
                    {
                        "name": "target",
                        "type": "Patient",
                        "mode": "target",
                    },
                ],
                "rule": [
                    {
                        "name": "identifier",
                        "source": [
                            {
                                "context": "source",
                                "element": "identifier",
                                "variable": "id",
                            },
                        ],
                        "target": [
                            {
                                "context": "target",
                                "contextType": "variable",
                                "element": "identifier",
                                "transform": "copy",
                                "parameter": [{"valueId": "id"}],
                            },
                        ],
                    },
                    {
                        "name": "name",
                        "source": [
                            {
                                "context": "source",
                                "element": "name",
                                "variable": "srcName",
                            },
                        ],
                        "target": [
                            {
                                "context": "target",
                                "contextType": "variable",
                                "element": "name",
                                "transform": "copy",
                                "parameter": [{"valueId": "srcName"}],
                            },
                        ],
                    },
                    {
                        "name": "birthDate",
                        "source": [
                            {
                                "context": "source",
                                "element": "birthDate",
                                "variable": "bd",
                            },
                        ],
                        "target": [
                            {
                                "context": "target",
                                "contextType": "variable",
                                "element": "birthDate",
                                "transform": "copy",
                                "parameter": [{"valueId": "bd"}],
                            },
                        ],
                    },
                ],
            },
        ]

    def generate_simple_copy_map(
        self,
        source_type: str,
        target_type: str,
        fields: list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a simple copy transformation map.

        Args:
            source_type: Source resource type
            target_type: Target resource type
            fields: Fields to copy

        Returns:
            StructureMap FHIR resource
        """
        structures = [
            {
                "url": f"http://hl7.org/fhir/StructureDefinition/{source_type}",
                "mode": "source",
                "alias": f"{source_type}Source",
            },
            {
                "url": f"http://hl7.org/fhir/StructureDefinition/{target_type}",
                "mode": "target",
                "alias": f"{target_type}Target",
            },
        ]

        rules = []
        for field in fields:
            rules.append(
                {
                    "name": field,
                    "source": [
                        {
                            "context": "source",
                            "element": field,
                            "variable": f"v_{field}",
                        },
                    ],
                    "target": [
                        {
                            "context": "target",
                            "contextType": "variable",
                            "element": field,
                            "transform": "copy",
                            "parameter": [{"valueId": f"v_{field}"}],
                        },
                    ],
                }
            )

        groups = [
            {
                "name": f"{source_type}To{target_type}",
                "typeMode": "none",
                "input": [
                    {
                        "name": "source",
                        "type": source_type,
                        "mode": "source",
                    },
                    {
                        "name": "target",
                        "type": target_type,
                        "mode": "target",
                    },
                ],
                "rule": rules,
            },
        ]

        return self.generate(
            name=f"{source_type}To{target_type}Map",
            title=f"Transform {source_type} to {target_type}",
            description=f"Simple copy transformation from {source_type} to {target_type}",
            structure=structures,
            groups=groups,
            **kwargs,
        )
