"""MessageDefinition resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class MessageDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR MessageDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    CATEGORY_CODES = ["consequence", "currency", "notification"]

    EVENT_CODES = [
        {
            "system": "http://example.org/fhir/message-events",
            "code": "admin-notify",
            "display": "Admin Notification",
        },
        {
            "system": "http://example.org/fhir/message-events",
            "code": "diagnosticreport-provide",
            "display": "Provide Diagnostic Report",
        },
        {
            "system": "http://example.org/fhir/message-events",
            "code": "patient-link",
            "display": "Patient Link",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        url: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        event_coding: dict[str, Any] | None = None,
        category: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MessageDefinition resource."""
        if definition_id is None:
            definition_id = self._generate_id()

        if name is None:
            name = f"MessageDef{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Message"

        if url is None:
            url = f"http://example.org/fhir/MessageDefinition/{definition_id}"

        if event_coding is None:
            event_coding = self.faker.random_element(self.EVENT_CODES)

        if category is None:
            category = self.faker.random_element(self.CATEGORY_CODES)

        definition: dict[str, Any] = {
            "resourceType": "MessageDefinition",
            "id": definition_id,
            "url": url,
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "eventCoding": event_coding,
            "category": category,
        }

        return definition
