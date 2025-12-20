"""EvidenceVariable resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EvidenceVariableGenerator(FHIRResourceGenerator):
    """Generator for FHIR EvidenceVariable resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    VARIABLE_TYPES = ["dichotomous", "continuous", "descriptive"]

    CHARACTERISTIC_TYPES = [
        {
            "system": "http://snomed.info/sct",
            "code": "248153007",
            "display": "Male",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "248152002",
            "display": "Female",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "133936004",
            "display": "Adult",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "410599005",
            "display": "Deceased",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        variable_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        variable_type: str | None = None,
        characteristics: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EvidenceVariable resource.

        Args:
            variable_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            variable_type: Type of variable
            characteristics: Variable characteristics

        Returns:
            EvidenceVariable FHIR resource
        """
        if variable_id is None:
            variable_id = self._generate_id()

        if name is None:
            name = f"EvidenceVariable{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"{self.faker.word().title()} Population Variable"

        if variable_type is None:
            variable_type = self.faker.random_element(self.VARIABLE_TYPES)

        evidence_variable: dict[str, Any] = {
            "resourceType": "EvidenceVariable",
            "id": variable_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/EvidenceVariable/{variable_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "type": variable_type,
        }

        if description:
            evidence_variable["description"] = description
        else:
            evidence_variable["description"] = f"Definition of {title.lower()}"

        # Add characteristics
        if characteristics:
            evidence_variable["characteristic"] = characteristics
        else:
            evidence_variable["characteristic"] = self._generate_characteristics()

        return evidence_variable

    def _generate_characteristics(self) -> list[dict[str, Any]]:
        """Generate variable characteristics."""
        char_type = self.faker.random_element(self.CHARACTERISTIC_TYPES)

        return [
            {
                "description": f"Characteristic: {char_type['display']}",
                "definitionCodeableConcept": {
                    "coding": [char_type],
                    "text": char_type["display"],
                },
                "exclude": False,
            }
        ]

    def generate_population_variable(
        self,
        population_description: str,
        age_min: int | None = None,
        age_max: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EvidenceVariable for a population.

        Args:
            population_description: Description of the population
            age_min: Minimum age
            age_max: Maximum age

        Returns:
            EvidenceVariable FHIR resource
        """
        characteristics = [
            {
                "description": population_description,
                "exclude": False,
            }
        ]

        if age_min is not None or age_max is not None:
            age_char: dict[str, Any] = {
                "description": "Age range",
                "exclude": False,
            }
            if age_min is not None and age_max is not None:
                age_char["definitionCodeableConcept"] = {"text": f"Age {age_min}-{age_max} years"}
            characteristics.append(age_char)

        return self.generate(
            title=f"Population: {population_description}",
            variable_type="dichotomous",
            characteristics=characteristics,
            **kwargs,
        )
