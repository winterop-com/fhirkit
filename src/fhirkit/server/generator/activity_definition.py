"""ActivityDefinition resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ActivityDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ActivityDefinition resources."""

    KIND_CODES = [
        "Appointment",
        "CommunicationRequest",
        "DeviceRequest",
        "MedicationRequest",
        "NutritionOrder",
        "Task",
        "ServiceRequest",
        "VisionPrescription",
    ]

    INTENT_CODES = ["proposal", "plan", "directive", "order", "original-order"]

    PRIORITY_CODES = ["routine", "urgent", "asap", "stat"]

    TOPIC_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/definition-topic",
            "code": "treatment",
            "display": "Treatment",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/definition-topic",
            "code": "education",
            "display": "Education",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/definition-topic",
            "code": "assessment",
            "display": "Assessment",
        },
    ]

    ACTIVITY_CODES = [
        {
            "system": "http://snomed.info/sct",
            "code": "304566005",
            "display": "Counseling for condition",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "410155007",
            "display": "Occupational therapy assessment",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "386053000",
            "display": "Evaluation procedure",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "225358003",
            "display": "Physical therapy",
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
        kind: str | None = None,
        intent: str | None = None,
        priority: str | None = None,
        code: dict[str, Any] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ActivityDefinition resource.

        Args:
            definition_id: Resource ID (generates UUID if None)
            url: Canonical URL
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            kind: Kind of resource to create
            intent: Proposal, plan, order, etc.
            priority: Routine, urgent, asap, stat
            code: Activity code
            description: Description of the activity

        Returns:
            ActivityDefinition FHIR resource
        """
        if definition_id is None:
            definition_id = self._generate_id()

        if name is None:
            name = f"Activity{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Activity Definition"

        if url is None:
            url = f"http://example.org/fhir/ActivityDefinition/{definition_id}"

        if kind is None:
            kind = self.faker.random_element(self.KIND_CODES)

        if intent is None:
            intent = self.faker.random_element(self.INTENT_CODES)

        if code is None:
            code = self.faker.random_element(self.ACTIVITY_CODES)

        definition: dict[str, Any] = {
            "resourceType": "ActivityDefinition",
            "id": definition_id,
            "url": url,
            "name": name,
            "title": title,
            "status": status,
            "kind": kind,
            "intent": intent,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "code": {
                "coding": [code],
                "text": code["display"],
            },
        }

        # Add priority
        if priority:
            definition["priority"] = priority
        elif self.faker.boolean(chance_of_getting_true=30):
            definition["priority"] = self.faker.random_element(self.PRIORITY_CODES)

        # Add description
        if description:
            definition["description"] = description
        else:
            definition["description"] = f"Activity definition for {code['display']}"

        # Add topic
        topic = self.faker.random_element(self.TOPIC_CODES)
        definition["topic"] = [
            {
                "coding": [topic],
                "text": topic["display"],
            }
        ]

        return definition

    def generate_for_medication(
        self,
        medication_code: dict[str, Any] | None = None,
        dosage_instruction: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ActivityDefinition for medication orders.

        Args:
            medication_code: Medication code
            dosage_instruction: Dosage instructions

        Returns:
            ActivityDefinition FHIR resource
        """
        definition = self.generate(kind="MedicationRequest", **kwargs)

        if medication_code:
            definition["productCodeableConcept"] = {
                "coding": [medication_code],
                "text": medication_code.get("display", ""),
            }

        if dosage_instruction:
            definition["dosage"] = [{"text": dosage_instruction}]

        return definition
