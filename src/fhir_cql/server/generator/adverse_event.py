"""AdverseEvent resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class AdverseEventGenerator(FHIRResourceGenerator):
    """Generator for FHIR AdverseEvent resources.

    AdverseEvent records actual or potential events that may cause harm
    to a patient during medical treatment.
    """

    # Actuality (actual vs potential)
    ACTUALITIES: list[str] = ["actual", "actual", "actual", "potential"]

    # Event categories
    CATEGORIES: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "product-problem",
            "display": "Product Problem",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "product-quality",
            "display": "Product Quality",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "product-use-error",
            "display": "Product Use Error",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "wrong-dose",
            "display": "Wrong Dose",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "incorrect-prescribing-information",
            "display": "Incorrect Prescribing Information",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "wrong-technique",
            "display": "Wrong Technique",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "wrong-route-of-administration",
            "display": "Wrong Route of Administration",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "wrong-rate",
            "display": "Wrong Rate",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "wrong-time",
            "display": "Wrong Time",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "expired-drug",
            "display": "Expired Drug",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "medical-device-use-error",
            "display": "Medical Device Use Error",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-category",
            "code": "unsafe-physical-environment",
            "display": "Unsafe Physical Environment",
        },
    ]

    # Adverse event types
    EVENT_TYPES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "418799008", "display": "Adverse reaction to drug"},
        {"system": "http://snomed.info/sct", "code": "281647001", "display": "Adverse reaction"},
        {"system": "http://snomed.info/sct", "code": "304386008", "display": "Fall from bed"},
        {"system": "http://snomed.info/sct", "code": "217082002", "display": "Accidental fall"},
        {"system": "http://snomed.info/sct", "code": "262574004", "display": "Surgical wound infection"},
        {"system": "http://snomed.info/sct", "code": "128309008", "display": "Nosocomial infection"},
        {"system": "http://snomed.info/sct", "code": "213293003", "display": "Pressure ulcer"},
        {"system": "http://snomed.info/sct", "code": "242602001", "display": "Blood transfusion reaction"},
    ]

    # Seriousness codes
    SERIOUSNESS: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "Non-serious",
            "display": "Non-serious",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "Serious",
            "display": "Serious",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "SeriousResultsInDeath",
            "display": "Results in death",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "SeriousIsLifeThreatening",
            "display": "Is Life-threatening",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "SeriousResultsInHospitalization",
            "display": "Requires or prolongs inpatient hospitalization",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
            "code": "SeriousResultsInDisability",
            "display": "Results in persistent or significant disability",
        },
    ]

    # Outcome codes
    OUTCOMES: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            "code": "resolved",
            "display": "Resolved",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            "code": "recovering",
            "display": "Recovering",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            "code": "ongoing",
            "display": "Ongoing",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            "code": "resolvedWithSequelae",
            "display": "Resolved with Sequelae",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome", "code": "fatal", "display": "Fatal"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            "code": "unknown",
            "display": "Unknown",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        event_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        practitioner_ref: str | None = None,
        location_ref: str | None = None,
        suspect_ref: str | None = None,
        actuality: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an AdverseEvent resource.

        Args:
            event_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference
            encounter_ref: Encounter reference
            practitioner_ref: Recorder reference
            location_ref: Location reference
            suspect_ref: Suspected causative agent (e.g., Medication)
            actuality: Whether event is actual or potential

        Returns:
            AdverseEvent FHIR resource
        """
        if event_id is None:
            event_id = self._generate_id()

        if actuality is None:
            actuality = self.faker.random_element(self.ACTUALITIES)

        # Select event details
        category = self.faker.random_element(self.CATEGORIES)
        event_type = self.faker.random_element(self.EVENT_TYPES)
        seriousness = self.faker.random_element(self.SERIOUSNESS)
        outcome = self.faker.random_element(self.OUTCOMES)

        # Generate event date
        event_date = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Generate detected date (same or after event date)
        detected_date = self.faker.date_time_between(
            start_date=event_date,
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Generate recorded date (same or after detected date)
        recorded_date = self.faker.date_time_between(
            start_date=detected_date,
            end_date="now",
            tzinfo=timezone.utc,
        )

        event: dict[str, Any] = {
            "resourceType": "AdverseEvent",
            "id": event_id,
            "meta": self._generate_meta(),
            "identifier": self._generate_identifier(
                system="http://example.org/adverse-event-ids",
                value=f"AE-{self.faker.numerify('########')}",
            ),
            "actuality": actuality,
            "category": [make_codeable_concept(category)],
            "event": make_codeable_concept(event_type),
            "date": event_date.isoformat(),
            "detected": detected_date.isoformat(),
            "recordedDate": recorded_date.isoformat(),
            "seriousness": make_codeable_concept(seriousness),
            "outcome": make_codeable_concept(outcome),
        }

        if patient_ref:
            event["subject"] = {"reference": patient_ref}

        if encounter_ref:
            event["encounter"] = {"reference": encounter_ref}

        if practitioner_ref:
            event["recorder"] = {"reference": practitioner_ref}

        if location_ref:
            event["location"] = {"reference": location_ref}

        # Add suspect entity if provided
        if suspect_ref:
            event["suspectEntity"] = [
                {
                    "instance": {"reference": suspect_ref},
                    "causality": [
                        {
                            "assessment": {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
                                        "code": self.faker.random_element(
                                            [
                                                "Certain",
                                                "Probable-Likely",
                                                "Possible",
                                                "Unlikely",
                                                "Conditional-Classified",
                                                "Unassessable-Unclassifiable",
                                            ]
                                        ),
                                    }
                                ]
                            }
                        }
                    ],
                }
            ]

        return event
