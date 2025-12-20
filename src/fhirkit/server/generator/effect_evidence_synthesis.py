"""EffectEvidenceSynthesis resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EffectEvidenceSynthesisGenerator(FHIRResourceGenerator):
    """Generator for FHIR EffectEvidenceSynthesis resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    STUDY_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/synthesis-type",
            "code": "std-MA",
            "display": "summary data meta-analysis",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/synthesis-type",
            "code": "IPD-MA",
            "display": "individual patient data meta-analysis",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/synthesis-type",
            "code": "indirect-NMA",
            "display": "indirect network meta-analysis",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        synthesis_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        population_reference: str | None = None,
        exposure_reference: str | None = None,
        comparator_reference: str | None = None,
        outcome_reference: str | None = None,
        study_type: dict[str, Any] | None = None,
        effect_estimate: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EffectEvidenceSynthesis resource.

        Args:
            synthesis_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            population_reference: Reference to population EvidenceVariable
            exposure_reference: Reference to exposure EvidenceVariable
            comparator_reference: Reference to comparator EvidenceVariable
            outcome_reference: Reference to outcome EvidenceVariable
            study_type: Type of study
            effect_estimate: Effect estimates

        Returns:
            EffectEvidenceSynthesis FHIR resource
        """
        if synthesis_id is None:
            synthesis_id = self._generate_id()

        if name is None:
            name = f"EffectSynthesis{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"Effect of {self.faker.word().title()} Treatment"

        synthesis: dict[str, Any] = {
            "resourceType": "EffectEvidenceSynthesis",
            "id": synthesis_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/EffectEvidenceSynthesis/{synthesis_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            synthesis["description"] = description
        else:
            synthesis["description"] = f"Synthesis of effect evidence for {title.lower()}"

        # Add study type
        if study_type:
            synthesis["studyType"] = {"coding": [study_type]}
        else:
            st = self.faker.random_element(self.STUDY_TYPES)
            synthesis["studyType"] = {"coding": [st], "text": st["display"]}

        # Add population
        if population_reference:
            synthesis["population"] = {"reference": population_reference}
        else:
            synthesis["population"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add exposure
        if exposure_reference:
            synthesis["exposure"] = {"reference": exposure_reference}
        else:
            synthesis["exposure"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add comparator
        if comparator_reference:
            synthesis["comparator"] = {"reference": comparator_reference}
        else:
            synthesis["comparator"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add outcome
        if outcome_reference:
            synthesis["outcome"] = {"reference": outcome_reference}
        else:
            synthesis["outcome"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add effect estimate
        if effect_estimate:
            synthesis["effectEstimate"] = effect_estimate
        else:
            synthesis["effectEstimate"] = self._generate_effect_estimate()

        return synthesis

    def _generate_effect_estimate(self) -> list[dict[str, Any]]:
        """Generate effect estimate."""
        return [
            {
                "description": "Relative risk reduction",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/effect-estimate-type",
                            "code": "relative-RR",
                            "display": "relative risk",
                        }
                    ]
                },
                "value": round(self.faker.pyfloat(min_value=0.5, max_value=1.5), 2),
                "unitOfMeasure": {
                    "coding": [
                        {
                            "system": "http://unitsofmeasure.org",
                            "code": "1",
                            "display": "1",
                        }
                    ]
                },
            }
        ]
