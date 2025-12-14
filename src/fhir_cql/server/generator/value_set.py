"""ValueSet resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ValueSetGenerator(FHIRResourceGenerator):
    """Generator for FHIR ValueSet resources."""

    # Common value set templates
    VALUE_SET_TEMPLATES = [
        {
            "name": "ConditionSeverity",
            "title": "Condition Severity",
            "description": "Severity levels for clinical conditions",
            "concepts": [
                {"code": "24484000", "display": "Severe", "system": "http://snomed.info/sct"},
                {"code": "6736007", "display": "Moderate", "system": "http://snomed.info/sct"},
                {"code": "255604002", "display": "Mild", "system": "http://snomed.info/sct"},
            ],
        },
        {
            "name": "ObservationStatus",
            "title": "Observation Status",
            "description": "Status codes for observations",
            "concepts": [
                {"code": "registered", "display": "Registered", "system": "http://hl7.org/fhir/observation-status"},
                {"code": "preliminary", "display": "Preliminary", "system": "http://hl7.org/fhir/observation-status"},
                {"code": "final", "display": "Final", "system": "http://hl7.org/fhir/observation-status"},
                {"code": "amended", "display": "Amended", "system": "http://hl7.org/fhir/observation-status"},
            ],
        },
        {
            "name": "AdministrativeGender",
            "title": "Administrative Gender",
            "description": "Gender codes for administrative purposes",
            "concepts": [
                {"code": "male", "display": "Male", "system": "http://hl7.org/fhir/administrative-gender"},
                {"code": "female", "display": "Female", "system": "http://hl7.org/fhir/administrative-gender"},
                {"code": "other", "display": "Other", "system": "http://hl7.org/fhir/administrative-gender"},
                {"code": "unknown", "display": "Unknown", "system": "http://hl7.org/fhir/administrative-gender"},
            ],
        },
        {
            "name": "EncounterType",
            "title": "Encounter Type",
            "description": "Types of clinical encounters",
            "concepts": [
                {"code": "AMB", "display": "Ambulatory", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
                {"code": "EMER", "display": "Emergency", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
                {"code": "IMP", "display": "Inpatient", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
                {
                    "code": "OBSENC",
                    "display": "Observation",
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                },
            ],
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        value_set_id: str | None = None,
        name: str | None = None,
        version: str = "1.0.0",
        status: str = "active",
        template: dict | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ValueSet resource.

        Args:
            value_set_id: ValueSet ID (generates UUID if None)
            name: ValueSet name (random template if None)
            version: ValueSet version
            status: Publication status (draft, active, retired, unknown)
            template: Custom template with name, title, description, concepts

        Returns:
            ValueSet FHIR resource
        """
        if value_set_id is None:
            value_set_id = self._generate_id()

        # Use provided template or select random one
        if template is None:
            template = self.faker.random_element(self.VALUE_SET_TEMPLATES)

        if name is None:
            name = template["name"]

        # Group concepts by system
        systems: dict[str, list] = {}
        for concept in template["concepts"]:
            system = concept["system"]
            if system not in systems:
                systems[system] = []
            systems[system].append({"code": concept["code"], "display": concept["display"]})

        value_set: dict[str, Any] = {
            "resourceType": "ValueSet",
            "id": value_set_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/ValueSet/{name}",
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/valueset-ids",
                    value=f"VS-{self.faker.numerify('######')}",
                ),
            ],
            "version": version,
            "name": name,
            "title": template["title"],
            "status": status,
            "experimental": False,
            "date": self._generate_date(),
            "publisher": self.faker.company(),
            "description": template["description"],
            "compose": {
                "include": [
                    {
                        "system": system,
                        "concept": concepts,
                    }
                    for system, concepts in systems.items()
                ]
            },
        }

        return value_set
