"""Person resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class PersonGenerator(FHIRResourceGenerator):
    """Generator for FHIR Person resources."""

    LINK_ASSURANCE_LEVELS = ["level1", "level2", "level3", "level4"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        person_id: str | None = None,
        active: bool = True,
        name_family: str | None = None,
        name_given: list[str] | None = None,
        gender: str | None = None,
        birth_date: str | None = None,
        telecom: list[dict[str, Any]] | None = None,
        address: dict[str, Any] | None = None,
        managing_organization_reference: str | None = None,
        link_references: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Person resource.

        Args:
            person_id: Resource ID (generates UUID if None)
            active: Whether the record is active
            name_family: Family name
            name_given: Given names
            gender: Administrative gender
            birth_date: Date of birth
            telecom: Contact details
            address: Address information
            managing_organization_reference: Reference to managing Organization
            link_references: Links to related Patient/Practitioner/RelatedPerson

        Returns:
            Person FHIR resource
        """
        if person_id is None:
            person_id = self._generate_id()

        if name_family is None:
            name_family = self.faker.last_name()

        if name_given is None:
            name_given = [self.faker.first_name()]

        if gender is None:
            gender = self.faker.random_element(["male", "female", "other", "unknown"])

        if birth_date is None:
            birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=90).isoformat()

        person: dict[str, Any] = {
            "resourceType": "Person",
            "id": person_id,
            "active": active,
            "name": [
                {
                    "use": "official",
                    "family": name_family,
                    "given": name_given,
                }
            ],
            "gender": gender,
            "birthDate": birth_date,
        }

        # Add telecom
        if telecom:
            person["telecom"] = telecom
        else:
            person["telecom"] = [
                {
                    "system": "phone",
                    "value": self.faker.phone_number(),
                    "use": "home",
                },
                {
                    "system": "email",
                    "value": self.faker.email(),
                    "use": "home",
                },
            ]

        # Add address
        if address:
            person["address"] = [address]
        else:
            person["address"] = [
                {
                    "use": "home",
                    "type": "physical",
                    "line": [self.faker.street_address()],
                    "city": self.faker.city(),
                    "state": self.faker.state_abbr(),
                    "postalCode": self.faker.postcode(),
                    "country": "US",
                }
            ]

        # Add managing organization
        if managing_organization_reference:
            person["managingOrganization"] = {"reference": managing_organization_reference}

        # Add links to related resources
        if link_references:
            person["link"] = link_references
        elif self.faker.boolean(chance_of_getting_true=50):
            # Add a link to a Patient
            person["link"] = [
                {
                    "target": {"reference": f"Patient/{self._generate_id()}"},
                    "assurance": self.faker.random_element(self.LINK_ASSURANCE_LEVELS),
                }
            ]

        return person

    def generate_with_patient_link(
        self,
        patient_id: str,
        assurance: str = "level3",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Person with a link to a Patient.

        Args:
            patient_id: Patient ID to link to
            assurance: Assurance level of the link

        Returns:
            Person FHIR resource
        """
        link_references = [
            {
                "target": {"reference": f"Patient/{patient_id}"},
                "assurance": assurance,
            }
        ]
        return self.generate(link_references=link_references, **kwargs)
