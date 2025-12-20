"""GraphDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class GraphDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR GraphDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Common starting resource types
    START_TYPES = ["Patient", "Encounter", "Condition", "Procedure", "Observation"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        graph_id: str | None = None,
        name: str | None = None,
        status: str = "active",
        description: str | None = None,
        start: str | None = None,
        profile: str | None = None,
        links: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a GraphDefinition resource.

        Args:
            graph_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            status: Publication status
            description: Natural language description
            start: Starting resource type
            profile: Profile on the start type
            links: Links from start type to other types

        Returns:
            GraphDefinition FHIR resource
        """
        if graph_id is None:
            graph_id = self._generate_id()

        if name is None:
            name = f"GraphDefinition{self.faker.random_number(digits=4, fix_len=True)}"

        if start is None:
            start = self.faker.random_element(self.START_TYPES)

        graph_definition: dict[str, Any] = {
            "resourceType": "GraphDefinition",
            "id": graph_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/GraphDefinition/{graph_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "start": start,
        }

        if description:
            graph_definition["description"] = description
        else:
            graph_definition["description"] = f"Graph definition starting from {start}"

        if profile:
            graph_definition["profile"] = profile

        # Add links
        if links:
            graph_definition["link"] = links
        else:
            graph_definition["link"] = self._generate_links(start)

        return graph_definition

    def _generate_links(self, start: str) -> list[dict[str, Any]]:
        """Generate links based on start type."""
        links = []

        if start == "Patient":
            links = [
                {
                    "path": "Patient.managingOrganization",
                    "min": 0,
                    "max": "1",
                    "target": [
                        {
                            "type": "Organization",
                            "params": "identifier={ref}",
                        }
                    ],
                },
                {
                    "path": "Patient.generalPractitioner",
                    "min": 0,
                    "max": "*",
                    "target": [
                        {
                            "type": "Practitioner",
                            "params": "identifier={ref}",
                        }
                    ],
                },
            ]
        elif start == "Encounter":
            links = [
                {
                    "path": "Encounter.subject",
                    "min": 1,
                    "max": "1",
                    "target": [
                        {
                            "type": "Patient",
                            "params": "_id={ref}",
                        }
                    ],
                },
                {
                    "path": "Encounter.participant.individual",
                    "min": 0,
                    "max": "*",
                    "target": [
                        {
                            "type": "Practitioner",
                            "params": "_id={ref}",
                        }
                    ],
                },
            ]
        elif start == "Condition":
            links = [
                {
                    "path": "Condition.subject",
                    "min": 1,
                    "max": "1",
                    "target": [
                        {
                            "type": "Patient",
                            "params": "_id={ref}",
                        }
                    ],
                },
                {
                    "path": "Condition.encounter",
                    "min": 0,
                    "max": "1",
                    "target": [
                        {
                            "type": "Encounter",
                            "params": "_id={ref}",
                        }
                    ],
                },
            ]
        else:
            # Generic links
            links = [
                {
                    "path": f"{start}.subject",
                    "min": 0,
                    "max": "1",
                    "target": [
                        {
                            "type": "Patient",
                            "params": "_id={ref}",
                        }
                    ],
                },
            ]

        return links

    def generate_patient_everything_graph(self, **kwargs: Any) -> dict[str, Any]:
        """Generate a GraphDefinition for Patient $everything operation.

        Returns:
            GraphDefinition FHIR resource
        """
        links = [
            {
                "path": "Patient.managingOrganization",
                "min": 0,
                "max": "1",
                "target": [{"type": "Organization"}],
            },
            {
                "path": "Patient.generalPractitioner",
                "min": 0,
                "max": "*",
                "target": [{"type": "Practitioner"}, {"type": "Organization"}],
            },
        ]

        return self.generate(
            name="PatientEverythingGraph",
            description="Graph for Patient $everything operation",
            start="Patient",
            links=links,
            **kwargs,
        )

    def generate_encounter_graph(self, **kwargs: Any) -> dict[str, Any]:
        """Generate a GraphDefinition for Encounter traversal.

        Returns:
            GraphDefinition FHIR resource
        """
        links = [
            {
                "path": "Encounter.subject",
                "min": 1,
                "max": "1",
                "target": [{"type": "Patient"}],
            },
            {
                "path": "Encounter.participant.individual",
                "min": 0,
                "max": "*",
                "target": [{"type": "Practitioner"}, {"type": "PractitionerRole"}],
            },
            {
                "path": "Encounter.serviceProvider",
                "min": 0,
                "max": "1",
                "target": [{"type": "Organization"}],
            },
            {
                "path": "Encounter.location.location",
                "min": 0,
                "max": "*",
                "target": [{"type": "Location"}],
            },
        ]

        return self.generate(
            name="EncounterGraph",
            description="Graph for Encounter with related resources",
            start="Encounter",
            links=links,
            **kwargs,
        )
