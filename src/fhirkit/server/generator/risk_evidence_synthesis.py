"""RiskEvidenceSynthesis resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class RiskEvidenceSynthesisGenerator(FHIRResourceGenerator):
    """Generator for FHIR RiskEvidenceSynthesis resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

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
        outcome_reference: str | None = None,
        risk_estimate: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a RiskEvidenceSynthesis resource.

        Args:
            synthesis_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            population_reference: Reference to population EvidenceVariable
            exposure_reference: Reference to exposure EvidenceVariable
            outcome_reference: Reference to outcome EvidenceVariable
            risk_estimate: Risk estimates

        Returns:
            RiskEvidenceSynthesis FHIR resource
        """
        if synthesis_id is None:
            synthesis_id = self._generate_id()

        if name is None:
            name = f"RiskSynthesis{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"Risk of {self.faker.word().title()} Outcome"

        synthesis: dict[str, Any] = {
            "resourceType": "RiskEvidenceSynthesis",
            "id": synthesis_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/RiskEvidenceSynthesis/{synthesis_id}",
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
            synthesis["description"] = f"Synthesis of risk evidence for {title.lower()}"

        # Add population
        if population_reference:
            synthesis["population"] = {"reference": population_reference}
        else:
            synthesis["population"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add exposure
        if exposure_reference:
            synthesis["exposure"] = {"reference": exposure_reference}

        # Add outcome
        if outcome_reference:
            synthesis["outcome"] = {"reference": outcome_reference}
        else:
            synthesis["outcome"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add risk estimate
        if risk_estimate:
            synthesis["riskEstimate"] = risk_estimate
        else:
            synthesis["riskEstimate"] = self._generate_risk_estimate()

        return synthesis

    def _generate_risk_estimate(self) -> dict[str, Any]:
        """Generate risk estimate."""
        denominator = self.faker.random_int(100, 10000)
        numerator = self.faker.random_int(1, denominator // 10)

        return {
            "description": "Estimated risk",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/risk-estimate-type",
                        "code": "proportion",
                        "display": "proportion",
                    }
                ]
            },
            "value": round(numerator / denominator, 4),
            "unitOfMeasure": {
                "coding": [
                    {
                        "system": "http://unitsofmeasure.org",
                        "code": "1",
                        "display": "1",
                    }
                ]
            },
            "denominatorCount": denominator,
            "numeratorCount": numerator,
        }
