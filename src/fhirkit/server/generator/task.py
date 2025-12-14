"""Task resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class TaskGenerator(FHIRResourceGenerator):
    """Generator for FHIR Task resources."""

    # Task status codes
    STATUS_CODES = [
        "draft",
        "requested",
        "received",
        "accepted",
        "rejected",
        "ready",
        "cancelled",
        "in-progress",
        "on-hold",
        "failed",
        "completed",
        "entered-in-error",
    ]

    # Task intent codes
    INTENT_CODES = [
        "unknown",
        "proposal",
        "plan",
        "order",
        "original-order",
        "reflex-order",
        "filler-order",
        "instance-order",
        "option",
    ]

    # Task priority codes
    PRIORITY_CODES = ["routine", "urgent", "asap", "stat"]

    # Task codes
    TASK_CODES = [
        {"code": "approve", "display": "Approve", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "fulfill", "display": "Fulfill", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "abort", "display": "Abort", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "replace", "display": "Replace", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "change", "display": "Change", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "suspend", "display": "Suspend", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
        {"code": "resume", "display": "Resume", "system": "http://hl7.org/fhir/CodeSystem/task-code"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        task_id: str | None = None,
        patient_ref: str | None = None,
        requester_ref: str | None = None,
        owner_ref: str | None = None,
        status: str | None = None,
        intent: str = "order",
        priority: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Task resource.

        Args:
            task_id: Task ID (generates UUID if None)
            patient_ref: Reference to Patient (for field)
            requester_ref: Reference to requester (Practitioner, Organization, etc.)
            owner_ref: Reference to owner responsible for task
            status: Task status (random if None)
            intent: Task intent
            priority: Task priority (random if None)

        Returns:
            Task FHIR resource
        """
        if task_id is None:
            task_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(["draft", "requested", "in-progress", "completed"])

        if priority is None:
            priority = self.faker.random_element(self.PRIORITY_CODES)

        task_code = self.faker.random_element(self.TASK_CODES)

        task: dict[str, Any] = {
            "resourceType": "Task",
            "id": task_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/task-ids",
                    value=f"TASK-{self.faker.numerify('######')}",
                ),
            ],
            "status": status,
            "intent": intent,
            "priority": priority,
            "code": {
                "coding": [task_code],
                "text": task_code["display"],
            },
            "description": f"Task: {task_code['display']} - {self.faker.sentence(nb_words=6)}",
            "authoredOn": self._generate_datetime(),
        }

        # Add execution period for in-progress or completed tasks
        if status in ["in-progress", "completed", "failed"]:
            task["executionPeriod"] = self._generate_period()

        if patient_ref:
            task["for"] = {"reference": patient_ref}

        if requester_ref:
            task["requester"] = {"reference": requester_ref}

        if owner_ref:
            task["owner"] = {"reference": owner_ref}

        return task
