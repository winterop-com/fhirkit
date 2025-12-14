"""CarePlan resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    CAREPLAN_ACTIVITIES,
    CAREPLAN_CATEGORIES,
    SNOMED_SYSTEM,
)


class CarePlanGenerator(FHIRResourceGenerator):
    """Generator for FHIR CarePlan resources.

    CarePlan represents a care coordination document that describes the intention
    of how one or more practitioners intend to deliver care for a patient.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        careplan_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        condition_refs: list[str] | None = None,
        status: str | None = None,
        intent: str | None = None,
        period_start: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CarePlan resource.

        Args:
            careplan_id: CarePlan ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            author_ref: Author (Practitioner) reference
            condition_refs: List of Condition references this plan addresses
            status: Status code (draft, active, on-hold, etc.)
            intent: Intent code (proposal, plan, order, option)
            period_start: Start date of the care plan period

        Returns:
            CarePlan FHIR resource
        """
        if careplan_id is None:
            careplan_id = self._generate_id()

        # Status with weighted distribution
        if status is None:
            status = self.faker.random_element(
                elements=["active"] * 60 + ["completed"] * 25 + ["draft"] * 10 + ["on-hold"] * 5
            )

        # Intent
        if intent is None:
            intent = self.faker.random_element(elements=["plan"] * 60 + ["order"] * 30 + ["proposal"] * 10)

        # Generate period
        if period_start is None:
            start_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            period_start = start_dt.isoformat()

        # Category
        category = self.faker.random_element(CAREPLAN_CATEGORIES)

        # Title
        title = self._generate_careplan_title()

        careplan: dict[str, Any] = {
            "resourceType": "CarePlan",
            "id": careplan_id,
            "meta": self._generate_meta(),
            "status": status,
            "intent": intent,
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/us/core/CodeSystem/careplan-category",
                            "code": category["code"],
                            "display": category["display"],
                        }
                    ],
                    "text": category["display"],
                }
            ],
            "title": title,
            "description": self._generate_careplan_description(),
            "period": {"start": period_start},
            "created": self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            ).isoformat(),
        }

        if patient_ref:
            careplan["subject"] = {"reference": patient_ref}

        if encounter_ref:
            careplan["encounter"] = {"reference": encounter_ref}

        if author_ref:
            careplan["author"] = {"reference": author_ref}

        if condition_refs:
            careplan["addresses"] = [{"reference": ref} for ref in condition_refs]

        # Add activities (2-5 activities per care plan)
        num_activities = self.faker.random_int(min=2, max=5)
        careplan["activity"] = self._generate_activities(num_activities)

        return careplan

    def _generate_careplan_title(self) -> str:
        """Generate a realistic care plan title."""
        titles = [
            "Diabetes Management Plan",
            "Hypertension Care Plan",
            "Chronic Disease Management",
            "Post-Operative Care Plan",
            "Weight Management Program",
            "Cardiac Rehabilitation Plan",
            "Mental Health Treatment Plan",
            "Pain Management Plan",
            "Respiratory Care Plan",
            "Preventive Care Plan",
        ]
        return self.faker.random_element(titles)

    def _generate_careplan_description(self) -> str:
        """Generate a care plan description."""
        descriptions = [
            "Comprehensive care plan addressing patient's chronic condition management.",
            "Multidisciplinary approach to optimize patient health outcomes.",
            "Patient-centered care plan developed in collaboration with care team.",
            "Evidence-based treatment plan with measurable goals and interventions.",
            "Individualized care plan based on patient assessment and preferences.",
        ]
        return self.faker.random_element(descriptions)

    def _generate_activities(self, count: int) -> list[dict[str, Any]]:
        """Generate care plan activities."""
        activities = []
        selected = self.faker.random_elements(
            elements=CAREPLAN_ACTIVITIES,
            length=min(count, len(CAREPLAN_ACTIVITIES)),
            unique=True,
        )

        for activity_code in selected:
            activity: dict[str, Any] = {
                "detail": {
                    "status": self.faker.random_element(["not-started", "scheduled", "in-progress", "completed"]),
                    "code": {
                        "coding": [
                            {
                                "system": SNOMED_SYSTEM,
                                "code": activity_code["code"],
                                "display": activity_code["display"],
                            }
                        ],
                        "text": activity_code["display"],
                    },
                    "description": f"Patient to engage in {activity_code['display'].lower()}.",
                }
            }
            activities.append(activity)

        return activities
