"""ResearchElementDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ResearchElementDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ResearchElementDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    ELEMENT_TYPES = ["population", "exposure", "outcome"]

    VARIABLE_TYPES = ["dichotomous", "continuous", "descriptive"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        element_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        element_type: str | None = None,
        variable_type: str | None = None,
        characteristics: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ResearchElementDefinition resource.

        Args:
            element_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            element_type: Type of element (population, exposure, outcome)
            variable_type: Type of variable
            characteristics: Element characteristics

        Returns:
            ResearchElementDefinition FHIR resource
        """
        if element_id is None:
            element_id = self._generate_id()

        if name is None:
            name = f"ResearchElement{self.faker.random_number(digits=4, fix_len=True)}"

        if element_type is None:
            element_type = self.faker.random_element(self.ELEMENT_TYPES)

        if title is None:
            title = f"Research Element: {element_type.title()} Definition"

        if variable_type is None:
            variable_type = self.faker.random_element(self.VARIABLE_TYPES)

        research_element: dict[str, Any] = {
            "resourceType": "ResearchElementDefinition",
            "id": element_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/ResearchElementDefinition/{element_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "type": element_type,
            "variableType": variable_type,
        }

        if description:
            research_element["description"] = description
        else:
            research_element["description"] = f"Definition of {element_type} for research study"

        # Add subject type
        research_element["subjectCodeableConcept"] = {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/resource-types",
                    "code": "Patient",
                    "display": "Patient",
                }
            ]
        }

        # Add characteristics
        if characteristics:
            research_element["characteristic"] = characteristics
        else:
            research_element["characteristic"] = self._generate_characteristics(element_type)

        return research_element

    def _generate_characteristics(self, element_type: str) -> list[dict[str, Any]]:
        """Generate element characteristics."""
        if element_type == "population":
            return [
                {
                    "definitionCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "133936004",
                                "display": "Adult",
                            }
                        ],
                        "text": "Adult population",
                    },
                    "exclude": False,
                }
            ]
        elif element_type == "exposure":
            return [
                {
                    "definitionCodeableConcept": {"text": "Treatment intervention"},
                    "exclude": False,
                }
            ]
        else:  # outcome
            return [
                {
                    "definitionCodeableConcept": {"text": "Primary outcome measure"},
                    "exclude": False,
                }
            ]

    def generate_population_element(
        self,
        description: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a population ResearchElementDefinition.

        Args:
            description: Population description

        Returns:
            ResearchElementDefinition FHIR resource
        """
        characteristics = [
            {
                "definitionCodeableConcept": {"text": description},
                "exclude": False,
            }
        ]

        return self.generate(
            title=f"Population: {description}",
            element_type="population",
            characteristics=characteristics,
            **kwargs,
        )
