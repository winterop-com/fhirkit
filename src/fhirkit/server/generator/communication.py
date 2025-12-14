"""Communication resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class CommunicationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Communication resources.

    Communication represents messages exchanged between healthcare providers
    and patients, including notifications, reminders, alerts, and instructions.
    """

    # Communication categories
    CATEGORIES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/communication-category", "code": "alert", "display": "Alert"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/communication-category",
            "code": "notification",
            "display": "Notification",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/communication-category",
            "code": "reminder",
            "display": "Reminder",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/communication-category",
            "code": "instruction",
            "display": "Instruction",
        },
    ]

    # Priority levels
    PRIORITIES: list[str] = ["routine", "urgent", "asap", "stat"]

    # Topic codes
    TOPIC_CODES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "310389008", "display": "Appointment reminder"},
        {"system": "http://snomed.info/sct", "code": "371535009", "display": "Referral letter"},
        {"system": "http://snomed.info/sct", "code": "390790000", "display": "Medication reminder"},
        {"system": "http://snomed.info/sct", "code": "275329004", "display": "Lab results notification"},
        {"system": "http://snomed.info/sct", "code": "385763009", "display": "Care plan update"},
        {"system": "http://snomed.info/sct", "code": "77386006", "display": "Patient education"},
    ]

    # Message templates by category
    MESSAGE_TEMPLATES: dict[str, list[str]] = {
        "alert": [
            "Urgent: Critical lab result requires immediate attention.",
            "Alert: Patient condition has changed significantly.",
            "Warning: Potential drug interaction identified.",
            "Critical: Vital signs outside normal parameters.",
        ],
        "notification": [
            "Your recent lab results are now available in your patient portal.",
            "Your referral to the specialist has been processed.",
            "Your prescription has been sent to the pharmacy.",
            "Your insurance has approved the requested procedure.",
        ],
        "reminder": [
            "Reminder: You have an appointment scheduled for next week.",
            "Please remember to take your medication as prescribed.",
            "It's time for your annual wellness check-up.",
            "Reminder: Please complete your pre-visit questionnaire.",
        ],
        "instruction": [
            "Please follow up with your primary care provider within 2 weeks.",
            "Take the prescribed medication twice daily with food.",
            "Avoid strenuous activity for the next 48 hours.",
            "Please fast for 12 hours before your lab appointment.",
        ],
    }

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        communication_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        sender_ref: str | None = None,
        recipient_ref: str | None = None,
        status: str | None = None,
        category: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Communication resource.

        Args:
            communication_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (subject)
            encounter_ref: Related encounter reference
            sender_ref: Who sent the message (Practitioner, Organization, etc.)
            recipient_ref: Who received the message
            status: Communication status
            category: Communication category (alert, notification, reminder, instruction)

        Returns:
            Communication FHIR resource
        """
        if communication_id is None:
            communication_id = self._generate_id()

        # Generate status (weighted towards completed)
        if status is None:
            status_weights = [
                ("completed", 0.70),
                ("in-progress", 0.15),
                ("preparation", 0.05),
                ("on-hold", 0.05),
                ("not-done", 0.05),
            ]
            roll = self.faker.random.random()
            cumulative = 0.0
            status = "completed"
            for s, weight in status_weights:
                cumulative += weight
                if roll < cumulative:
                    status = s
                    break

        # Select category
        if category is None:
            category = self.faker.random_element(["alert", "notification", "reminder", "instruction"])

        category_coding = next(
            (c for c in self.CATEGORIES if c["code"] == category),
            self.CATEGORIES[1],  # Default to notification
        )

        # Generate message content
        messages = self.MESSAGE_TEMPLATES.get(category, self.MESSAGE_TEMPLATES["notification"])
        message_text = self.faker.random_element(messages)

        # Generate sent time
        sent_time = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Select topic
        topic = self.faker.random_element(self.TOPIC_CODES)

        # Select priority (weighted towards routine)
        priority = self.faker.random_element(elements=["routine", "routine", "routine", "urgent", "asap"])

        communication: dict[str, Any] = {
            "resourceType": "Communication",
            "id": communication_id,
            "meta": self._generate_meta(),
            "status": status,
            "category": [make_codeable_concept(category_coding)],
            "priority": priority,
            "topic": make_codeable_concept(topic),
            "sent": sent_time.isoformat(),
            "payload": [
                {
                    "contentString": message_text,
                }
            ],
        }

        # Add received time for completed communications
        if status == "completed":
            communication["received"] = sent_time.isoformat()

        if patient_ref:
            communication["subject"] = {"reference": patient_ref}
            # Default recipient to patient if not specified
            if not recipient_ref:
                communication["recipient"] = [{"reference": patient_ref}]

        if sender_ref:
            communication["sender"] = {"reference": sender_ref}

        if recipient_ref:
            communication["recipient"] = [{"reference": recipient_ref}]

        if encounter_ref:
            communication["encounter"] = {"reference": encounter_ref}

        return communication
