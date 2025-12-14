"""HealthcareService resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class HealthcareServiceGenerator(FHIRResourceGenerator):
    """Generator for FHIR HealthcareService resources.

    HealthcareService describes a healthcare service available at a location,
    including details about the service type, specialty, and availability.
    """

    # Service categories
    SERVICE_CATEGORIES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "1", "display": "Adoption"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "2", "display": "Aged Care"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "8", "display": "Counselling"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-category",
            "code": "17",
            "display": "General Practice",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-category",
            "code": "27",
            "display": "Specialist Medical",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "35", "display": "Hospital"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-category",
            "code": "36",
            "display": "Emergency Department",
        },
    ]

    # Service types
    SERVICE_TYPES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "124", "display": "General Practice"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "57", "display": "Immunization"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "221", "display": "Surgery - General"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "394579002", "display": "Cardiology"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "394582007", "display": "Dermatology"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-type",
            "code": "394583002",
            "display": "Endocrinology",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-type",
            "code": "394584008",
            "display": "Gastroenterology",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/service-type",
            "code": "394585009",
            "display": "Obstetrics and Gynecology",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "394587001", "display": "Psychiatry"},
        {"system": "http://terminology.hl7.org/CodeSystem/service-type", "code": "394589003", "display": "Nephrology"},
    ]

    # Specialties
    SPECIALTIES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "394814009", "display": "General practice"},
        {"system": "http://snomed.info/sct", "code": "394579002", "display": "Cardiology"},
        {"system": "http://snomed.info/sct", "code": "394582007", "display": "Dermatology"},
        {"system": "http://snomed.info/sct", "code": "394583002", "display": "Endocrinology"},
        {"system": "http://snomed.info/sct", "code": "394584008", "display": "Gastroenterology"},
        {"system": "http://snomed.info/sct", "code": "394585009", "display": "Obstetrics and Gynecology"},
        {"system": "http://snomed.info/sct", "code": "394587001", "display": "Psychiatry"},
        {"system": "http://snomed.info/sct", "code": "394589003", "display": "Nephrology"},
        {"system": "http://snomed.info/sct", "code": "408443003", "display": "General medical practice"},
        {"system": "http://snomed.info/sct", "code": "419772000", "display": "Family practice"},
    ]

    # Days of week
    DAYS_OF_WEEK: list[str] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        service_id: str | None = None,
        organization_ref: str | None = None,
        location_ref: str | None = None,
        active: bool | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a HealthcareService resource.

        Args:
            service_id: Resource ID (generates UUID if None)
            organization_ref: Organization providing the service
            location_ref: Location where service is available
            active: Whether service is active

        Returns:
            HealthcareService FHIR resource
        """
        if service_id is None:
            service_id = self._generate_id()

        if active is None:
            active = self.faker.boolean(chance_of_getting_true=90)

        # Select category, type, and specialty
        category = self.faker.random_element(self.SERVICE_CATEGORIES)
        service_type = self.faker.random_element(self.SERVICE_TYPES)
        specialty = self.faker.random_element(self.SPECIALTIES)

        # Generate service name
        service_name = f"{specialty['display']} Services"

        service: dict[str, Any] = {
            "resourceType": "HealthcareService",
            "id": service_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/service-ids",
                    value=f"SVC-{self.faker.numerify('######')}",
                )
            ],
            "active": active,
            "category": [make_codeable_concept(category)],
            "type": [make_codeable_concept(service_type)],
            "specialty": [make_codeable_concept(specialty)],
            "name": service_name,
            "comment": f"Providing {specialty['display'].lower()} services to patients",
            "telecom": [
                {
                    "system": "phone",
                    "value": self.faker.phone_number(),
                    "use": "work",
                },
                {
                    "system": "email",
                    "value": f"{service_type['code'].lower()}@example.org",
                    "use": "work",
                },
            ],
            "availableTime": self._generate_available_times(),
            "availabilityExceptions": "Closed on public holidays",
        }

        # Add appointment required flag
        service["appointmentRequired"] = self.faker.boolean(chance_of_getting_true=70)

        if organization_ref:
            service["providedBy"] = {"reference": organization_ref}

        if location_ref:
            service["location"] = [{"reference": location_ref}]

        return service

    def _generate_available_times(self) -> list[dict[str, Any]]:
        """Generate available time slots."""
        # Weekday hours
        available_times = [
            {
                "daysOfWeek": ["mon", "tue", "wed", "thu", "fri"],
                "availableStartTime": "08:00:00",
                "availableEndTime": "17:00:00",
            }
        ]

        # Maybe add Saturday hours
        if self.faker.boolean(chance_of_getting_true=40):
            available_times.append(
                {
                    "daysOfWeek": ["sat"],
                    "availableStartTime": "09:00:00",
                    "availableEndTime": "13:00:00",
                }
            )

        return available_times
