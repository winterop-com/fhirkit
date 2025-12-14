"""ServiceRequest resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    SERVICE_REQUEST_CATEGORIES,
    SERVICE_REQUEST_ORDER_CODES,
    SNOMED_SYSTEM,
)


class ServiceRequestGenerator(FHIRResourceGenerator):
    """Generator for FHIR ServiceRequest resources.

    ServiceRequest represents a request for a service such as a diagnostic test,
    procedure, referral, or other clinical intervention.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        request_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        requester_ref: str | None = None,
        performer_ref: str | None = None,
        status: str | None = None,
        intent: str | None = None,
        priority: str | None = None,
        order_category: str | None = None,
        authored_on: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ServiceRequest resource.

        Args:
            request_id: ServiceRequest ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            requester_ref: Who is ordering the service (Practitioner reference)
            performer_ref: Who should perform the service
            status: Status (draft, active, on-hold, etc.)
            intent: Intent (proposal, plan, order, etc.)
            priority: Priority (routine, urgent, asap, stat)
            order_category: Category of order (laboratory, imaging, etc.)
            authored_on: When the request was authored

        Returns:
            ServiceRequest FHIR resource
        """
        if request_id is None:
            request_id = self._generate_id()

        # Status with weighted distribution
        if status is None:
            status = self.faker.random_element(
                elements=["active"] * 50 + ["completed"] * 35 + ["draft"] * 10 + ["on-hold"] * 5
            )

        # Intent
        if intent is None:
            intent = self.faker.random_element(elements=["order"] * 70 + ["plan"] * 20 + ["proposal"] * 10)

        # Priority
        if priority is None:
            priority = self.faker.random_element(
                elements=["routine"] * 70 + ["urgent"] * 20 + ["asap"] * 8 + ["stat"] * 2
            )

        # Select order code based on category
        if order_category:
            matching_orders = [o for o in SERVICE_REQUEST_ORDER_CODES if o.get("category") == order_category]
            order_code = (
                self.faker.random_element(matching_orders)
                if matching_orders
                else self.faker.random_element(SERVICE_REQUEST_ORDER_CODES)
            )
        else:
            order_code = self.faker.random_element(SERVICE_REQUEST_ORDER_CODES)

        # Get category for the order
        category_code = order_code.get("category", "laboratory")
        category = next(
            (c for c in SERVICE_REQUEST_CATEGORIES if c["display"].lower() == category_code),
            SERVICE_REQUEST_CATEGORIES[0],
        )

        # Authored on
        if authored_on is None:
            authored_dt = self.faker.date_time_between(
                start_date="-6m",
                end_date="now",
                tzinfo=timezone.utc,
            )
            authored_on = authored_dt.isoformat()

        service_request: dict[str, Any] = {
            "resourceType": "ServiceRequest",
            "id": request_id,
            "meta": self._generate_meta(),
            "status": status,
            "intent": intent,
            "priority": priority,
            "category": [
                {
                    "coding": [
                        {
                            "system": SNOMED_SYSTEM,
                            "code": category["code"],
                            "display": category["display"],
                        }
                    ],
                    "text": category["display"],
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": SNOMED_SYSTEM,
                        "code": order_code["code"],
                        "display": order_code["display"],
                    }
                ],
                "text": order_code["display"],
            },
            "authoredOn": authored_on,
        }

        if patient_ref:
            service_request["subject"] = {"reference": patient_ref}

        if encounter_ref:
            service_request["encounter"] = {"reference": encounter_ref}

        if requester_ref:
            service_request["requester"] = {"reference": requester_ref}

        if performer_ref:
            service_request["performer"] = [{"reference": performer_ref}]

        # Add reason (50% chance)
        if self.faker.random.random() < 0.5:
            service_request["reasonCode"] = [{"text": self._generate_reason(order_code)}]

        # Add note (30% chance)
        if self.faker.random.random() < 0.3:
            service_request["note"] = [{"text": self._generate_note(order_code, priority)}]

        return service_request

    def _generate_reason(self, order_code: dict[str, str]) -> str:
        """Generate a reason for the service request."""
        order_name = order_code.get("display", "procedure")
        reasons = [
            f"Routine {order_name} for patient evaluation.",
            f"Follow-up {order_name} to monitor condition.",
            f"{order_name} indicated based on clinical findings.",
            f"Screening {order_name} per guidelines.",
            f"Diagnostic workup requiring {order_name}.",
        ]
        return self.faker.random_element(reasons)

    def _generate_note(self, order_code: dict[str, str], priority: str) -> str:
        """Generate a clinical note for the service request."""
        if priority == "stat":
            return "STAT order - expedite processing. Clinical urgency."
        elif priority == "asap":
            return "Please prioritize. Results needed urgently."
        elif priority == "urgent":
            return "Urgent request. Please process within 24 hours."
        else:
            return f"Routine {order_code.get('display', 'order')}. Standard processing."

    def generate_lab_order(
        self,
        patient_ref: str | None = None,
        requester_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a laboratory service request.

        Returns:
            ServiceRequest for a laboratory test
        """
        return self.generate(
            patient_ref=patient_ref,
            requester_ref=requester_ref,
            order_category="laboratory",
            intent="order",
        )

    def generate_imaging_order(
        self,
        patient_ref: str | None = None,
        requester_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate an imaging service request.

        Returns:
            ServiceRequest for an imaging study
        """
        return self.generate(
            patient_ref=patient_ref,
            requester_ref=requester_ref,
            order_category="imaging",
            intent="order",
        )

    def generate_referral(
        self,
        patient_ref: str | None = None,
        requester_ref: str | None = None,
        performer_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a referral service request.

        Returns:
            ServiceRequest for a referral
        """
        return self.generate(
            patient_ref=patient_ref,
            requester_ref=requester_ref,
            performer_ref=performer_ref,
            order_category="referral",
            intent="order",
        )
