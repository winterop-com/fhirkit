"""MessageHeader resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class MessageHeaderGenerator(FHIRResourceGenerator):
    """Generator for FHIR MessageHeader resources."""

    # Message event types (from http://hl7.org/fhir/message-events)
    MESSAGE_EVENTS = [
        {
            "code": "admin-notify",
            "display": "Admin Notify",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
        {
            "code": "diagnosticreport-provide",
            "display": "Provide a DiagnosticReport",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
        {
            "code": "observation-provide",
            "display": "Provide an Observation",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
        {
            "code": "patient-link",
            "display": "Patient Link",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
        {
            "code": "patient-unlink",
            "display": "Patient Unlink",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
        {
            "code": "valueset-expand",
            "display": "ValueSet Expand",
            "system": "http://terminology.hl7.org/CodeSystem/message-events",
        },
    ]

    # Response codes
    RESPONSE_CODES = ["ok", "transient-error", "fatal-error"]

    # Reason codes for message
    REASON_CODES = [
        {
            "code": "admit",
            "display": "Admit",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
        {
            "code": "discharge",
            "display": "Discharge",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
        {
            "code": "absent",
            "display": "Absent",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
        {
            "code": "return",
            "display": "Return",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
        {
            "code": "moved",
            "display": "Moved",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
        {
            "code": "edit",
            "display": "Edit",
            "system": "http://terminology.hl7.org/CodeSystem/message-reasons-encounter",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def _generate_version(self) -> str:
        """Generate a semantic version string."""
        major = self.faker.random_int(1, 10)
        minor = self.faker.random_int(0, 9)
        patch = self.faker.random_int(0, 99)
        return f"{major}.{minor}.{patch}"

    def generate(
        self,
        message_id: str | None = None,
        event_code: str | None = None,
        event_uri: str | None = None,
        source_endpoint: str | None = None,
        destination_endpoint: str | None = None,
        sender_ref: str | None = None,
        author_ref: str | None = None,
        focus_refs: list[str] | None = None,
        is_response: bool = False,
        response_to_id: str | None = None,
        response_code: str = "ok",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MessageHeader resource.

        Args:
            message_id: Message header ID (generates UUID if None)
            event_code: Event code (uses random if None and no event_uri)
            event_uri: Event URI (alternative to eventCoding)
            source_endpoint: Source endpoint URL
            destination_endpoint: Destination endpoint URL
            sender_ref: Reference to sending organization/practitioner
            author_ref: Reference to author
            focus_refs: List of references to focus resources
            is_response: Whether this is a response message
            response_to_id: ID of message this responds to
            response_code: Response code (ok, transient-error, fatal-error)

        Returns:
            MessageHeader FHIR resource
        """
        if message_id is None:
            message_id = self._generate_id()

        # Generate source endpoint if not provided
        if source_endpoint is None:
            source_endpoint = f"http://{self.faker.domain_name()}/fhir/messaging"

        message_header: dict[str, Any] = {
            "resourceType": "MessageHeader",
            "id": message_id,
            "meta": self._generate_meta(),
        }

        # Generate event - either eventUri or eventCoding
        if event_uri:
            message_header["eventUri"] = event_uri
        else:
            event_coding = (
                next((e for e in self.MESSAGE_EVENTS if e["code"] == event_code), None)
                if event_code
                else self.faker.random_element(self.MESSAGE_EVENTS)
            )
            message_header["eventCoding"] = event_coding

        message_header["source"] = {
            "name": self.faker.company(),
            "software": f"{self.faker.word().title()} EHR",
            "version": self._generate_version(),
            "contact": self._generate_contact_point("email"),
            "endpoint": source_endpoint,
        }

        # Add destination if provided
        if destination_endpoint:
            message_header["destination"] = [
                {
                    "name": self.faker.company(),
                    "endpoint": destination_endpoint,
                }
            ]

        # Add sender reference
        if sender_ref:
            message_header["sender"] = {"reference": sender_ref}

        # Add author reference
        if author_ref:
            message_header["author"] = {"reference": author_ref}

        # Add focus references
        if focus_refs:
            message_header["focus"] = [{"reference": ref} for ref in focus_refs]

        # Add reason
        if self.faker.boolean(chance_of_getting_true=50):
            reason = self.faker.random_element(self.REASON_CODES)
            message_header["reason"] = {
                "coding": [reason],
                "text": reason["display"],
            }

        # Add response element if this is a response message
        if is_response and response_to_id:
            message_header["response"] = {
                "identifier": response_to_id,
                "code": response_code,
            }

        return message_header

    def generate_response(
        self,
        original_message_id: str,
        response_code: str = "ok",
        source_endpoint: str | None = None,
        error_details_ref: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a response MessageHeader.

        Args:
            original_message_id: ID of the original message being responded to
            response_code: ok, transient-error, or fatal-error
            source_endpoint: Source endpoint URL
            error_details_ref: Reference to OperationOutcome for errors

        Returns:
            MessageHeader FHIR resource as a response
        """
        message = self.generate(
            source_endpoint=source_endpoint,
            is_response=True,
            response_to_id=original_message_id,
            response_code=response_code,
            **kwargs,
        )

        # Add error details if provided
        if error_details_ref and response_code != "ok":
            message["response"]["details"] = {"reference": error_details_ref}

        return message
