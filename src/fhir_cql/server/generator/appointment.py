"""Appointment resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class AppointmentGenerator(FHIRResourceGenerator):
    """Generator for FHIR Appointment resources."""

    # Appointment status codes
    STATUS_CODES = [
        "proposed",
        "pending",
        "booked",
        "arrived",
        "fulfilled",
        "cancelled",
        "noshow",
        "entered-in-error",
        "checked-in",
        "waitlist",
    ]

    # Service categories
    SERVICE_CATEGORIES = [
        {
            "code": "17",
            "display": "General Practice",
            "system": "http://terminology.hl7.org/CodeSystem/service-category",
        },
        {
            "code": "27",
            "display": "Specialist Medical",
            "system": "http://terminology.hl7.org/CodeSystem/service-category",
        },
        {"code": "2", "display": "Aged Care", "system": "http://terminology.hl7.org/CodeSystem/service-category"},
        {"code": "4", "display": "Allied Health", "system": "http://terminology.hl7.org/CodeSystem/service-category"},
    ]

    # Service types
    SERVICE_TYPES = [
        {"code": "124", "display": "General Practice", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
        {"code": "57", "display": "Immunization", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
        {"code": "168", "display": "Nursing", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
        {"code": "540", "display": "Physical Therapy", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
    ]

    # Appointment types
    APPOINTMENT_TYPES = [
        {
            "code": "ROUTINE",
            "display": "Routine appointment",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
        },
        {
            "code": "WALKIN",
            "display": "A walk-in appointment",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
        },
        {"code": "CHECKUP", "display": "A routine check-up", "system": "http://terminology.hl7.org/CodeSystem/v2-0276"},
        {"code": "FOLLOWUP", "display": "A follow-up visit", "system": "http://terminology.hl7.org/CodeSystem/v2-0276"},
        {
            "code": "EMERGENCY",
            "display": "Emergency appointment",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
        },
    ]

    # Participant statuses
    PARTICIPANT_STATUS = ["accepted", "declined", "tentative", "needs-action"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        appointment_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        location_ref: str | None = None,
        slot_ref: str | None = None,
        status: str = "booked",
        start: datetime | None = None,
        duration_minutes: int = 30,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Appointment resource.

        Args:
            appointment_id: Appointment ID (generates UUID if None)
            patient_ref: Reference to Patient
            practitioner_ref: Reference to Practitioner
            location_ref: Reference to Location
            slot_ref: Reference to Slot
            status: Appointment status
            start: Start datetime (random future if None)
            duration_minutes: Duration in minutes

        Returns:
            Appointment FHIR resource
        """
        if appointment_id is None:
            appointment_id = self._generate_id()

        # Generate future start time if not provided
        if start is None:
            future_days = self.faker.random_int(min=1, max=30)
            hour = self.faker.random_int(min=8, max=16)
            minute = self.faker.random_element([0, 15, 30, 45])
            start = datetime.now(timezone.utc) + timedelta(days=future_days)
            start = start.replace(hour=hour, minute=minute, second=0, microsecond=0)

        end = start + timedelta(minutes=duration_minutes)

        service_category = self.faker.random_element(self.SERVICE_CATEGORIES)
        service_type = self.faker.random_element(self.SERVICE_TYPES)
        appointment_type = self.faker.random_element(self.APPOINTMENT_TYPES)

        appointment: dict[str, Any] = {
            "resourceType": "Appointment",
            "id": appointment_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/appointment-ids",
                    value=f"APT-{self.faker.numerify('######')}",
                ),
            ],
            "status": status,
            "serviceCategory": [{"coding": [service_category], "text": service_category["display"]}],
            "serviceType": [{"coding": [service_type], "text": service_type["display"]}],
            "appointmentType": {"coding": [appointment_type], "text": appointment_type["display"]},
            "description": f"{appointment_type['display']} - {service_type['display']}",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "minutesDuration": duration_minutes,
            "created": datetime.now(timezone.utc).isoformat(),
            "comment": self.faker.sentence(nb_words=8),
            "participant": [],
        }

        # Add slot reference if provided
        if slot_ref:
            appointment["slot"] = [{"reference": slot_ref}]

        # Add patient participant
        if patient_ref:
            appointment["participant"].append(
                {
                    "actor": {"reference": patient_ref},
                    "required": "required",
                    "status": "accepted",
                }
            )

        # Add practitioner participant
        if practitioner_ref:
            appointment["participant"].append(
                {
                    "actor": {"reference": practitioner_ref},
                    "required": "required",
                    "status": "accepted",
                }
            )

        # Add location participant
        if location_ref:
            appointment["participant"].append(
                {
                    "actor": {"reference": location_ref},
                    "required": "required",
                    "status": "accepted",
                }
            )

        # Ensure at least one participant
        if not appointment["participant"]:
            appointment["participant"].append(
                {
                    "required": "required",
                    "status": "needs-action",
                }
            )

        return appointment
