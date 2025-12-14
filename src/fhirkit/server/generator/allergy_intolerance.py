"""AllergyIntolerance resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    ALLERGENS_ENVIRONMENT,
    ALLERGENS_FOOD,
    ALLERGENS_MEDICATION,
    ALLERGY_CLINICAL_STATUS,
    ALLERGY_REACTIONS,
    ALLERGY_VERIFICATION_STATUS,
    SNOMED_SYSTEM,
    CodingTemplate,
)


class AllergyIntoleranceGenerator(FHIRResourceGenerator):
    """Generator for FHIR AllergyIntolerance resources.

    AllergyIntolerance represents a patient's allergies and intolerances,
    including the allergen, reaction details, and clinical criticality.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        allergy_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        recorder_ref: str | None = None,
        category: str | None = None,
        onset_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an AllergyIntolerance resource.

        Args:
            allergy_id: Allergy ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter where allergy was recorded
            recorder_ref: Practitioner who recorded the allergy
            category: Category of allergen ("food", "medication", "environment", or None for random)
            onset_date: When the allergy was first identified (random if None)

        Returns:
            AllergyIntolerance FHIR resource
        """
        if allergy_id is None:
            allergy_id = self._generate_id()

        # Select category
        if category is None:
            category = self.faker.random_element(elements=["medication"] * 40 + ["food"] * 35 + ["environment"] * 25)

        # Select allergen based on category
        if category == "medication":
            allergen = self.faker.random_element(ALLERGENS_MEDICATION)
        elif category == "food":
            allergen = self.faker.random_element(ALLERGENS_FOOD)
        else:
            allergen = self.faker.random_element(ALLERGENS_ENVIRONMENT)

        # Select allergy type
        allergy_type = self.faker.random_element(elements=["allergy"] * 80 + ["intolerance"] * 20)

        # Select criticality with weighted distribution
        criticality = self.faker.random_element(elements=["low"] * 50 + ["high"] * 35 + ["unable-to-assess"] * 15)

        # Select clinical status (most are active)
        clinical_status = self.faker.random_element(elements=["active"] * 75 + ["inactive"] * 15 + ["resolved"] * 10)
        clinical_status_obj = next(
            (s for s in ALLERGY_CLINICAL_STATUS if s["code"] == clinical_status), ALLERGY_CLINICAL_STATUS[0]
        )

        # Select verification status (most are confirmed)
        verification_status = self.faker.random_element(
            elements=["confirmed"] * 60 + ["presumed"] * 25 + ["unconfirmed"] * 15
        )
        verification_status_obj = next(
            (s for s in ALLERGY_VERIFICATION_STATUS if s["code"] == verification_status), ALLERGY_VERIFICATION_STATUS[0]
        )

        # Generate onset date if not provided
        if onset_date is None:
            onset_dt = self.faker.date_time_between(
                start_date="-10y",
                end_date="-1m",
                tzinfo=timezone.utc,
            )
            onset_date = onset_dt.date().isoformat()

        # Generate recorded date (typically after onset)
        recorded_dt = self.faker.date_time_between(
            start_date="-1y",
            end_date="now",
            tzinfo=timezone.utc,
        )

        allergy: dict[str, Any] = {
            "resourceType": "AllergyIntolerance",
            "id": allergy_id,
            "meta": self._generate_meta(),
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": clinical_status_obj["code"],
                        "display": clinical_status_obj["display"],
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": verification_status_obj["code"],
                        "display": verification_status_obj["display"],
                    }
                ]
            },
            "type": allergy_type,
            "category": [category],
            "criticality": criticality,
            "code": {
                "coding": [
                    {
                        "system": SNOMED_SYSTEM,
                        "code": allergen["code"],
                        "display": allergen["display"],
                    }
                ],
                "text": allergen["display"],
            },
            "onsetDateTime": onset_date,
            "recordedDate": recorded_dt.isoformat(),
        }

        if patient_ref:
            allergy["patient"] = {"reference": patient_ref}

        if encounter_ref:
            allergy["encounter"] = {"reference": encounter_ref}

        if recorder_ref:
            allergy["recorder"] = {"reference": recorder_ref}

        # Add reaction details (70% chance)
        if self.faker.random.random() < 0.7:
            allergy["reaction"] = self._generate_reactions(criticality)

        # Add note for high criticality (50% chance)
        if criticality == "high" and self.faker.random.random() < 0.5:
            allergy["note"] = [{"text": self._generate_allergy_note(allergen, criticality)}]

        return allergy

    def _generate_reactions(self, criticality: str) -> list[dict[str, Any]]:
        """Generate reaction details based on criticality."""
        num_reactions = self.faker.random_int(min=1, max=3)
        reactions = []

        # For high criticality, always include a severe reaction
        if criticality == "high":
            severe_reactions = [r for r in ALLERGY_REACTIONS if r.get("severity") == "severe"]
            if severe_reactions:
                reaction = self.faker.random_element(severe_reactions)
                reactions.append(self._build_reaction(reaction, "severe"))

        # Add additional reactions
        while len(reactions) < num_reactions:
            reaction = self.faker.random_element(ALLERGY_REACTIONS)
            severity = reaction.get("severity", "mild")
            if criticality == "low" and severity == "severe":
                severity = "moderate"
            reactions.append(self._build_reaction(reaction, severity))

        return reactions

    def _build_reaction(self, reaction: dict[str, str], severity: str) -> dict[str, Any]:
        """Build a single reaction entry."""
        return {
            "manifestation": [
                {
                    "coding": [
                        {
                            "system": SNOMED_SYSTEM,
                            "code": reaction["code"],
                            "display": reaction["display"],
                        }
                    ],
                    "text": reaction["display"],
                }
            ],
            "severity": severity,
        }

    def _generate_allergy_note(self, allergen: CodingTemplate, criticality: str) -> str:
        """Generate a clinical note for the allergy."""
        allergen_name = allergen.get("display", "Unknown allergen")

        if criticality == "high":
            templates = [
                f"Patient has a history of severe reaction to {allergen_name}. "
                "Epinephrine auto-injector prescribed. Immediate medical attention required upon exposure.",
                f"HIGH ALERT: Known severe {allergen_name}. "
                "Previous anaphylactic reaction documented. Avoid all related substances.",
                f"Critical allergy to {allergen_name}. Patient carries emergency epinephrine. Alert all providers.",
            ]
        else:
            templates = [
                f"Patient reported {allergen_name}. Monitor for reactions.",
                f"Documented {allergen_name}. Avoid exposure when possible.",
            ]

        return self.faker.random_element(templates)

    def generate_medication_allergy(
        self,
        patient_ref: str | None = None,
        recorder_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a medication allergy.

        Returns:
            AllergyIntolerance for a medication
        """
        return self.generate(
            patient_ref=patient_ref,
            recorder_ref=recorder_ref,
            category="medication",
        )

    def generate_food_allergy(
        self,
        patient_ref: str | None = None,
        recorder_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a food allergy.

        Returns:
            AllergyIntolerance for a food
        """
        return self.generate(
            patient_ref=patient_ref,
            recorder_ref=recorder_ref,
            category="food",
        )

    def generate_environmental_allergy(
        self,
        patient_ref: str | None = None,
        recorder_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate an environmental allergy.

        Returns:
            AllergyIntolerance for an environmental allergen
        """
        return self.generate(
            patient_ref=patient_ref,
            recorder_ref=recorder_ref,
            category="environment",
        )
