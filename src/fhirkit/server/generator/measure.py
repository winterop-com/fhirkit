"""Measure resource generator."""

from datetime import date, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    MEASURE_EXAMPLES,
    MEASURE_IMPROVEMENT_NOTATION,
    MEASURE_POPULATION_CODES,
    MEASURE_SCORING_CODES,
    MEASURE_STATUS_CODES,
    MEASURE_TYPE_CODES,
)


class MeasureGenerator(FHIRResourceGenerator):
    """Generator for FHIR Measure resources.

    Measure resources define quality measures including eCQMs (electronic
    Clinical Quality Measures) with population criteria and scoring methods.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None) -> None:
        """Initialize the generator.

        Args:
            faker: Faker instance to use
            seed: Optional random seed for reproducibility
        """
        super().__init__(faker, seed)

    def generate(
        self,
        *,
        measure_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str | None = None,
        library_ref: str | None = None,
        scoring: str | None = None,
        measure_type: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Measure resource.

        Args:
            measure_id: Optional specific ID
            name: Measure name (machine-friendly)
            title: Human-readable title
            status: draft | active | retired
            library_ref: Reference to associated Library
            scoring: proportion | ratio | continuous-variable | cohort
            measure_type: process | outcome | structure | etc.

        Returns:
            A FHIR Measure resource
        """
        # Use example measure if not specified
        example = self.faker.random_element(MEASURE_EXAMPLES)

        resource_id = measure_id or self._generate_id()
        measure_name = name or example["name"]
        measure_title = title or example["title"]
        measure_status = status or self.faker.random_element(MEASURE_STATUS_CODES)

        # Determine scoring and type
        scoring_code = scoring or example.get("scoring", "proportion")
        type_code = measure_type or example.get("type", "process")

        # Get code details
        scoring_info = next(
            (s for s in MEASURE_SCORING_CODES if s["code"] == scoring_code),
            MEASURE_SCORING_CODES[0],
        )
        type_info = next(
            (t for t in MEASURE_TYPE_CODES if t["code"] == type_code),
            MEASURE_TYPE_CODES[0],
        )
        improvement = self.faker.random_element(MEASURE_IMPROVEMENT_NOTATION)

        # Build resource
        resource: dict[str, Any] = {
            "resourceType": "Measure",
            "id": resource_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/Measure/{measure_name}",
            "identifier": [
                {
                    "system": "http://example.org/fhir/measure-identifier",
                    "value": resource_id,
                }
            ],
            "version": "1.0.0",
            "name": measure_name,
            "title": measure_title,
            "status": measure_status,
            "experimental": measure_status == "draft",
            "date": self._generate_datetime(),
            "publisher": "Example Healthcare Organization",
            "description": example.get("description", f"Quality measure: {measure_title}"),
            "purpose": f"To measure {measure_title.lower()} for quality improvement",
            "scoring": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/measure-scoring",
                        "code": scoring_info["code"],
                        "display": scoring_info["display"],
                    }
                ]
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/measure-type",
                            "code": type_info["code"],
                            "display": type_info["display"],
                        }
                    ]
                }
            ],
            "improvementNotation": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation",
                        "code": improvement["code"],
                        "display": improvement["display"],
                    }
                ]
            },
        }

        # Add library reference if provided
        if library_ref:
            resource["library"] = [library_ref]

        # Add effective period
        today = date.today()
        start_date = today - timedelta(days=self.faker.random_int(30, 365))
        resource["effectivePeriod"] = {
            "start": start_date.isoformat(),
            "end": (start_date + timedelta(days=365)).isoformat(),
        }

        # Add population groups
        resource["group"] = self._generate_population_groups(scoring_code)

        return resource

    def _generate_population_groups(self, scoring: str) -> list[dict[str, Any]]:
        """Generate population groups based on scoring type.

        Args:
            scoring: The measure scoring type

        Returns:
            List of population group definitions
        """
        populations = []

        # Initial population is always included
        populations.append(self._make_population("initial-population"))

        if scoring == "proportion":
            populations.extend(
                [
                    self._make_population("denominator"),
                    self._make_population("denominator-exclusion"),
                    self._make_population("numerator"),
                ]
            )
        elif scoring == "ratio":
            populations.extend(
                [
                    self._make_population("denominator"),
                    self._make_population("numerator"),
                ]
            )
        elif scoring == "continuous-variable":
            populations.extend(
                [
                    self._make_population("measure-population"),
                    self._make_population("measure-observation"),
                ]
            )
        elif scoring == "cohort":
            pass  # Only initial population needed

        return [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://example.org/fhir/measure-group",
                            "code": "main-group",
                            "display": "Main Population Group",
                        }
                    ]
                },
                "population": populations,
            }
        ]

    def _make_population(self, code: str) -> dict[str, Any]:
        """Create a population definition.

        Args:
            code: Population code (e.g., "initial-population")

        Returns:
            Population definition
        """
        pop_info = next(
            (p for p in MEASURE_POPULATION_CODES if p["code"] == code),
            {"code": code, "display": code.replace("-", " ").title()},
        )

        return {
            "code": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/measure-population",
                        "code": pop_info["code"],
                        "display": pop_info["display"],
                    }
                ]
            },
            "criteria": {
                "language": "text/cql-identifier",
                "expression": pop_info["display"].replace(" ", ""),
            },
        }

    def generate_proportion_measure(
        self,
        *,
        name: str | None = None,
        title: str | None = None,
        library_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a proportion-scored measure.

        Args:
            name: Measure name
            title: Human-readable title
            library_ref: Reference to CQL library

        Returns:
            A proportion Measure resource
        """
        return self.generate(
            name=name,
            title=title,
            library_ref=library_ref,
            scoring="proportion",
            measure_type="process",
            status="active",
        )

    def generate_outcome_measure(
        self,
        *,
        name: str | None = None,
        title: str | None = None,
        library_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate an outcome measure.

        Args:
            name: Measure name
            title: Human-readable title
            library_ref: Reference to CQL library

        Returns:
            An outcome Measure resource
        """
        return self.generate(
            name=name,
            title=title,
            library_ref=library_ref,
            scoring="proportion",
            measure_type="outcome",
            status="active",
        )

    def generate_batch(
        self,
        count: int = 10,
        library_ref: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate multiple Measure resources.

        Args:
            count: Number of measures to generate
            library_ref: Optional library reference for all measures

        Returns:
            List of Measure resources
        """
        return [self.generate(library_ref=library_ref) for _ in range(count)]
