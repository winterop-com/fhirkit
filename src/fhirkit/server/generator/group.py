"""Group resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class GroupGenerator(FHIRResourceGenerator):
    """Generator for FHIR Group resources."""

    # Group types
    GROUP_TYPES = ["person", "animal", "practitioner", "device", "medication", "substance"]

    # Group codes
    GROUP_CODES = [
        {"code": "diabetes-cohort", "display": "Diabetes Patient Cohort", "system": "http://example.org/group-types"},
        {
            "code": "hypertension-cohort",
            "display": "Hypertension Patient Cohort",
            "system": "http://example.org/group-types",
        },
        {
            "code": "research-study",
            "display": "Research Study Participants",
            "system": "http://example.org/group-types",
        },
        {"code": "care-team", "display": "Care Team Members", "system": "http://example.org/group-types"},
        {
            "code": "measure-population",
            "display": "Quality Measure Population",
            "system": "http://example.org/group-types",
        },
    ]

    # Characteristic codes
    CHARACTERISTIC_CODES = [
        {"code": "age", "display": "Age", "system": "http://example.org/characteristics"},
        {"code": "gender", "display": "Gender", "system": "http://example.org/characteristics"},
        {"code": "diagnosis", "display": "Diagnosis", "system": "http://example.org/characteristics"},
        {"code": "medication", "display": "Medication", "system": "http://example.org/characteristics"},
    ]

    # Name patterns
    NAME_PATTERNS = [
        "{condition} Patient Cohort",
        "{condition} Study Group",
        "{department} Care Team",
        "Quality Measure: {measure}",
        "{condition} Registry",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        group_id: str | None = None,
        name: str | None = None,
        group_type: str = "person",
        actual: bool = True,
        member_refs: list[str] | None = None,
        managing_entity_ref: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Group resource.

        Args:
            group_id: Group ID (generates UUID if None)
            name: Group name (random if None)
            group_type: Type of group members (person, animal, practitioner, etc.)
            actual: True for actual group, False for definitional
            member_refs: List of member references (e.g., ["Patient/123", "Patient/456"])
            managing_entity_ref: Reference to managing Organization

        Returns:
            Group FHIR resource
        """
        if group_id is None:
            group_id = self._generate_id()

        # Generate name
        if name is None:
            pattern = self.faker.random_element(self.NAME_PATTERNS)
            name = pattern.format(
                condition=self.faker.random_element(["Diabetes", "Hypertension", "COPD", "Asthma", "Heart Failure"]),
                department=self.faker.random_element(["Cardiology", "Oncology", "Primary Care", "Emergency"]),
                measure=self.faker.random_element(["HbA1c Control", "Blood Pressure", "Preventive Screening"]),
            )

        group_code = self.faker.random_element(self.GROUP_CODES)

        group: dict[str, Any] = {
            "resourceType": "Group",
            "id": group_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/group-ids",
                    value=f"GRP-{self.faker.numerify('######')}",
                ),
            ],
            "active": True,
            "type": group_type,
            "actual": actual,
            "code": {
                "coding": [group_code],
                "text": group_code["display"],
            },
            "name": name,
            "quantity": len(member_refs) if member_refs else self.faker.random_int(min=10, max=500),
        }

        if managing_entity_ref:
            group["managingEntity"] = {"reference": managing_entity_ref}

        # Add characteristics for definitional groups
        if not actual:
            char_code = self.faker.random_element(self.CHARACTERISTIC_CODES)
            group["characteristic"] = [
                {
                    "code": {"coding": [char_code], "text": char_code["display"]},
                    "valueBoolean": True,
                    "exclude": False,
                }
            ]

        # Add members for actual groups
        if actual and member_refs:
            group["member"] = [
                {
                    "entity": {"reference": ref},
                    "period": {"start": self._generate_date()},
                }
                for ref in member_refs
            ]

        return group
