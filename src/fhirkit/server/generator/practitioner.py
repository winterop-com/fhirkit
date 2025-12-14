"""Practitioner resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import PRACTITIONER_SPECIALTIES, make_codeable_concept


class PractitionerGenerator(FHIRResourceGenerator):
    """Generator for FHIR Practitioner resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        practitioner_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Practitioner resource.

        Args:
            practitioner_id: Practitioner ID (generates UUID if None)

        Returns:
            Practitioner FHIR resource
        """
        if practitioner_id is None:
            practitioner_id = self._generate_id()

        gender = self.faker.random_element(["male", "female"])
        if gender == "male":
            first_name = self.faker.first_name_male()
            prefix = self.faker.random_element(["Dr.", "Dr."])
        else:
            first_name = self.faker.first_name_female()
            prefix = self.faker.random_element(["Dr.", "Dr."])

        last_name = self.faker.last_name()

        # Generate NPI (National Provider Identifier)
        npi = self.faker.numerify("##########")

        # Pick a specialty
        specialty = self.faker.random_element(PRACTITIONER_SPECIALTIES)

        practitioner: dict[str, Any] = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://hl7.org/fhir/sid/us-npi",
                    value=npi,
                    type_code="NPI",
                    type_display="National Provider Identifier",
                ),
            ],
            "active": True,
            "name": [
                self._generate_human_name(
                    family=last_name,
                    given=[first_name],
                    prefix=prefix,
                )
            ],
            "telecom": [
                self._generate_contact_point("phone", use="work"),
                self._generate_contact_point("email", use="work"),
            ],
            "gender": gender,
            "qualification": [
                {
                    "code": make_codeable_concept(specialty),
                    "issuer": {
                        "display": "American Board of Medical Specialties",
                    },
                }
            ],
        }

        return practitioner
