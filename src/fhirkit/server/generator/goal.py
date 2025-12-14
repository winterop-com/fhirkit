"""Goal resource generator."""

from datetime import timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    GOAL_ACHIEVEMENT_STATUS,
    GOAL_DESCRIPTIONS,
    GOAL_PRIORITY,
    GOAL_TARGET_MEASURES,
    SNOMED_SYSTEM,
    CodingTemplate,
)


class GoalGenerator(FHIRResourceGenerator):
    """Generator for FHIR Goal resources.

    Goal represents a desired state of health for a patient, or an aim
    of the care provided, which can be achieved through activities.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        goal_id: str | None = None,
        patient_ref: str | None = None,
        expressed_by_ref: str | None = None,
        lifecycle_status: str | None = None,
        start_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Goal resource.

        Args:
            goal_id: Goal ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            expressed_by_ref: Reference to who set the goal (Patient/Practitioner)
            lifecycle_status: Lifecycle status (proposed, planned, accepted, active, etc.)
            start_date: When work towards the goal started

        Returns:
            Goal FHIR resource
        """
        if goal_id is None:
            goal_id = self._generate_id()

        # Lifecycle status with weighted distribution
        if lifecycle_status is None:
            lifecycle_status = self.faker.random_element(
                elements=["active"] * 50 + ["accepted"] * 20 + ["completed"] * 15 + ["on-hold"] * 10 + ["proposed"] * 5
            )

        # Generate start date
        if start_date is None:
            start_dt = self.faker.date_time_between(
                start_date="-6m",
                end_date="now",
                tzinfo=timezone.utc,
            )
            start_date = start_dt.date().isoformat()

        # Select goal description
        goal_desc = self.faker.random_element(GOAL_DESCRIPTIONS)

        # Achievement status (relevant for active/completed goals)
        achievement_status = None
        if lifecycle_status in ["active", "completed"]:
            if lifecycle_status == "completed":
                achievement_status = self.faker.random_element(["achieved", "sustaining", "not-achieved"])
            else:
                achievement_status = self.faker.random_element(["in-progress", "improving", "worsening", "no-change"])

        # Priority
        priority = self.faker.random_element(GOAL_PRIORITY)

        goal: dict[str, Any] = {
            "resourceType": "Goal",
            "id": goal_id,
            "meta": self._generate_meta(),
            "lifecycleStatus": lifecycle_status,
            "priority": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/goal-priority",
                        "code": priority["code"],
                        "display": priority["display"],
                    }
                ]
            },
            "description": {
                "coding": [
                    {
                        "system": SNOMED_SYSTEM,
                        "code": goal_desc["code"],
                        "display": goal_desc["display"],
                    }
                ],
                "text": goal_desc["display"],
            },
            "startDate": start_date,
        }

        if patient_ref:
            goal["subject"] = {"reference": patient_ref}

        if expressed_by_ref:
            goal["expressedBy"] = {"reference": expressed_by_ref}

        if achievement_status:
            status_obj = next(
                (s for s in GOAL_ACHIEVEMENT_STATUS if s["code"] == achievement_status), GOAL_ACHIEVEMENT_STATUS[0]
            )
            goal["achievementStatus"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/goal-achievement",
                        "code": status_obj["code"],
                        "display": status_obj["display"],
                    }
                ]
            }

        # Add target (60% chance)
        if self.faker.random.random() < 0.6:
            goal["target"] = self._generate_target(start_date)

        # Add note (30% chance)
        if self.faker.random.random() < 0.3:
            goal["note"] = [{"text": self._generate_goal_note(goal_desc, lifecycle_status)}]

        return goal

    def _generate_target(self, start_date: str) -> list[dict[str, Any]]:
        """Generate goal target with measure and due date."""
        measure = self.faker.random_element(GOAL_TARGET_MEASURES)

        # Due date 1-6 months from start
        start_dt = self.faker.date_between(start_date="-6m", end_date="now")
        due_date = (start_dt + timedelta(days=self.faker.random_int(30, 180))).isoformat()

        # Target value within the target range
        target_value = self.faker.random.uniform(measure.get("target_low", 50), measure.get("target_high", 100))

        return [
            {
                "measure": {
                    "coding": [
                        {
                            "system": SNOMED_SYSTEM,
                            "code": measure["code"],
                            "display": measure["display"],
                        }
                    ],
                    "text": measure["display"],
                },
                "detailQuantity": {
                    "value": round(target_value, 1),
                    "unit": measure.get("unit", "unit"),
                    "system": "http://unitsofmeasure.org",
                    "code": measure.get("unit", "unit"),
                },
                "dueDate": due_date,
            }
        ]

    def _generate_goal_note(self, goal_desc: CodingTemplate, status: str) -> str:
        """Generate a clinical note for the goal."""
        goal_name = goal_desc.get("display", "goal")

        if status == "completed":
            templates = [
                f"Goal of {goal_name} successfully achieved. Continue maintenance.",
                f"Patient has met {goal_name} target. Review at next visit.",
            ]
        elif status == "active":
            templates = [
                f"Patient is actively working towards {goal_name}.",
                f"Ongoing progress on {goal_name}. Encourage continued effort.",
                f"Regular monitoring of {goal_name} in progress.",
            ]
        else:
            templates = [
                f"Goal for {goal_name} established with patient.",
                f"Patient agrees to work on {goal_name}.",
            ]

        return self.faker.random_element(templates)
