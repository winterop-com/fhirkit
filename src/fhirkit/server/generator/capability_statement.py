"""CapabilityStatement resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CapabilityStatementGenerator(FHIRResourceGenerator):
    """Generator for FHIR CapabilityStatement resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    FHIR_VERSIONS = ["4.0.1", "4.0.0", "3.0.2"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        statement_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        kind: str = "instance",
        fhir_version: str = "4.0.1",
        format_list: list[str] | None = None,
        rest: list[dict[str, Any]] | None = None,
        messaging: list[dict[str, Any]] | None = None,
        document: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CapabilityStatement resource.

        Args:
            statement_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            kind: instance | capability | requirements
            fhir_version: FHIR version supported
            format_list: Supported formats
            rest: REST capabilities
            messaging: Messaging capabilities
            document: Document capabilities

        Returns:
            CapabilityStatement FHIR resource
        """
        if statement_id is None:
            statement_id = self._generate_id()

        if name is None:
            name = f"CapabilityStatement{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.company()} FHIR Server"

        capability_statement: dict[str, Any] = {
            "resourceType": "CapabilityStatement",
            "id": statement_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/CapabilityStatement/{statement_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "kind": kind,
            "fhirVersion": fhir_version,
        }

        if description:
            capability_statement["description"] = description
        else:
            capability_statement["description"] = f"Capability statement for {title}"

        # Add software info for instance kind
        if kind == "instance":
            major = self.faker.random_int(1, 5)
            minor = self.faker.random_int(0, 9)
            patch = self.faker.random_int(0, 99)
            capability_statement["software"] = {
                "name": f"{self.faker.word().title()} FHIR Server",
                "version": f"{major}.{minor}.{patch}",
            }
            capability_statement["implementation"] = {
                "description": "FHIR Server implementation",
                "url": f"http://{self.faker.domain_name()}/fhir",
            }

        # Add format
        if format_list:
            capability_statement["format"] = format_list
        else:
            capability_statement["format"] = ["application/fhir+json", "application/fhir+xml"]

        # Add REST capabilities
        if rest:
            capability_statement["rest"] = rest
        else:
            capability_statement["rest"] = self._generate_rest()

        # Add messaging if provided
        if messaging:
            capability_statement["messaging"] = messaging

        # Add document if provided
        if document:
            capability_statement["document"] = document

        return capability_statement

    def _generate_rest(self) -> list[dict[str, Any]]:
        """Generate REST capabilities."""
        common_resources = [
            "Patient",
            "Practitioner",
            "Organization",
            "Encounter",
            "Observation",
            "Condition",
            "Medication",
            "MedicationRequest",
        ]

        resources = []
        for resource_type in common_resources:
            resources.append(
                {
                    "type": resource_type,
                    "interaction": [
                        {"code": "read"},
                        {"code": "vread"},
                        {"code": "search-type"},
                        {"code": "create"},
                        {"code": "update"},
                        {"code": "delete"},
                    ],
                    "versioning": "versioned",
                    "readHistory": True,
                    "updateCreate": True,
                    "conditionalCreate": True,
                    "conditionalRead": "full-support",
                    "conditionalUpdate": True,
                    "conditionalDelete": "single",
                }
            )

        return [
            {
                "mode": "server",
                "documentation": "RESTful FHIR server",
                "security": {
                    "cors": True,
                    "service": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/restful-security-service",
                                    "code": "SMART-on-FHIR",
                                }
                            ]
                        }
                    ],
                },
                "resource": resources,
                "interaction": [
                    {"code": "transaction"},
                    {"code": "batch"},
                    {"code": "search-system"},
                ],
            }
        ]

    def generate_minimal(self, **kwargs: Any) -> dict[str, Any]:
        """Generate a minimal capability statement.

        Returns:
            CapabilityStatement FHIR resource
        """
        rest = [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                    }
                ],
            }
        ]

        return self.generate(
            title="Minimal FHIR Server",
            rest=rest,
            **kwargs,
        )
