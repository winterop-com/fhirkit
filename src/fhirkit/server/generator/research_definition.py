"""ResearchDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ResearchDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ResearchDefinition resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        purpose: str | None = None,
        subject_reference: str | None = None,
        population_reference: str | None = None,
        exposure_reference: str | None = None,
        exposure_alternative_reference: str | None = None,
        outcome_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ResearchDefinition resource.

        Args:
            definition_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            purpose: Purpose of the research definition
            subject_reference: Reference to subject group
            population_reference: Reference to population
            exposure_reference: Reference to exposure
            exposure_alternative_reference: Reference to alternative exposure
            outcome_reference: Reference to outcome

        Returns:
            ResearchDefinition FHIR resource
        """
        if definition_id is None:
            definition_id = self._generate_id()

        if name is None:
            name = f"ResearchDefinition{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"Research Protocol: {self.faker.word().title()} Study"

        research_definition: dict[str, Any] = {
            "resourceType": "ResearchDefinition",
            "id": definition_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/ResearchDefinition/{definition_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            research_definition["description"] = description
        else:
            research_definition["description"] = f"Research definition for studying {self.faker.word()} effects"

        if purpose:
            research_definition["purpose"] = purpose
        else:
            research_definition["purpose"] = "To evaluate the effectiveness of the intervention"

        # Add subject type
        if subject_reference:
            research_definition["subjectReference"] = {"reference": subject_reference}
        else:
            research_definition["subjectCodeableConcept"] = {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/resource-types",
                        "code": "Patient",
                        "display": "Patient",
                    }
                ]
            }

        # Add population
        if population_reference:
            research_definition["population"] = {"reference": population_reference}
        else:
            research_definition["population"] = {"reference": f"Group/{self._generate_id()}"}

        # Add exposure
        if exposure_reference:
            research_definition["exposure"] = {"reference": exposure_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            research_definition["exposure"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add exposure alternative
        if exposure_alternative_reference:
            research_definition["exposureAlternative"] = {"reference": exposure_alternative_reference}
        elif self.faker.boolean(chance_of_getting_true=50):
            research_definition["exposureAlternative"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add outcome
        if outcome_reference:
            research_definition["outcome"] = {"reference": outcome_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            research_definition["outcome"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        return research_definition
