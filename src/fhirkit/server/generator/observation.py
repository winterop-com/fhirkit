"""Observation resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import LAB_TESTS, LOINC_SYSTEM, VITAL_SIGNS


class ObservationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Observation resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        observation_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        observation_type: str = "vital-signs",
        effective_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Observation resource.

        Args:
            observation_id: Observation ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            observation_type: Type of observation ("vital-signs" or "laboratory")
            effective_date: Effective datetime (random if None)

        Returns:
            Observation FHIR resource
        """
        if observation_id is None:
            observation_id = self._generate_id()

        if effective_date is None:
            effective_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            effective_date = effective_dt.isoformat()

        if observation_type == "vital-signs":
            return self._generate_vital_sign(observation_id, patient_ref, encounter_ref, effective_date)
        else:
            return self._generate_lab_result(observation_id, patient_ref, encounter_ref, effective_date)

    def _generate_vital_sign(
        self,
        observation_id: str,
        patient_ref: str | None,
        encounter_ref: str | None,
        effective_date: str,
    ) -> dict[str, Any]:
        """Generate a vital sign observation."""
        vital = self.faker.random_element(VITAL_SIGNS)

        # Generate value (80% normal, 20% abnormal)
        if self.faker.random.random() < 0.8:
            value = self.faker.random.uniform(vital["normal_low"], vital["normal_high"])
        else:
            # Generate abnormal value
            if self.faker.random.random() < 0.5 and vital.get("abnormal_low"):
                value = self.faker.random.uniform(vital["abnormal_low"], vital["normal_low"])
            elif vital.get("abnormal_high"):
                value = self.faker.random.uniform(vital["normal_high"], vital["abnormal_high"])
            else:
                value = self.faker.random.uniform(vital["normal_low"], vital["normal_high"])

        # Determine interpretation
        if value < vital["normal_low"]:
            interpretation = {"code": "L", "display": "Low"}
        elif value > vital["normal_high"]:
            interpretation = {"code": "H", "display": "High"}
        else:
            interpretation = {"code": "N", "display": "Normal"}

        observation: dict[str, Any] = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": self._generate_meta(),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": LOINC_SYSTEM,
                        "code": vital["code"],
                        "display": vital["display"],
                    }
                ],
                "text": vital["display"],
            },
            "effectiveDateTime": effective_date,
            "valueQuantity": self._generate_quantity(
                value=value,
                unit=vital["unit"],
            ),
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": interpretation["code"],
                            "display": interpretation["display"],
                        }
                    ]
                }
            ],
            "referenceRange": [
                {
                    "low": self._generate_quantity(vital["normal_low"], vital["unit"]),
                    "high": self._generate_quantity(vital["normal_high"], vital["unit"]),
                }
            ],
        }

        if patient_ref:
            observation["subject"] = {"reference": patient_ref}

        if encounter_ref:
            observation["encounter"] = {"reference": encounter_ref}

        return observation

    def _generate_lab_result(
        self,
        observation_id: str,
        patient_ref: str | None,
        encounter_ref: str | None,
        effective_date: str,
    ) -> dict[str, Any]:
        """Generate a laboratory observation."""
        lab = self.faker.random_element(LAB_TESTS)

        # Generate value (75% normal, 25% abnormal)
        if self.faker.random.random() < 0.75:
            value = self.faker.random.uniform(lab["normal_low"], lab["normal_high"])
        else:
            # Abnormal - either low or high
            range_size = lab["normal_high"] - lab["normal_low"]
            if self.faker.random.random() < 0.5:
                value = lab["normal_low"] - self.faker.random.uniform(0.1 * range_size, 0.5 * range_size)
            else:
                value = lab["normal_high"] + self.faker.random.uniform(0.1 * range_size, 0.5 * range_size)

        # Determine interpretation
        if value < lab["normal_low"]:
            interpretation = {"code": "L", "display": "Low"}
        elif value > lab["normal_high"]:
            interpretation = {"code": "H", "display": "High"}
        else:
            interpretation = {"code": "N", "display": "Normal"}

        observation: dict[str, Any] = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": self._generate_meta(),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": LOINC_SYSTEM,
                        "code": lab["code"],
                        "display": lab["display"],
                    }
                ],
                "text": lab["display"],
            },
            "effectiveDateTime": effective_date,
            "valueQuantity": self._generate_quantity(
                value=round(value, 2),
                unit=lab["unit"],
            ),
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": interpretation["code"],
                            "display": interpretation["display"],
                        }
                    ]
                }
            ],
            "referenceRange": [
                {
                    "low": self._generate_quantity(lab["normal_low"], lab["unit"]),
                    "high": self._generate_quantity(lab["normal_high"], lab["unit"]),
                }
            ],
        }

        if patient_ref:
            observation["subject"] = {"reference": patient_ref}

        if encounter_ref:
            observation["encounter"] = {"reference": encounter_ref}

        return observation

    def generate_vital_signs_panel(
        self,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        effective_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generate a complete set of vital signs.

        Returns:
            List of vital sign observations
        """
        if effective_date is None:
            effective_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            effective_date = effective_dt.isoformat()

        observations = []

        # Generate all vital signs
        for vital in VITAL_SIGNS:
            obs = self._generate_vital_sign(
                observation_id=self._generate_id(),
                patient_ref=patient_ref,
                encounter_ref=encounter_ref,
                effective_date=effective_date,
            )
            # Override with specific vital sign
            obs["code"]["coding"][0]["code"] = vital["code"]
            obs["code"]["coding"][0]["display"] = vital["display"]
            obs["code"]["text"] = vital["display"]

            # Generate appropriate value
            value = self.faker.random.uniform(vital["normal_low"], vital["normal_high"])
            obs["valueQuantity"] = self._generate_quantity(value, vital["unit"])
            obs["referenceRange"] = [
                {
                    "low": self._generate_quantity(vital["normal_low"], vital["unit"]),
                    "high": self._generate_quantity(vital["normal_high"], vital["unit"]),
                }
            ]

            observations.append(obs)

        return observations
