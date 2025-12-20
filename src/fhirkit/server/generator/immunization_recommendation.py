"""ImmunizationRecommendation resource generator."""

from datetime import datetime, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ImmunizationRecommendationGenerator(FHIRResourceGenerator):
    """Generator for FHIR ImmunizationRecommendation resources."""

    VACCINE_CODES = [
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "08",
            "display": "Hep B, adolescent or pediatric",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "20",
            "display": "DTaP",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "10",
            "display": "IPV",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "03",
            "display": "MMR",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "21",
            "display": "Varicella",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "115",
            "display": "Tdap",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "141",
            "display": "Influenza, seasonal, injectable",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "207",
            "display": "COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "33",
            "display": "pneumococcal polysaccharide PPV23",
        },
        {
            "system": "http://hl7.org/fhir/sid/cvx",
            "code": "52",
            "display": "Hep A, adult",
        },
    ]

    FORECAST_STATUS_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-recommendation-status",
            "code": "due",
            "display": "Due",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-recommendation-status",
            "code": "overdue",
            "display": "Overdue",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-recommendation-status",
            "code": "immune",
            "display": "Immune",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-recommendation-status",
            "code": "contraindicated",
            "display": "Contraindicated",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/immunization-recommendation-status",
            "code": "complete",
            "display": "Complete",
        },
    ]

    DATE_CRITERION_CODES = [
        {
            "system": "http://loinc.org",
            "code": "30981-5",
            "display": "Earliest date to give",
        },
        {
            "system": "http://loinc.org",
            "code": "30980-7",
            "display": "Date vaccine due",
        },
        {
            "system": "http://loinc.org",
            "code": "59777-3",
            "display": "Latest date to give immunization",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        recommendation_id: str | None = None,
        patient_reference: str | None = None,
        date: str | None = None,
        authority_reference: str | None = None,
        vaccine_code: dict[str, Any] | None = None,
        target_disease: dict[str, Any] | None = None,
        forecast_status: dict[str, Any] | None = None,
        dose_number: int | None = None,
        series_doses: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ImmunizationRecommendation resource.

        Args:
            recommendation_id: Resource ID (generates UUID if None)
            patient_reference: Reference to Patient
            date: Date of recommendation
            authority_reference: Reference to authority Organization
            vaccine_code: Vaccine code
            target_disease: Target disease code
            forecast_status: Forecast status
            dose_number: Recommended dose number
            series_doses: Total doses in series

        Returns:
            ImmunizationRecommendation FHIR resource
        """
        if recommendation_id is None:
            recommendation_id = self._generate_id()

        if date is None:
            date = datetime.now().isoformat()

        if vaccine_code is None:
            vaccine_code = self.faker.random_element(self.VACCINE_CODES)

        if forecast_status is None:
            forecast_status = self.faker.random_element(self.FORECAST_STATUS_CODES)

        if dose_number is None:
            dose_number = self.faker.random_int(1, 4)

        if series_doses is None:
            series_doses = max(dose_number, self.faker.random_int(dose_number, 5))

        recommendation: dict[str, Any] = {
            "resourceType": "ImmunizationRecommendation",
            "id": recommendation_id,
            "date": date,
        }

        # Add patient reference
        if patient_reference:
            recommendation["patient"] = {"reference": patient_reference}
        else:
            recommendation["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add authority reference
        if authority_reference:
            recommendation["authority"] = {"reference": authority_reference}

        # Build recommendation entry
        rec_entry: dict[str, Any] = {
            "vaccineCode": [
                {
                    "coding": [vaccine_code],
                    "text": vaccine_code["display"],
                }
            ],
            "forecastStatus": {
                "coding": [forecast_status],
                "text": forecast_status["display"],
            },
            "doseNumberPositiveInt": dose_number,
            "seriesDosesPositiveInt": series_doses,
        }

        # Add target disease if provided
        if target_disease:
            rec_entry["targetDisease"] = {
                "coding": [target_disease],
                "text": target_disease.get("display", ""),
            }

        # Add date criterion
        if forecast_status["code"] in ["due", "overdue"]:
            due_date = datetime.now() + timedelta(days=self.faker.random_int(-30, 90))
            rec_entry["dateCriterion"] = [
                {
                    "code": {
                        "coding": [self.DATE_CRITERION_CODES[1]],
                    },
                    "value": due_date.strftime("%Y-%m-%d"),
                }
            ]

        recommendation["recommendation"] = [rec_entry]

        return recommendation

    def generate_for_patient(
        self,
        patient_id: str,
        vaccine_codes: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an ImmunizationRecommendation for a patient.

        Args:
            patient_id: Patient ID
            vaccine_codes: List of vaccine codes for multiple recommendations

        Returns:
            ImmunizationRecommendation FHIR resource
        """
        return self.generate(
            patient_reference=f"Patient/{patient_id}",
            vaccine_code=vaccine_codes[0] if vaccine_codes else None,
            **kwargs,
        )
