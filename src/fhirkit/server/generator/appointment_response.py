"""AppointmentResponse resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class AppointmentResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR AppointmentResponse resources."""

    # Participant status codes
    PARTICIPANT_STATUS = ["accepted", "declined", "tentative", "needs-action"]

    # Participant type codes
    PARTICIPANT_TYPES = [
        {
            "code": "ATND",
            "display": "attender",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
        },
        {
            "code": "PPRF",
            "display": "primary performer",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
        },
        {
            "code": "SPRF",
            "display": "secondary performer",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
        },
        {
            "code": "LOC",
            "display": "location",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        appointment_ref: str | None = None,
        actor_ref: str | None = None,
        participant_status: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        comment: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an AppointmentResponse resource.

        Args:
            response_id: Response ID (generates UUID if None)
            appointment_ref: Reference to Appointment (required, generates if None)
            actor_ref: Reference to responding actor (Patient, Practitioner, etc.)
            participant_status: Status (accepted, declined, tentative, needs-action)
            start: Proposed start time
            end: Proposed end time
            comment: Response comment

        Returns:
            AppointmentResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        if participant_status is None:
            participant_status = self.faker.random_element(self.PARTICIPANT_STATUS)

        if appointment_ref is None:
            appointment_ref = f"Appointment/{self._generate_id()}"

        appointment_response: dict[str, Any] = {
            "resourceType": "AppointmentResponse",
            "id": response_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/appointment-response-ids",
                    value=f"APRESP-{self.faker.numerify('######')}",
                ),
            ],
            "appointment": {"reference": appointment_ref},
            "participantStatus": participant_status,
        }

        # Add actor reference
        if actor_ref:
            appointment_response["actor"] = {"reference": actor_ref}

        # Add participant type
        participant_type = self.faker.random_element(self.PARTICIPANT_TYPES)
        appointment_response["participantType"] = [
            {
                "coding": [participant_type],
                "text": participant_type["display"],
            }
        ]

        # Add proposed times if provided
        if start:
            appointment_response["start"] = start.isoformat()
        if end:
            appointment_response["end"] = end.isoformat()

        # Add comment
        if comment:
            appointment_response["comment"] = comment
        elif self.faker.boolean(chance_of_getting_true=40):
            comments_by_status = {
                "accepted": [
                    "Confirmed attendance",
                    "I will be there",
                    "Appointment confirmed",
                ],
                "declined": [
                    "Unable to attend due to scheduling conflict",
                    "Please reschedule",
                    "Cannot make this time",
                ],
                "tentative": [
                    "May be able to attend, will confirm later",
                    "Tentatively available",
                    "Need to check my schedule",
                ],
                "needs-action": [
                    "Awaiting confirmation",
                    "Need to review",
                    "Checking availability",
                ],
            }
            status_comments = comments_by_status.get(participant_status, [])
            if status_comments:
                appointment_response["comment"] = self.faker.random_element(status_comments)

        return appointment_response

    def generate_for_appointment(
        self,
        appointment_ref: str,
        actor_refs: list[str],
        participant_status: str = "accepted",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate responses for multiple actors for an appointment.

        Args:
            appointment_ref: Reference to the Appointment
            actor_refs: List of actor references
            participant_status: Default status for all responses

        Returns:
            List of AppointmentResponse resources
        """
        return [
            self.generate(
                appointment_ref=appointment_ref,
                actor_ref=actor_ref,
                participant_status=participant_status,
                **kwargs,
            )
            for actor_ref in actor_refs
        ]
