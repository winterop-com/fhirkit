"""RiskAssessment resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class RiskAssessmentGenerator(FHIRResourceGenerator):
    """Generator for FHIR RiskAssessment resources.

    RiskAssessment represents clinical risk assessments that predict
    the likelihood of various health outcomes.
    """

    # Assessment statuses
    STATUSES: list[str] = [
        "final",
        "final",
        "final",
        "preliminary",
        "amended",
        "registered",
    ]

    # Risk assessment types with predictions
    RISK_TYPES: list[dict[str, Any]] = [
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {"system": "http://snomed.info/sct", "code": "129299003", "display": "Fall risk assessment"},
            "outcome": {"system": "http://snomed.info/sct", "code": "161898004", "display": "Falls"},
            "qualitative_risk": "moderate",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {
                "system": "http://snomed.info/sct",
                "code": "763247001",
                "display": "Cardiovascular risk assessment",
            },
            "outcome": {"system": "http://snomed.info/sct", "code": "22298006", "display": "Myocardial infarction"},
            "qualitative_risk": "high",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {"system": "http://snomed.info/sct", "code": "710063005", "display": "VTE risk assessment"},
            "outcome": {"system": "http://snomed.info/sct", "code": "59282003", "display": "Pulmonary embolism"},
            "qualitative_risk": "low",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {"system": "http://snomed.info/sct", "code": "445536008", "display": "Stroke risk assessment"},
            "outcome": {"system": "http://snomed.info/sct", "code": "230690007", "display": "Cerebrovascular accident"},
            "qualitative_risk": "moderate",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {
                "system": "http://snomed.info/sct",
                "code": "428232008",
                "display": "Pressure ulcer risk assessment",
            },
            "outcome": {"system": "http://snomed.info/sct", "code": "420226006", "display": "Pressure ulcer"},
            "qualitative_risk": "moderate",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {"system": "http://snomed.info/sct", "code": "225337009", "display": "Suicide risk assessment"},
            "outcome": {"system": "http://snomed.info/sct", "code": "44301001", "display": "Suicide"},
            "qualitative_risk": "low",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "225338004", "display": "Risk assessment"},
            "method": {
                "system": "http://snomed.info/sct",
                "code": "171207007",
                "display": "Osteoporosis risk assessment",
            },
            "outcome": {"system": "http://snomed.info/sct", "code": "125605004", "display": "Fracture"},
            "qualitative_risk": "moderate",
        },
    ]

    # Qualitative risk levels
    QUALITATIVE_RISKS: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/risk-probability",
            "code": "negligible",
            "display": "Negligible likelihood",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/risk-probability",
            "code": "low",
            "display": "Low likelihood",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/risk-probability",
            "code": "moderate",
            "display": "Moderate likelihood",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/risk-probability",
            "code": "high",
            "display": "High likelihood",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/risk-probability", "code": "certain", "display": "Certain"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        assessment_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        practitioner_ref: str | None = None,
        condition_ref: str | None = None,
        status: str | None = None,
        risk_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a RiskAssessment resource.

        Args:
            assessment_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference
            encounter_ref: Encounter reference
            practitioner_ref: Performer reference
            condition_ref: Related condition reference
            status: Assessment status
            risk_type: Specific risk type configuration

        Returns:
            RiskAssessment FHIR resource
        """
        if assessment_id is None:
            assessment_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUSES)

        if risk_type is None:
            risk_type = self.faker.random_element(self.RISK_TYPES)

        # Generate occurrence time
        occurrence_datetime = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Find matching qualitative risk
        qual_risk = next(
            (r for r in self.QUALITATIVE_RISKS if r["code"] == risk_type["qualitative_risk"]),
            self.QUALITATIVE_RISKS[2],  # default to moderate
        )

        # Generate probability based on qualitative risk
        prob_map = {
            "negligible": (0.0, 0.05),
            "low": (0.05, 0.2),
            "moderate": (0.2, 0.5),
            "high": (0.5, 0.8),
            "certain": (0.8, 1.0),
        }
        prob_range = prob_map.get(risk_type["qualitative_risk"], (0.2, 0.5))
        probability = round(self.faker.pyfloat(min_value=prob_range[0], max_value=prob_range[1]), 2)

        assessment: dict[str, Any] = {
            "resourceType": "RiskAssessment",
            "id": assessment_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/risk-assessment-ids",
                    value=f"RA-{self.faker.numerify('########')}",
                )
            ],
            "status": status,
            "code": make_codeable_concept(risk_type["code"]),
            "method": make_codeable_concept(risk_type["method"]),
            "occurrenceDateTime": occurrence_datetime.isoformat(),
            "prediction": [
                {
                    "outcome": make_codeable_concept(risk_type["outcome"]),
                    "probabilityDecimal": probability,
                    "qualitativeRisk": make_codeable_concept(qual_risk),
                    "relativeRisk": round(self.faker.pyfloat(min_value=0.5, max_value=3.0), 1),
                    "whenRange": {
                        "low": {"value": 1, "unit": "year", "system": "http://unitsofmeasure.org", "code": "a"},
                        "high": {"value": 5, "unit": "years", "system": "http://unitsofmeasure.org", "code": "a"},
                    },
                }
            ],
            "mitigation": f"Monitor and implement preventive measures for {risk_type['outcome']['display'].lower()}",
        }

        # Add note
        assessment["note"] = [
            {
                "text": f"Risk assessment performed using standardized {risk_type['method']['display'].lower()} tool.",
            }
        ]

        if patient_ref:
            assessment["subject"] = {"reference": patient_ref}

        if encounter_ref:
            assessment["encounter"] = {"reference": encounter_ref}

        if practitioner_ref:
            assessment["performer"] = {"reference": practitioner_ref}

        if condition_ref:
            assessment["basis"] = [{"reference": condition_ref}]

        return assessment
