"""Encounter resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import ENCOUNTER_CLASSES, ENCOUNTER_TYPES, make_codeable_concept


class EncounterGenerator(FHIRResourceGenerator):
    """Generator for FHIR Encounter resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        encounter_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        organization_ref: str | None = None,
        encounter_class: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Encounter resource.

        Args:
            encounter_id: Encounter ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            practitioner_ref: Practitioner reference
            organization_ref: Organization reference
            encounter_class: Encounter class code (AMB, EMER, IMP, etc.)

        Returns:
            Encounter FHIR resource
        """
        if encounter_id is None:
            encounter_id = self._generate_id()

        # Select encounter class (weighted towards ambulatory)
        if encounter_class is None:
            class_weights = [
                ("AMB", 0.7),  # Ambulatory most common
                ("EMER", 0.1),  # Emergency
                ("IMP", 0.1),  # Inpatient
                ("VR", 0.1),  # Virtual
            ]
            roll = self.faker.random.random()
            cumulative = 0.0
            encounter_class = "AMB"
            for code, weight in class_weights:
                cumulative += weight
                if roll < cumulative:
                    encounter_class = code
                    break

        class_coding = next(
            (c for c in ENCOUNTER_CLASSES if c.get("code") == encounter_class),
            ENCOUNTER_CLASSES[0],
        )

        # Select encounter type
        encounter_type = self.faker.random_element(ENCOUNTER_TYPES)

        # Generate period based on class
        now = datetime.now(timezone.utc)
        start = self.faker.date_time_between(
            start_date="-1y",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Duration based on type
        if encounter_class == "IMP":
            duration_hours = self.faker.random_int(min=24, max=168)  # 1-7 days
        elif encounter_class == "EMER":
            duration_hours = self.faker.random_int(min=2, max=12)
        else:
            duration_hours = self.faker.random_int(min=1, max=2)

        end = min(start + timedelta(hours=duration_hours), now)

        # Determine status based on dates
        if end < now:
            status = "finished"
        else:
            status = "in-progress"

        encounter: dict[str, Any] = {
            "resourceType": "Encounter",
            "id": encounter_id,
            "meta": self._generate_meta(),
            "status": status,
            "class": class_coding,
            "type": [make_codeable_concept(encounter_type)],
            "priority": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                        "code": "R",
                        "display": "routine",
                    }
                ]
            },
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
        }

        if patient_ref:
            encounter["subject"] = {"reference": patient_ref}

        if practitioner_ref:
            encounter["participant"] = [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "PPRF",
                                    "display": "primary performer",
                                }
                            ]
                        }
                    ],
                    "individual": {"reference": practitioner_ref},
                }
            ]

        if organization_ref:
            encounter["serviceProvider"] = {"reference": organization_ref}

        return encounter
