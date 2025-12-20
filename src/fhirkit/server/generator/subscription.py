"""Subscription resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubscriptionGenerator(FHIRResourceGenerator):
    """Generator for FHIR Subscription resources."""

    # Subscription status codes
    STATUS_CODES = ["requested", "active", "error", "off"]

    # Channel types
    CHANNEL_TYPES = ["rest-hook", "websocket", "email", "sms", "message"]

    # Payload MIME types
    PAYLOAD_TYPES = [
        "application/fhir+json",
        "application/fhir+xml",
        "application/json",
    ]

    # Common subscription criteria patterns
    CRITERIA_PATTERNS = [
        "Observation?code=http://loinc.org|85354-9",
        "Condition?clinical-status=active",
        "Encounter?status=in-progress",
        "MedicationRequest?status=active",
        "DiagnosticReport?status=final",
        "Patient?_lastUpdated=gt{date}",
        "Observation?category=vital-signs",
        "AllergyIntolerance?clinical-status=active",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        subscription_id: str | None = None,
        status: str = "active",
        criteria: str | None = None,
        channel_type: str = "rest-hook",
        endpoint: str | None = None,
        payload: str = "application/fhir+json",
        reason: str | None = None,
        end_time: datetime | None = None,
        headers: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Subscription resource.

        Args:
            subscription_id: Resource ID (generates UUID if None)
            status: Subscription status
            criteria: Search criteria for triggering
            channel_type: Notification channel type
            endpoint: Notification endpoint URL
            payload: MIME type for payload
            reason: Reason for subscription
            end_time: When subscription expires
            headers: HTTP headers for rest-hook

        Returns:
            Subscription FHIR resource
        """
        if subscription_id is None:
            subscription_id = self._generate_id()

        if criteria is None:
            pattern = self.faker.random_element(self.CRITERIA_PATTERNS)
            criteria = pattern.replace(
                "{date}",
                (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d"),
            )

        if reason is None:
            reasons = [
                "Monitor patient vital signs",
                "Track medication adherence",
                "Alert on critical lab results",
                "Notify on admission/discharge",
                "Monitor condition changes",
                "Real-time clinical decision support",
            ]
            reason = self.faker.random_element(reasons)

        if endpoint is None and channel_type == "rest-hook":
            endpoint = f"https://{self.faker.domain_name()}/fhir/notifications"
        elif endpoint is None and channel_type == "email":
            endpoint = f"mailto:{self.faker.email()}"

        subscription: dict[str, Any] = {
            "resourceType": "Subscription",
            "id": subscription_id,
            "meta": self._generate_meta(),
            "status": status,
            "reason": reason,
            "criteria": criteria,
            "channel": {
                "type": channel_type,
                "payload": payload,
            },
        }

        # Add endpoint for applicable channel types
        if endpoint and channel_type in ["rest-hook", "email", "message"]:
            subscription["channel"]["endpoint"] = endpoint

        # Add headers for rest-hook
        if channel_type == "rest-hook":
            if headers:
                subscription["channel"]["header"] = headers
            elif self.faker.boolean(chance_of_getting_true=50):
                subscription["channel"]["header"] = [
                    f"Authorization: Bearer {self.faker.sha256()[:32]}",
                ]

        # Add contact information
        if self.faker.boolean(chance_of_getting_true=40):
            subscription["contact"] = [
                self._generate_contact_point("email", use="work"),
            ]

        # Add end time
        if end_time:
            subscription["end"] = end_time.isoformat()
        elif self.faker.boolean(chance_of_getting_true=30):
            future_end = datetime.now(timezone.utc) + timedelta(days=self.faker.random_int(30, 365))
            subscription["end"] = future_end.isoformat()

        # Add error for error status
        if status == "error":
            errors = [
                "Connection refused to endpoint",
                "HTTP 503 Service Unavailable",
                "SSL certificate verification failed",
                "Endpoint timeout after 30 seconds",
                "Invalid response from endpoint",
            ]
            subscription["error"] = self.faker.random_element(errors)

        return subscription

    def generate_rest_hook(
        self,
        criteria: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a REST hook subscription.

        Args:
            criteria: Search criteria
            endpoint: Webhook URL

        Returns:
            Subscription FHIR resource
        """
        return self.generate(
            criteria=criteria,
            channel_type="rest-hook",
            endpoint=endpoint,
            **kwargs,
        )

    def generate_websocket(
        self,
        criteria: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a WebSocket subscription.

        Args:
            criteria: Search criteria

        Returns:
            Subscription FHIR resource
        """
        return self.generate(
            criteria=criteria,
            channel_type="websocket",
            **kwargs,
        )
