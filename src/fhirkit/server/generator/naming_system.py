"""NamingSystem resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class NamingSystemGenerator(FHIRResourceGenerator):
    """Generator for FHIR NamingSystem resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    KIND_CODES = ["codesystem", "identifier", "root"]

    IDENTIFIER_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "MR",
            "display": "Medical record number",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "SS",
            "display": "Social Security Number",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "DL",
            "display": "Driver's license number",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "PPN",
            "display": "Passport number",
        },
    ]

    UNIQUE_ID_TYPES = ["oid", "uuid", "uri", "other"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        naming_system_id: str | None = None,
        name: str | None = None,
        status: str = "active",
        kind: str | None = None,
        description: str | None = None,
        jurisdiction: list[dict[str, Any]] | None = None,
        unique_ids: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a NamingSystem resource.

        Args:
            naming_system_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            status: Publication status
            kind: codesystem | identifier | root
            description: Natural language description
            jurisdiction: Jurisdiction of use
            unique_ids: Unique identifier definitions

        Returns:
            NamingSystem FHIR resource
        """
        if naming_system_id is None:
            naming_system_id = self._generate_id()

        if name is None:
            name = f"NamingSystem{self.faker.random_number(digits=4, fix_len=True)}"

        if kind is None:
            kind = self.faker.random_element(self.KIND_CODES)

        naming_system: dict[str, Any] = {
            "resourceType": "NamingSystem",
            "id": naming_system_id,
            "meta": self._generate_meta(),
            "name": name,
            "status": status,
            "kind": kind,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "responsible": self.faker.name(),
        }

        if description:
            naming_system["description"] = description
        else:
            naming_system["description"] = f"Naming system for {kind} identifiers"

        # Add type for identifier kind
        if kind == "identifier":
            id_type = self.faker.random_element(self.IDENTIFIER_TYPES)
            naming_system["type"] = {"coding": [id_type], "text": id_type["display"]}

        # Add jurisdiction
        if jurisdiction:
            naming_system["jurisdiction"] = jurisdiction
        else:
            naming_system["jurisdiction"] = [
                {
                    "coding": [
                        {
                            "system": "urn:iso:std:iso:3166",
                            "code": "US",
                            "display": "United States of America",
                        }
                    ]
                }
            ]

        # Add unique IDs
        if unique_ids:
            naming_system["uniqueId"] = unique_ids
        else:
            naming_system["uniqueId"] = self._generate_unique_ids()

        return naming_system

    def _generate_unique_ids(self) -> list[dict[str, Any]]:
        """Generate unique identifier definitions."""
        unique_ids = []

        # Add OID
        unique_ids.append(
            {
                "type": "oid",
                "value": f"urn:oid:2.16.840.1.113883.4.{self.faker.random_int(1, 999)}",
                "preferred": True,
            }
        )

        # Add URI
        if self.faker.boolean(chance_of_getting_true=70):
            unique_ids.append(
                {
                    "type": "uri",
                    "value": f"http://example.org/naming-system/{self.faker.uuid4()}",
                    "preferred": False,
                }
            )

        return unique_ids

    def generate_identifier_system(
        self,
        name: str,
        oid: str | None = None,
        uri: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a NamingSystem for an identifier system.

        Args:
            name: Name of the identifier system
            oid: OID for the system
            uri: URI for the system

        Returns:
            NamingSystem FHIR resource
        """
        unique_ids = []

        if oid:
            unique_ids.append({"type": "oid", "value": oid, "preferred": True})

        if uri:
            unique_ids.append({"type": "uri", "value": uri, "preferred": not oid})

        return self.generate(
            name=name,
            kind="identifier",
            unique_ids=unique_ids if unique_ids else None,
            **kwargs,
        )
