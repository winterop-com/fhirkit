"""ExampleScenario resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ExampleScenarioGenerator(FHIRResourceGenerator):
    """Generator for FHIR ExampleScenario resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    ACTOR_TYPES = ["person", "entity"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        scenario_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        purpose: str | None = None,
        actor: list[dict[str, Any]] | None = None,
        instance: list[dict[str, Any]] | None = None,
        process: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ExampleScenario resource.

        Args:
            scenario_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            purpose: Scenario purpose
            actor: Actors in the scenario
            instance: Resource instances in the scenario
            process: Workflow processes

        Returns:
            ExampleScenario FHIR resource
        """
        if scenario_id is None:
            scenario_id = self._generate_id()

        if name is None:
            name = f"ExampleScenario{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Workflow Example"

        example_scenario: dict[str, Any] = {
            "resourceType": "ExampleScenario",
            "id": scenario_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/ExampleScenario/{scenario_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        # Add purpose
        if purpose:
            example_scenario["purpose"] = purpose
        else:
            example_scenario["purpose"] = f"Demonstrates the workflow for {self.faker.word()} scenario"

        # Add actors
        if actor:
            example_scenario["actor"] = actor
        else:
            example_scenario["actor"] = self._generate_actors()

        # Add instances
        if instance:
            example_scenario["instance"] = instance
        else:
            example_scenario["instance"] = self._generate_instances()

        # Add process
        if process:
            example_scenario["process"] = process
        else:
            example_scenario["process"] = self._generate_processes()

        return example_scenario

    def _generate_actors(self) -> list[dict[str, Any]]:
        """Generate scenario actors."""
        actors = [
            {
                "actorId": "patient",
                "type": "person",
                "name": "Patient",
                "description": "The patient receiving care",
            },
            {
                "actorId": "provider",
                "type": "person",
                "name": "Healthcare Provider",
                "description": "The clinician providing care",
            },
            {
                "actorId": "system",
                "type": "entity",
                "name": "EHR System",
                "description": "The electronic health record system",
            },
        ]

        return list(self.faker.random_elements(actors, length=self.faker.random_int(2, 3)))

    def _generate_instances(self) -> list[dict[str, Any]]:
        """Generate resource instances."""
        return [
            {
                "resourceId": "patient-1",
                "resourceType": "Patient",
                "name": "Example Patient",
                "description": "The patient in this scenario",
            },
            {
                "resourceId": "encounter-1",
                "resourceType": "Encounter",
                "name": "Example Encounter",
                "description": "The clinical encounter",
            },
        ]

    def _generate_processes(self) -> list[dict[str, Any]]:
        """Generate workflow processes."""
        return [
            {
                "title": "Main Process",
                "description": "The main workflow process",
                "step": [
                    {
                        "process": [
                            {
                                "title": "Step 1",
                                "description": "Initial step in the workflow",
                            }
                        ]
                    }
                ],
            }
        ]
