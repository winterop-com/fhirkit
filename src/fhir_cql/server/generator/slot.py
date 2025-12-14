"""Slot resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SlotGenerator(FHIRResourceGenerator):
    """Generator for FHIR Slot resources."""

    # Slot status codes
    STATUS_CODES = ["busy", "free", "busy-unavailable", "busy-tentative", "entered-in-error"]

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
    ]

    # Service types
    SERVICE_TYPES = [
        {"code": "124", "display": "General Practice", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
        {"code": "57", "display": "Immunization", "system": "http://terminology.hl7.org/CodeSystem/service-type"},
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
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        slot_id: str | None = None,
        schedule_ref: str | None = None,
        status: str = "free",
        start: datetime | None = None,
        duration_minutes: int = 30,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Slot resource.

        Args:
            slot_id: Slot ID (generates UUID if None)
            schedule_ref: Reference to Schedule (required in FHIR)
            status: Slot status (free, busy, etc.)
            start: Start datetime (random future if None)
            duration_minutes: Duration in minutes

        Returns:
            Slot FHIR resource
        """
        if slot_id is None:
            slot_id = self._generate_id()

        # Generate future start time if not provided
        if start is None:
            future_days = self.faker.random_int(min=1, max=14)
            hour = self.faker.random_int(min=8, max=16)
            minute = self.faker.random_element([0, 15, 30, 45])
            start = datetime.now(timezone.utc) + timedelta(days=future_days)
            start = start.replace(hour=hour, minute=minute, second=0, microsecond=0)

        end = start + timedelta(minutes=duration_minutes)

        service_category = self.faker.random_element(self.SERVICE_CATEGORIES)
        service_type = self.faker.random_element(self.SERVICE_TYPES)
        appointment_type = self.faker.random_element(self.APPOINTMENT_TYPES)

        slot: dict[str, Any] = {
            "resourceType": "Slot",
            "id": slot_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/slot-ids",
                    value=f"SLOT-{self.faker.numerify('######')}",
                ),
            ],
            "serviceCategory": [{"coding": [service_category], "text": service_category["display"]}],
            "serviceType": [{"coding": [service_type], "text": service_type["display"]}],
            "appointmentType": {"coding": [appointment_type], "text": appointment_type["display"]},
            "status": status,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "overbooked": False,
            "comment": f"{duration_minutes}-minute {appointment_type['display'].lower()}",
        }

        if schedule_ref:
            slot["schedule"] = {"reference": schedule_ref}

        return slot

    def generate_day_slots(
        self,
        schedule_ref: str,
        date: datetime | None = None,
        start_hour: int = 9,
        end_hour: int = 17,
        slot_duration_minutes: int = 30,
        lunch_hour: int = 12,
    ) -> list[dict[str, Any]]:
        """Generate all slots for a day.

        Args:
            schedule_ref: Reference to Schedule
            date: Date for slots (tomorrow if None)
            start_hour: Start hour of day
            end_hour: End hour of day
            slot_duration_minutes: Duration of each slot
            lunch_hour: Hour to skip for lunch

        Returns:
            List of Slot resources for the day
        """
        if date is None:
            date = datetime.now(timezone.utc) + timedelta(days=1)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)

        slots = []
        current = date.replace(hour=start_hour, minute=0)
        end = date.replace(hour=end_hour, minute=0)

        while current < end:
            # Skip lunch hour
            if current.hour != lunch_hour:
                slot = self.generate(
                    schedule_ref=schedule_ref,
                    status="free",
                    start=current,
                    duration_minutes=slot_duration_minutes,
                )
                slots.append(slot)

            current += timedelta(minutes=slot_duration_minutes)

        return slots
