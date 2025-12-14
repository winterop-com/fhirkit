"""PractitionerRole resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class PractitionerRoleGenerator(FHIRResourceGenerator):
    """Generator for FHIR PractitionerRole resources."""

    # Practitioner role codes
    ROLE_CODES = [
        {"code": "doctor", "display": "Doctor", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
        {"code": "nurse", "display": "Nurse", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
        {"code": "pharmacist", "display": "Pharmacist", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
        {"code": "researcher", "display": "Researcher", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
        {"code": "teacher", "display": "Teacher/Educator", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
        {"code": "ict", "display": "ICT Professional", "system": "http://terminology.hl7.org/CodeSystem/practitioner-role"},
    ]

    # Specialty codes (SNOMED CT)
    SPECIALTY_CODES = [
        {"code": "394814009", "display": "General practice", "system": "http://snomed.info/sct"},
        {"code": "394802001", "display": "General medicine", "system": "http://snomed.info/sct"},
        {"code": "394592004", "display": "Clinical oncology", "system": "http://snomed.info/sct"},
        {"code": "394579002", "display": "Cardiology", "system": "http://snomed.info/sct"},
        {"code": "394585009", "display": "Obstetrics and gynecology", "system": "http://snomed.info/sct"},
        {"code": "394537008", "display": "Pediatrics", "system": "http://snomed.info/sct"},
        {"code": "394576009", "display": "Surgical-Accident & emergency", "system": "http://snomed.info/sct"},
        {"code": "394600006", "display": "Psychiatry", "system": "http://snomed.info/sct"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        practitioner_role_id: str | None = None,
        practitioner_ref: str | None = None,
        organization_ref: str | None = None,
        location_ref: str | None = None,
        role_code: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PractitionerRole resource.

        Args:
            practitioner_role_id: Role ID (generates UUID if None)
            practitioner_ref: Reference to Practitioner
            organization_ref: Reference to Organization
            location_ref: Reference to Location
            role_code: Role code (random if None)

        Returns:
            PractitionerRole FHIR resource
        """
        if practitioner_role_id is None:
            practitioner_role_id = self._generate_id()

        # Select role
        if role_code is None:
            role_coding = self.faker.random_element(self.ROLE_CODES)
        else:
            role_coding = next(
                (r for r in self.ROLE_CODES if r["code"] == role_code),
                self.ROLE_CODES[0],
            )

        # Select specialty
        specialty_coding = self.faker.random_element(self.SPECIALTY_CODES)

        practitioner_role: dict[str, Any] = {
            "resourceType": "PractitionerRole",
            "id": practitioner_role_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/practitioner-role-ids",
                    value=f"ROLE-{self.faker.numerify('######')}",
                ),
            ],
            "active": True,
            "code": [
                {
                    "coding": [role_coding],
                    "text": role_coding["display"],
                }
            ],
            "specialty": [
                {
                    "coding": [specialty_coding],
                    "text": specialty_coding["display"],
                }
            ],
            "telecom": [
                self._generate_contact_point("phone", use="work"),
                self._generate_contact_point("email", use="work"),
            ],
            "availableTime": [
                {
                    "daysOfWeek": ["mon", "tue", "wed", "thu", "fri"],
                    "availableStartTime": "09:00:00",
                    "availableEndTime": "17:00:00",
                }
            ],
        }

        if practitioner_ref:
            practitioner_role["practitioner"] = {"reference": practitioner_ref}

        if organization_ref:
            practitioner_role["organization"] = {"reference": organization_ref}

        if location_ref:
            practitioner_role["location"] = [{"reference": location_ref}]

        return practitioner_role
