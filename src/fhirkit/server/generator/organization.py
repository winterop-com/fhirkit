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
        {
            "code": "bus",
            "display": "Non-Healthcare Business",
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        },
        {
            "code": "team",
            "display": "Organizational team",
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        },
    ]

    # Hierarchy order for generating linked organizations (Corporate -> Division -> Department -> Unit)
    HIERARCHY_ORDER = ["bus", "prov", "dept", "team"]

    # Organization type info for hierarchy levels
    HIERARCHY_TYPES = {
        "bus": {"code": "bus", "display": "Non-Healthcare Business", "level_name": "Corporation"},
        "prov": {"code": "prov", "display": "Healthcare Provider", "level_name": "Division"},
        "dept": {"code": "dept", "display": "Hospital Department", "level_name": "Department"},
        "team": {"code": "team", "display": "Organizational team", "level_name": "Unit"},
    }

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

    # Name patterns for hierarchy levels
    HIERARCHY_NAME_PATTERNS = {
        "bus": ["{base} Healthcare Corporation", "{base} Health System", "{base} Medical Group"],
        "prov": ["{base} Regional Division", "{base} Medical Services", "{base} Healthcare Division"],
        "dept": ["{specialty} Department", "{specialty} Services", "Department of {specialty}"],
        "team": ["{specialty} Team", "{specialty} Unit", "{specialty} Care Team"],
    }

    # Medical specialties for department/team names
    SPECIALTIES = [
        "Cardiology",
        "Oncology",
        "Neurology",
        "Pediatrics",
        "Emergency",
        "Surgery",
        "Radiology",
        "Orthopedics",
        "Internal Medicine",
        "Pharmacy",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        organization_id: str | None = None,
        name: str | None = None,
        org_type: str | None = None,
        part_of_ref: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Organization resource.

        Args:
            organization_id: Organization ID (generates UUID if None)
            name: Organization name (generates random if None)
            org_type: Organization type code (random if None)
            part_of_ref: Reference to parent organization (e.g., "Organization/123")

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

        # Add parent organization reference
        if part_of_ref:
            organization["partOf"] = {"reference": part_of_ref}

        return organization

    def generate_hierarchy(
        self,
        depth: int = 4,
        base_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generate an organization hierarchy.

        Creates a chain of organizations linked via partOf from root to leaf.

        Args:
            depth: Number of levels in hierarchy (1-4, maps to Corporation->Division->Department->Unit)
            base_name: Base name to use for consistent naming across hierarchy

        Returns:
            List of Organization resources, from root (no partOf) to leaf (deepest nesting)
        """
        depth = max(1, min(depth, len(self.HIERARCHY_ORDER)))
        org_types = self.HIERARCHY_ORDER[:depth]

        if base_name is None:
            base_name = self.faker.last_name()

        organizations: list[dict[str, Any]] = []
        parent_ref: str | None = None

        for i, org_type in enumerate(org_types):
            # Generate appropriate name for hierarchy level
            patterns = self.HIERARCHY_NAME_PATTERNS.get(org_type, ["{base}"])
            pattern = self.faker.random_element(patterns)

            if "{specialty}" in pattern:
                specialty = self.faker.random_element(self.SPECIALTIES)
                name = pattern.format(specialty=specialty)
            else:
                name = pattern.format(base=base_name)

            org = self.generate(
                name=name,
                org_type=org_type,
                part_of_ref=parent_ref,
            )

            organizations.append(org)
            parent_ref = f"Organization/{org['id']}"

        return organizations
