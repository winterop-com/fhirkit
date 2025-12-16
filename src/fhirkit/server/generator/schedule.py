"""Schedule resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ScheduleGenerator(FHIRResourceGenerator):
    """Generator for FHIR Schedule resources."""

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

    # Specialties (SNOMED CT)
    SPECIALTIES = [
        {"code": "394814009", "display": "General practice", "system": "http://snomed.info/sct"},
        {"code": "394579002", "display": "Cardiology", "system": "http://snomed.info/sct"},
        {"code": "394537008", "display": "Pediatrics", "system": "http://snomed.info/sct"},
        {"code": "394585009", "display": "Obstetrics and gynecology", "system": "http://snomed.info/sct"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        schedule_id: str | None = None,
        practitioner_ref: str | None = None,
        location_ref: str | None = None,
        planning_horizon_days: int = 30,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Schedule resource.

        Args:
            schedule_id: Schedule ID (generates UUID if None)
            practitioner_ref: Reference to Practitioner
            location_ref: Reference to Location
            planning_horizon_days: Number of days in planning horizon

        Returns:
            Schedule FHIR resource
        """
        if schedule_id is None:
            schedule_id = self._generate_id()

        service_category = self.faker.random_element(self.SERVICE_CATEGORIES)
        service_type = self.faker.random_element(self.SERVICE_TYPES)
        specialty = self.faker.random_element(self.SPECIALTIES)

        now = datetime.now(timezone.utc)
        planning_end = now + timedelta(days=planning_horizon_days)

        schedule: dict[str, Any] = {
            "resourceType": "Schedule",
            "id": schedule_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/schedule-ids",
                    value=f"{specialty['display']} - {service_type['display']}",
                ),
            ],
            "active": True,
            "serviceCategory": [{"coding": [service_category], "text": service_category["display"]}],
            "serviceType": [{"coding": [service_type], "text": service_type["display"]}],
            "specialty": [{"coding": [specialty], "text": specialty["display"]}],
            "planningHorizon": {
                "start": now.isoformat(),
                "end": planning_end.isoformat(),
            },
            "comment": f"{specialty['display']} - {service_type['display']} Schedule",
            "actor": [],
        }

        # Add practitioner actor
        if practitioner_ref:
            schedule["actor"].append({"reference": practitioner_ref})

        # Add location actor
        if location_ref:
            schedule["actor"].append({"reference": location_ref})

        # Ensure at least one actor (FHIR requires it)
        if not schedule["actor"]:
            schedule["actor"].append({"display": f"{specialty['display']} Schedule"})

        return schedule
