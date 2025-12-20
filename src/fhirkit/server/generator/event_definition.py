"""EventDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EventDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR EventDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Example trigger types
    TRIGGER_TYPES = [
        "named-event",
        "periodic",
        "data-changed",
        "data-added",
        "data-modified",
        "data-removed",
        "data-accessed",
        "data-access-ended",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        event_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        purpose: str | None = None,
        trigger: list[dict[str, Any]] | None = None,
        subject_references: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EventDefinition resource.

        Args:
            event_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            purpose: Why this event definition exists
            trigger: Triggering conditions
            subject_references: References to subjects

        Returns:
            EventDefinition FHIR resource
        """
        if event_id is None:
            event_id = self._generate_id()

        if name is None:
            name = f"EventDefinition{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Event"

        event_definition: dict[str, Any] = {
            "resourceType": "EventDefinition",
            "id": event_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/EventDefinition/{event_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            event_definition["description"] = description
        else:
            event_definition["description"] = f"Event definition for {title.lower()}"

        if purpose:
            event_definition["purpose"] = purpose

        # Add trigger
        if trigger:
            event_definition["trigger"] = trigger
        else:
            event_definition["trigger"] = self._generate_triggers()

        # Add subject
        if subject_references:
            event_definition["subject"] = [{"reference": ref} for ref in subject_references]

        return event_definition

    def _generate_triggers(self) -> list[dict[str, Any]]:
        """Generate trigger definitions."""
        trigger_type = self.faker.random_element(self.TRIGGER_TYPES)

        trigger: dict[str, Any] = {
            "type": trigger_type,
            "name": f"{self.faker.word()}-{trigger_type}",
        }

        if trigger_type in ["data-changed", "data-added", "data-modified", "data-removed"]:
            trigger["data"] = [
                {
                    "type": self.faker.random_element(["Observation", "Condition", "Procedure"]),
                }
            ]

        if trigger_type == "periodic":
            trigger["timingTiming"] = {
                "repeat": {
                    "frequency": 1,
                    "period": 1,
                    "periodUnit": self.faker.random_element(["d", "wk", "mo"]),
                }
            }

        return [trigger]

    def generate_data_change_event(
        self,
        resource_type: str,
        trigger_type: str = "data-changed",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EventDefinition for data changes.

        Args:
            resource_type: Resource type to monitor
            trigger_type: Type of data trigger

        Returns:
            EventDefinition FHIR resource
        """
        trigger = [
            {
                "type": trigger_type,
                "name": f"{resource_type.lower()}-{trigger_type}",
                "data": [{"type": resource_type}],
            }
        ]

        return self.generate(
            name=f"{resource_type}ChangeEvent",
            title=f"{resource_type} Change Event",
            description=f"Triggers when a {resource_type} resource is {trigger_type.replace('data-', '')}",
            trigger=trigger,
            **kwargs,
        )
