"""Evidence resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EvidenceGenerator(FHIRResourceGenerator):
    """Generator for FHIR Evidence resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    EVIDENCE_TOPICS = [
        {
            "system": "http://snomed.info/sct",
            "code": "73211009",
            "display": "Diabetes mellitus",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "38341003",
            "display": "Hypertensive disorder",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "195967001",
            "display": "Asthma",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "13645005",
            "display": "Chronic obstructive lung disease",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        evidence_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        topic: list[dict[str, Any]] | None = None,
        exposure_background_reference: str | None = None,
        exposure_variant_references: list[str] | None = None,
        outcome_references: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Evidence resource.

        Args:
            evidence_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            topic: Topics covered by the evidence
            exposure_background_reference: Reference to background exposure
            exposure_variant_references: References to variant exposures
            outcome_references: References to outcomes

        Returns:
            Evidence FHIR resource
        """
        if evidence_id is None:
            evidence_id = self._generate_id()

        if name is None:
            name = f"Evidence{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"Evidence for {self.faker.word().title()} Treatment"

        evidence: dict[str, Any] = {
            "resourceType": "Evidence",
            "id": evidence_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/Evidence/{evidence_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            evidence["description"] = description
        else:
            evidence["description"] = f"Research evidence for {title.lower()}"

        # Add topic
        if topic:
            evidence["topic"] = topic
        else:
            t = self.faker.random_element(self.EVIDENCE_TOPICS)
            evidence["topic"] = [{"coding": [t], "text": t["display"]}]

        # Add exposure background
        if exposure_background_reference:
            evidence["exposureBackground"] = {"reference": exposure_background_reference}
        else:
            evidence["exposureBackground"] = {"reference": f"EvidenceVariable/{self._generate_id()}"}

        # Add exposure variants
        if exposure_variant_references:
            evidence["exposureVariant"] = [{"reference": ref} for ref in exposure_variant_references]

        # Add outcomes
        if outcome_references:
            evidence["outcome"] = [{"reference": ref} for ref in outcome_references]

        return evidence
