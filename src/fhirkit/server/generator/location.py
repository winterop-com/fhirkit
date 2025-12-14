"""Location resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class LocationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Location resources with hierarchy support."""

    # Location types (from HL7 v3 RoleCode)
    LOCATION_TYPES = [
        {
            "code": "HOSP",
            "display": "Hospital",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "ER",
            "display": "Emergency Room",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "ICU",
            "display": "Intensive Care Unit",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "OR",
            "display": "Operating Room",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "PHARM",
            "display": "Pharmacy",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "LAB",
            "display": "Laboratory",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "CLINIC",
            "display": "Outpatient Clinic",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
        {
            "code": "RADIOLOGY",
            "display": "Radiology Department",
            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        },
    ]

    # Physical types (from location-physical-type)
    PHYSICAL_TYPES = [
        {
            "code": "si",
            "display": "Site",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "bu",
            "display": "Building",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "wi",
            "display": "Wing",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "wa",
            "display": "Ward",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "ro",
            "display": "Room",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "bd",
            "display": "Bed",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
        {
            "code": "area",
            "display": "Area",
            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        },
    ]

    # Operational status codes
    OPERATIONAL_STATUS = [
        {
            "code": "C",
            "display": "Closed",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
        },
        {
            "code": "H",
            "display": "Housekeeping",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
        },
        {
            "code": "O",
            "display": "Occupied",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
        },
        {
            "code": "U",
            "display": "Unoccupied",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
        },
        {
            "code": "K",
            "display": "Contaminated",
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
        },
    ]

    # Hierarchy order for generating linked locations
    HIERARCHY_ORDER = ["si", "bu", "wi", "wa", "ro", "bd"]

    # Location name templates by physical type
    NAME_TEMPLATES = {
        "si": ["{city} Medical Campus", "{name} Healthcare Campus", "{city} Health Center"],
        "bu": ["Main Building", "North Tower", "South Wing Building", "Medical Pavilion", "{name} Building"],
        "wi": ["East Wing", "West Wing", "North Wing", "South Wing", "Pediatric Wing", "Surgical Wing"],
        "wa": ["Ward {number}", "Medical Ward {number}", "Surgical Ward", "Maternity Ward", "Oncology Ward"],
        "ro": ["Room {number}", "Exam Room {number}", "Treatment Room {number}", "Consultation Room {number}"],
        "bd": ["Bed {number}A", "Bed {number}B", "Bed {number}", "Bay {number}"],
        "area": ["Waiting Area", "Reception Area", "Triage Area", "Recovery Area"],
    }

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        location_id: str | None = None,
        name: str | None = None,
        location_type: str | None = None,
        physical_type: str | None = None,
        part_of_ref: str | None = None,
        managing_organization_ref: str | None = None,
        status: str = "active",
        include_position: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Location resource.

        Args:
            location_id: Location ID (generates UUID if None)
            name: Location name (generates random if None)
            location_type: Location type code (random if None)
            physical_type: Physical type code (random if None)
            part_of_ref: Reference to parent location (e.g., "Location/parent-id")
            managing_organization_ref: Reference to managing organization
            status: Location status (active, suspended, inactive)
            include_position: Whether to include lat/long position

        Returns:
            Location FHIR resource
        """
        if location_id is None:
            location_id = self._generate_id()

        # Select physical type
        if physical_type is None:
            phys_type_coding = self.faker.random_element(self.PHYSICAL_TYPES)
        else:
            phys_type_coding = next(
                (t for t in self.PHYSICAL_TYPES if t["code"] == physical_type),
                self.PHYSICAL_TYPES[0],
            )

        # Generate location name based on physical type
        if name is None:
            templates = self.NAME_TEMPLATES.get(phys_type_coding["code"], ["{city} Location"])
            template = self.faker.random_element(templates)
            name = template.format(
                city=self.faker.city(),
                name=self.faker.last_name(),
                number=self.faker.random_int(min=100, max=999),
            )

        # Select location type
        if location_type is None:
            type_coding = self.faker.random_element(self.LOCATION_TYPES)
        else:
            type_coding = next(
                (t for t in self.LOCATION_TYPES if t["code"] == location_type),
                self.LOCATION_TYPES[0],
            )

        location: dict[str, Any] = {
            "resourceType": "Location",
            "id": location_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/location-ids",
                    value=f"LOC-{self.faker.numerify('######')}",
                ),
            ],
            "status": status,
            "name": name,
            "mode": "instance",
            "type": [
                {
                    "coding": [type_coding],
                    "text": type_coding["display"],
                }
            ],
            "physicalType": {
                "coding": [phys_type_coding],
                "text": phys_type_coding["display"],
            },
            "telecom": [
                self._generate_contact_point("phone", use="work"),
            ],
            "address": self._generate_address(use="work"),
        }

        # Add operational status (mostly for rooms/beds)
        if phys_type_coding["code"] in ["ro", "bd"]:
            op_status = self.faker.random_element(self.OPERATIONAL_STATUS)
            location["operationalStatus"] = {
                "system": op_status["system"],
                "code": op_status["code"],
                "display": op_status["display"],
            }

        # Add position if requested
        if include_position:
            location["position"] = {
                "longitude": float(self.faker.longitude()),
                "latitude": float(self.faker.latitude()),
            }

        # Add managing organization reference
        if managing_organization_ref:
            location["managingOrganization"] = {"reference": managing_organization_ref}

        # Add parent location reference
        if part_of_ref:
            location["partOf"] = {"reference": part_of_ref}

        return location

    def generate_hierarchy(
        self,
        managing_organization_ref: str | None = None,
        depth: int = 3,
        base_city: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generate a location hierarchy.

        Creates a chain of locations linked via partOf from root to leaf.

        Args:
            managing_organization_ref: Reference to managing organization
            depth: Number of levels in hierarchy (1-6, maps to Site→Building→Wing→Ward→Room→Bed)
            base_city: City name to use for consistent naming

        Returns:
            List of Location resources, from root (no partOf) to leaf (deepest nesting)
        """
        depth = max(1, min(depth, len(self.HIERARCHY_ORDER)))
        physical_types = self.HIERARCHY_ORDER[:depth]

        if base_city is None:
            base_city = self.faker.city()

        locations: list[dict[str, Any]] = []
        parent_ref: str | None = None

        for i, phys_type in enumerate(physical_types):
            # Only top-level gets the full address and position
            include_position = i == 0

            # Generate name with consistent city for site level
            name = None
            if phys_type == "si":
                name = f"{base_city} Medical Center"

            location = self.generate(
                physical_type=phys_type,
                name=name,
                part_of_ref=parent_ref,
                managing_organization_ref=managing_organization_ref if i == 0 else None,
                include_position=include_position,
            )

            locations.append(location)
            parent_ref = f"Location/{location['id']}"

        return locations
