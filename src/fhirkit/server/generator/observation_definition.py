"""ObservationDefinition resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ObservationDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR ObservationDefinition resources."""

    # Observation categories
    CATEGORIES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "vital-signs",
            "display": "Vital Signs",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "laboratory",
            "display": "Laboratory",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "imaging",
            "display": "Imaging",
        },
    ]

    # Permitted data types
    PERMITTED_DATA_TYPES = [
        "Quantity",
        "CodeableConcept",
        "string",
        "boolean",
        "integer",
        "Range",
        "Ratio",
        "SampledData",
        "time",
        "dateTime",
        "Period",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        code: dict[str, Any] | None = None,
        category: list[dict[str, Any]] | None = None,
        permitted_data_type: list[str] | None = None,
        multiple_results_allowed: bool = False,
        method: dict[str, Any] | None = None,
        preferred_report_name: str | None = None,
        quantitative_details: dict[str, Any] | None = None,
        qualified_interval: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ObservationDefinition resource.

        Args:
            definition_id: Resource ID (generates UUID if None)
            code: What observation this defines
            category: Observation category
            permitted_data_type: Permitted value types
            multiple_results_allowed: Allow multiple results
            method: Method of observation
            preferred_report_name: Preferred name for reports
            quantitative_details: Quantitative details
            qualified_interval: Reference intervals

        Returns:
            ObservationDefinition FHIR resource
        """
        if definition_id is None:
            definition_id = self._generate_id()

        if code is None:
            code = self._generate_observation_code()

        observation_definition: dict[str, Any] = {
            "resourceType": "ObservationDefinition",
            "id": definition_id,
            "meta": self._generate_meta(),
            "code": code,
            "multipleResultsAllowed": multiple_results_allowed,
        }

        # Add category
        if category:
            observation_definition["category"] = category
        else:
            cat = self.faker.random_element(self.CATEGORIES)
            observation_definition["category"] = [{"coding": [cat], "text": cat["display"]}]

        # Add permitted data type
        if permitted_data_type:
            observation_definition["permittedDataType"] = permitted_data_type
        else:
            observation_definition["permittedDataType"] = [self.faker.random_element(self.PERMITTED_DATA_TYPES)]

        # Add method
        if method:
            observation_definition["method"] = method

        # Add preferred report name
        if preferred_report_name:
            observation_definition["preferredReportName"] = preferred_report_name
        else:
            observation_definition["preferredReportName"] = code.get(
                "text", code.get("coding", [{}])[0].get("display", "Observation")
            )

        # Add quantitative details for Quantity type
        if quantitative_details:
            observation_definition["quantitativeDetails"] = quantitative_details
        elif "Quantity" in observation_definition.get("permittedDataType", []):
            observation_definition["quantitativeDetails"] = self._generate_quantitative_details()

        # Add qualified interval (reference ranges)
        if qualified_interval:
            observation_definition["qualifiedInterval"] = qualified_interval
        elif self.faker.boolean(chance_of_getting_true=70):
            observation_definition["qualifiedInterval"] = self._generate_intervals()

        return observation_definition

    def _generate_observation_code(self) -> dict[str, Any]:
        """Generate an observation code."""
        codes = [
            {
                "system": "http://loinc.org",
                "code": "8480-6",
                "display": "Systolic blood pressure",
            },
            {
                "system": "http://loinc.org",
                "code": "8462-4",
                "display": "Diastolic blood pressure",
            },
            {
                "system": "http://loinc.org",
                "code": "8867-4",
                "display": "Heart rate",
            },
            {
                "system": "http://loinc.org",
                "code": "2339-0",
                "display": "Glucose [Mass/volume] in Blood",
            },
            {
                "system": "http://loinc.org",
                "code": "718-7",
                "display": "Hemoglobin [Mass/volume] in Blood",
            },
        ]
        selected = self.faker.random_element(codes)
        return {"coding": [selected], "text": selected["display"]}

    def _generate_quantitative_details(self) -> dict[str, Any]:
        """Generate quantitative details."""
        units = [
            {"code": "mmHg", "display": "millimeters of mercury"},
            {"code": "/min", "display": "per minute"},
            {"code": "mg/dL", "display": "milligrams per deciliter"},
            {"code": "g/dL", "display": "grams per deciliter"},
        ]
        unit = self.faker.random_element(units)

        return {
            "unit": {
                "coding": [
                    {
                        "system": "http://unitsofmeasure.org",
                        "code": unit["code"],
                        "display": unit["display"],
                    }
                ]
            },
            "decimalPrecision": self.faker.random_int(0, 2),
        }

    def _generate_intervals(self) -> list[dict[str, Any]]:
        """Generate reference intervals."""
        return [
            {
                "category": "reference",
                "range": {
                    "low": {"value": float(self.faker.random_int(60, 100)), "unit": "unit"},
                    "high": {"value": float(self.faker.random_int(100, 150)), "unit": "unit"},
                },
                "context": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
                            "code": "normal",
                            "display": "Normal Range",
                        }
                    ]
                },
            }
        ]

    def generate_vital_sign_definition(
        self,
        code: dict[str, Any],
        unit: str,
        low: float,
        high: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ObservationDefinition for a vital sign.

        Args:
            code: Observation code
            unit: Unit of measure
            low: Low reference value
            high: High reference value

        Returns:
            ObservationDefinition FHIR resource
        """
        category = [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ]
            }
        ]

        quantitative_details = {
            "unit": {"coding": [{"system": "http://unitsofmeasure.org", "code": unit}]},
            "decimalPrecision": 1,
        }

        qualified_interval = [
            {
                "category": "reference",
                "range": {"low": {"value": low, "unit": unit}, "high": {"value": high, "unit": unit}},
                "context": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
                            "code": "normal",
                        }
                    ]
                },
            }
        ]

        return self.generate(
            code=code,
            category=category,
            permitted_data_type=["Quantity"],
            quantitative_details=quantitative_details,
            qualified_interval=qualified_interval,
            **kwargs,
        )
