"""Organization resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class OrganizationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Organization resources."""

    # Common healthcare organization types
    ORG_TYPES = [
        {
            "code": "prov",
            "display": "Healthcare Provider",
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        },
        {
            "code": "dept",
            "display": "Hospital Department",
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        },
        {
            "code": "ins",
            "display": "Insurance Company",
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        },
        {"code": "pay", "display": "Payer", "system": "http://terminology.hl7.org/CodeSystem/organization-type"},
        {"code": "govt", "display": "Government", "system": "http://terminology.hl7.org/CodeSystem/organization-type"},
    ]

    # Common hospital name patterns
    HOSPITAL_NAMES = [
        "{city} General Hospital",
        "{city} Medical Center",
        "St. {name} Hospital",
        "{name} Memorial Hospital",
        "{city} Community Hospital",
        "University of {city} Health",
        "{name} Health System",
        "{city} Regional Medical Center",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        organization_id: str | None = None,
        name: str | None = None,
        org_type: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Organization resource.

        Args:
            organization_id: Organization ID (generates UUID if None)
            name: Organization name (generates random if None)
            org_type: Organization type code (random if None)

        Returns:
            Organization FHIR resource
        """
        if organization_id is None:
            organization_id = self._generate_id()

        # Generate organization name
        if name is None:
            pattern = self.faker.random_element(self.HOSPITAL_NAMES)
            name = pattern.format(
                city=self.faker.city(),
                name=self.faker.last_name(),
            )

        # Select org type
        if org_type is None:
            type_coding = self.faker.random_element(self.ORG_TYPES)
        else:
            type_coding = next(
                (t for t in self.ORG_TYPES if t["code"] == org_type),
                self.ORG_TYPES[0],
            )

        organization: dict[str, Any] = {
            "resourceType": "Organization",
            "id": organization_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://hl7.org/fhir/sid/us-npi",
                    value=self.faker.numerify("##########"),
                    type_code="NPI",
                    type_display="National Provider Identifier",
                ),
            ],
            "active": True,
            "type": [
                {
                    "coding": [type_coding],
                    "text": type_coding["display"],
                }
            ],
            "name": name,
            "telecom": [
                self._generate_contact_point("phone", use="work"),
            ],
            "address": [self._generate_address(use="work")],
        }

        return organization
