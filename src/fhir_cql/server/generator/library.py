"""Library resource generator."""

import base64
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class LibraryGenerator(FHIRResourceGenerator):
    """Generator for FHIR Library resources (CQL libraries)."""

    # Library types
    LIBRARY_TYPES = [
        {"code": "logic-library", "display": "Logic Library", "system": "http://terminology.hl7.org/CodeSystem/library-type"},
        {"code": "model-definition", "display": "Model Definition", "system": "http://terminology.hl7.org/CodeSystem/library-type"},
        {"code": "asset-collection", "display": "Asset Collection", "system": "http://terminology.hl7.org/CodeSystem/library-type"},
        {"code": "module-definition", "display": "Module Definition", "system": "http://terminology.hl7.org/CodeSystem/library-type"},
    ]

    # Common library name patterns
    NAME_PATTERNS = [
        "{condition}Logic",
        "{condition}Measures",
        "Common{category}",
        "{category}Helpers",
        "FHIR{category}",
    ]

    # Clinical topics
    TOPICS = [
        {"code": "diabetes", "display": "Diabetes", "system": "http://example.org/topics"},
        {"code": "cardiovascular", "display": "Cardiovascular", "system": "http://example.org/topics"},
        {"code": "preventive-care", "display": "Preventive Care", "system": "http://example.org/topics"},
        {"code": "mental-health", "display": "Mental Health", "system": "http://example.org/topics"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        library_id: str | None = None,
        name: str | None = None,
        version: str = "1.0.0",
        status: str = "active",
        library_type: str = "logic-library",
        include_cql: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Library resource.

        Args:
            library_id: Library ID (generates UUID if None)
            name: Library name (random if None)
            version: Library version
            status: Publication status (draft, active, retired, unknown)
            library_type: Library type code
            include_cql: Whether to include sample CQL content

        Returns:
            Library FHIR resource
        """
        if library_id is None:
            library_id = self._generate_id()

        # Generate name
        if name is None:
            pattern = self.faker.random_element(self.NAME_PATTERNS)
            name = pattern.format(
                condition=self.faker.random_element(["Diabetes", "Hypertension", "Asthma", "COPD"]),
                category=self.faker.random_element(["Helpers", "Quality", "Clinical", "Screening"]),
            )

        # Select library type
        type_coding = next(
            (t for t in self.LIBRARY_TYPES if t["code"] == library_type),
            self.LIBRARY_TYPES[0],
        )

        topic = self.faker.random_element(self.TOPICS)

        library: dict[str, Any] = {
            "resourceType": "Library",
            "id": library_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/Library/{name}",
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/library-ids",
                    value=f"LIB-{self.faker.numerify('######')}",
                ),
            ],
            "version": version,
            "name": name,
            "title": f"{name} Library",
            "status": status,
            "experimental": self.faker.boolean(chance_of_getting_true=20),
            "type": {"coding": [type_coding], "text": type_coding["display"]},
            "date": self._generate_date(),
            "publisher": self.faker.company(),
            "description": f"CQL library for {topic['display'].lower()} quality measures and clinical decision support.",
            "topic": [{"coding": [topic], "text": topic["display"]}],
            "relatedArtifact": [
                {
                    "type": "depends-on",
                    "resource": "http://hl7.org/fhir/Library/FHIRHelpers",
                }
            ],
            "parameter": [
                {
                    "name": "Patient",
                    "use": "in",
                    "type": "Patient",
                },
                {
                    "name": "Measurement Period",
                    "use": "in",
                    "type": "Period",
                },
            ],
            "dataRequirement": [
                {
                    "type": "Patient",
                },
                {
                    "type": "Condition",
                },
                {
                    "type": "Observation",
                },
            ],
        }

        # Add CQL content if requested
        if include_cql:
            cql_content = f"""library {name} version '{version}'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Initial Population":
  exists([Condition])

define "Denominator":
  "Initial Population"

define "Numerator":
  exists([Observation])
"""
            library["content"] = [
                {
                    "contentType": "text/cql",
                    "data": base64.b64encode(cql_content.encode()).decode(),
                }
            ]

        return library
