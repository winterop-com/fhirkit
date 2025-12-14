"""Immunization resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    IMMUNIZATION_ROUTES,
    IMMUNIZATION_SITES,
    VACCINES,
    CodingTemplate,
)


class ImmunizationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Immunization resources.

    Immunization represents a patient's vaccination records including
    the vaccine administered, site, route, and performer information.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        immunization_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        performer_ref: str | None = None,
        occurrence_date: str | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Immunization resource.

        Args:
            immunization_id: Immunization ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            performer_ref: Practitioner who administered the vaccine
            occurrence_date: When the immunization was given (random if None)
            status: Status (completed, entered-in-error, not-done)

        Returns:
            Immunization FHIR resource
        """
        if immunization_id is None:
            immunization_id = self._generate_id()

        # Select vaccine
        vaccine = self.faker.random_element(VACCINES)

        # Generate occurrence date if not provided
        if occurrence_date is None:
            occurrence_dt = self.faker.date_time_between(
                start_date="-5y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            occurrence_date = occurrence_dt.isoformat()

        # Status (most are completed)
        if status is None:
            status = self.faker.random_element(
                elements=["completed"] * 95 + ["not-done"] * 4 + ["entered-in-error"] * 1
            )

        # Select site and route
        site = self.faker.random_element(IMMUNIZATION_SITES)
        route = self.faker.random_element(IMMUNIZATION_ROUTES)

        # Generate lot number
        lot_number = self.faker.bothify("??####-##").upper()

        # Generate expiration date (1-3 years from occurrence)
        exp_date = self.faker.date_between(
            start_date="+6m",
            end_date="+3y",
        ).isoformat()

        immunization: dict[str, Any] = {
            "resourceType": "Immunization",
            "id": immunization_id,
            "meta": self._generate_meta(),
            "status": status,
            "vaccineCode": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/cvx",
                        "code": vaccine["code"],
                        "display": vaccine["display"],
                    }
                ],
                "text": vaccine["display"],
            },
            "occurrenceDateTime": occurrence_date,
            "primarySource": True,
        }

        if patient_ref:
            immunization["patient"] = {"reference": patient_ref}

        if encounter_ref:
            immunization["encounter"] = {"reference": encounter_ref}

        if status == "completed":
            # Add additional details for completed immunizations
            immunization["site"] = {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": site["code"],
                        "display": site["display"],
                    }
                ],
                "text": site["display"],
            }
            immunization["route"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration",
                        "code": route["code"],
                        "display": route["display"],
                    }
                ],
            }
            immunization["lotNumber"] = lot_number
            immunization["expirationDate"] = exp_date

            if performer_ref:
                immunization["performer"] = [
                    {
                        "function": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0443",
                                    "code": "AP",
                                    "display": "Administering Provider",
                                }
                            ]
                        },
                        "actor": {"reference": performer_ref},
                    }
                ]

            # Add dose quantity (standard 0.5 mL for most vaccines)
            immunization["doseQuantity"] = {
                "value": 0.5,
                "unit": "mL",
                "system": "http://unitsofmeasure.org",
                "code": "mL",
            }

        elif status == "not-done":
            # Add reason for not administering
            immunization["statusReason"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                        "code": self.faker.random_element(["MEDPREC", "PATOBJ", "OSTOCK"]),
                        "display": self.faker.random_element(
                            ["medical precaution", "patient objection", "product out of stock"]
                        ),
                    }
                ]
            }

        # Add note for some immunizations (20% chance)
        if self.faker.random.random() < 0.2:
            immunization["note"] = [{"text": self._generate_immunization_note(vaccine, status)}]

        return immunization

    def _generate_immunization_note(self, vaccine: CodingTemplate, status: str) -> str:
        """Generate a clinical note for the immunization."""
        vaccine_name = vaccine.get("display", "vaccine")

        if status == "completed":
            templates = [
                f"{vaccine_name} administered without complications.",
                "Patient tolerated vaccination well. No immediate adverse reactions.",
                "Vaccine administered per schedule. Patient observed for 15 minutes post-injection.",
                "Routine vaccination completed. Next dose due per recommended schedule.",
            ]
        elif status == "not-done":
            templates = [
                f"{vaccine_name} deferred due to patient illness. Reschedule when recovered.",
                "Vaccination postponed at patient request. Counseled on importance of vaccination.",
                "Vaccine not available. Patient to return when stock replenished.",
            ]
        else:
            templates = [
                "Entry made in error and corrected.",
            ]

        return self.faker.random_element(templates)

    def generate_flu_shot(
        self,
        patient_ref: str | None = None,
        performer_ref: str | None = None,
        occurrence_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a flu vaccination record.

        Returns:
            Immunization for influenza vaccine
        """
        # Select a flu vaccine specifically
        flu_vaccines = [v for v in VACCINES if "Influenza" in v.get("display", "")]
        vaccine = self.faker.random_element(flu_vaccines) if flu_vaccines else VACCINES[0]

        immunization = self.generate(
            patient_ref=patient_ref,
            performer_ref=performer_ref,
            occurrence_date=occurrence_date,
            status="completed",
        )
        # Override with flu vaccine
        immunization["vaccineCode"] = {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/cvx",
                    "code": vaccine["code"],
                    "display": vaccine["display"],
                }
            ],
            "text": vaccine["display"],
        }
        return immunization

    def generate_covid_vaccination(
        self,
        patient_ref: str | None = None,
        performer_ref: str | None = None,
        occurrence_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a COVID-19 vaccination record.

        Returns:
            Immunization for COVID-19 vaccine
        """
        # Select a COVID vaccine specifically
        covid_vaccines = [v for v in VACCINES if "COVID" in v.get("display", "")]
        vaccine = self.faker.random_element(covid_vaccines) if covid_vaccines else VACCINES[0]

        immunization = self.generate(
            patient_ref=patient_ref,
            performer_ref=performer_ref,
            occurrence_date=occurrence_date,
            status="completed",
        )
        # Override with COVID vaccine
        immunization["vaccineCode"] = {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/cvx",
                    "code": vaccine["code"],
                    "display": vaccine["display"],
                }
            ],
            "text": vaccine["display"],
        }
        return immunization
