"""PlanDefinition resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class PlanDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR PlanDefinition resources."""

    PLAN_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
            "code": "order-set",
            "display": "Order Set",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
            "code": "clinical-protocol",
            "display": "Clinical Protocol",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
            "code": "eca-rule",
            "display": "ECA Rule",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
            "code": "workflow-definition",
            "display": "Workflow Definition",
        },
    ]

    ACTION_TRIGGER_TYPES = [
        "named-event",
        "periodic",
        "data-changed",
        "data-added",
        "data-modified",
        "data-removed",
        "data-accessed",
        "data-access-ended",
    ]

    ACTION_RELATIONSHIP_TYPES = [
        "before-start",
        "before",
        "before-end",
        "concurrent-with-start",
        "concurrent",
        "concurrent-with-end",
        "after-start",
        "after",
        "after-end",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        plan_id: str | None = None,
        url: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        plan_type: dict[str, Any] | None = None,
        description: str | None = None,
        subject_type: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PlanDefinition resource.

        Args:
            plan_id: Resource ID (generates UUID if None)
            url: Canonical URL
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            plan_type: Type of plan
            description: Description
            subject_type: Type of subject

        Returns:
            PlanDefinition FHIR resource
        """
        if plan_id is None:
            plan_id = self._generate_id()

        if name is None:
            name = f"PlanDef{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Care Plan"

        if url is None:
            url = f"http://example.org/fhir/PlanDefinition/{plan_id}"

        if plan_type is None:
            plan_type = self.faker.random_element(self.PLAN_TYPES)

        if subject_type is None:
            subject_type = "Patient"

        plan: dict[str, Any] = {
            "resourceType": "PlanDefinition",
            "id": plan_id,
            "url": url,
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "type": {
                "coding": [plan_type],
                "text": plan_type["display"],
            },
            "subjectCodeableConcept": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/resource-types",
                        "code": subject_type,
                        "display": subject_type,
                    }
                ]
            },
        }

        # Add description
        if description:
            plan["description"] = description
        else:
            plan["description"] = f"A {plan_type['display']} for clinical care"

        # Add sample actions
        plan["action"] = self._generate_actions()

        return plan

    def _generate_actions(self, num_actions: int | None = None) -> list[dict[str, Any]]:
        """Generate sample actions for the plan."""
        if num_actions is None:
            num_actions = self.faker.random_int(1, 3)

        actions = []
        for i in range(num_actions):
            action: dict[str, Any] = {
                "title": f"Action {i + 1}: {self.faker.bs().title()}",
                "description": self.faker.sentence(),
            }

            # Add trigger
            if self.faker.boolean(chance_of_getting_true=50):
                action["trigger"] = [
                    {
                        "type": self.faker.random_element(self.ACTION_TRIGGER_TYPES),
                        "name": f"trigger-{i + 1}",
                    }
                ]

            # Add definition reference
            if self.faker.boolean(chance_of_getting_true=70):
                action["definitionCanonical"] = f"http://example.org/fhir/ActivityDefinition/activity-{i + 1}"

            actions.append(action)

        return actions

    def generate_order_set(
        self,
        title: str | None = None,
        activity_definitions: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an order set PlanDefinition.

        Args:
            title: Order set title
            activity_definitions: List of ActivityDefinition canonical URLs

        Returns:
            PlanDefinition FHIR resource
        """
        plan_type = {
            "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
            "code": "order-set",
            "display": "Order Set",
        }

        plan = self.generate(title=title, plan_type=plan_type, **kwargs)

        # Override actions with activity definitions
        if activity_definitions:
            plan["action"] = [
                {
                    "title": f"Order {i + 1}",
                    "definitionCanonical": url,
                }
                for i, url in enumerate(activity_definitions)
            ]

        return plan
