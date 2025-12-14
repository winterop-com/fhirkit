"""RelatedPerson resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class RelatedPersonGenerator(FHIRResourceGenerator):
    """Generator for FHIR RelatedPerson resources."""

    # Relationship codes
    RELATIONSHIP_CODES = [
        {"code": "FAMMEMB", "display": "Family Member", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "CHILD", "display": "Child", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "PARENT", "display": "Parent", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "SPS", "display": "Spouse", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "SIBLING", "display": "Sibling", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "GUARD", "display": "Guardian", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "ECON", "display": "Emergency Contact", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
        {"code": "FRND", "display": "Friend", "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        related_person_id: str | None = None,
        patient_ref: str | None = None,
        relationship_code: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a RelatedPerson resource.

        Args:
            related_person_id: RelatedPerson ID (generates UUID if None)
            patient_ref: Reference to Patient (required in FHIR)
            relationship_code: Relationship code (random if None)

        Returns:
            RelatedPerson FHIR resource
        """
        if related_person_id is None:
            related_person_id = self._generate_id()

        # Select relationship
        if relationship_code is None:
            rel_coding = self.faker.random_element(self.RELATIONSHIP_CODES)
        else:
            rel_coding = next(
                (r for r in self.RELATIONSHIP_CODES if r["code"] == relationship_code),
                self.RELATIONSHIP_CODES[0],
            )

        gender = self.faker.random_element(["male", "female"])

        related_person: dict[str, Any] = {
            "resourceType": "RelatedPerson",
            "id": related_person_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/related-person-ids",
                    value=f"RP-{self.faker.numerify('######')}",
                ),
            ],
            "active": True,
            "relationship": [
                {
                    "coding": [rel_coding],
                    "text": rel_coding["display"],
                }
            ],
            "name": [
                self._generate_human_name(
                    given=[self.faker.first_name_male() if gender == "male" else self.faker.first_name_female()],
                )
            ],
            "telecom": [
                self._generate_contact_point("phone", use="home"),
                self._generate_contact_point("email", use="home"),
            ],
            "gender": gender,
            "address": [self._generate_address(use="home")],
        }

        if patient_ref:
            related_person["patient"] = {"reference": patient_ref}

        return related_person
