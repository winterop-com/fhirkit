"""MedicationDispense resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import MEDICATIONS_RXNORM, make_codeable_concept


class MedicationDispenseGenerator(FHIRResourceGenerator):
    """Generator for FHIR MedicationDispense resources.

    MedicationDispense records the dispensing of a medication to a patient,
    typically by a pharmacy in response to a prescription.
    """

    # Dispense statuses (weighted towards completed)
    STATUSES: list[str] = [
        "completed",
        "completed",
        "completed",
        "in-progress",
        "on-hold",
        "cancelled",
    ]

    # Days supply options
    DAYS_SUPPLY: list[int] = [7, 14, 30, 60, 90]

    # Substitution reasons
    SUBSTITUTION_REASONS: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "CT", "display": "Continuing therapy"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "FP", "display": "Formulary policy"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "OS", "display": "Out of stock"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
            "code": "RR",
            "display": "Regulatory requirement",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        dispense_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        medication_request_ref: str | None = None,
        location_ref: str | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MedicationDispense resource.

        Args:
            dispense_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            practitioner_ref: Practitioner who dispensed
            medication_request_ref: Reference to the prescription
            location_ref: Pharmacy location reference
            status: Dispense status

        Returns:
            MedicationDispense FHIR resource
        """
        if dispense_id is None:
            dispense_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUSES)

        # Select medication
        medication = self.faker.random_element(MEDICATIONS_RXNORM)

        # Generate times
        when_prepared = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        when_handed_over = (
            self.faker.date_time_between(
                start_date=when_prepared,
                end_date="now",
                tzinfo=timezone.utc,
            )
            if status == "completed"
            else None
        )

        # Generate quantity
        days_supply = self.faker.random_element(self.DAYS_SUPPLY)
        quantity_value = self.faker.random_int(min=10, max=180)

        dispense: dict[str, Any] = {
            "resourceType": "MedicationDispense",
            "id": dispense_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/dispense-ids",
                    value=f"DISP-{self.faker.numerify('########')}",
                )
            ],
            "status": status,
            "medicationCodeableConcept": make_codeable_concept(medication),
            "whenPrepared": when_prepared.isoformat(),
            "quantity": {
                "value": quantity_value,
                "unit": "tablets",
                "system": "http://unitsofmeasure.org",
                "code": "{tbl}",
            },
            "daysSupply": {
                "value": days_supply,
                "unit": "days",
                "system": "http://unitsofmeasure.org",
                "code": "d",
            },
            "dosageInstruction": [
                {
                    "text": f"Take {self.faker.random_element([1, 2])} tablet(s) "
                    f"{self.faker.random_element(['once', 'twice', 'three times'])} daily",
                    "timing": {
                        "repeat": {
                            "frequency": self.faker.random_int(1, 3),
                            "period": 1,
                            "periodUnit": "d",
                        }
                    },
                }
            ],
        }

        if when_handed_over:
            dispense["whenHandedOver"] = when_handed_over.isoformat()

        # Add substitution info (30% chance)
        if self.faker.boolean(chance_of_getting_true=30):
            dispense["substitution"] = {
                "wasSubstituted": True,
                "reason": [make_codeable_concept(self.faker.random_element(self.SUBSTITUTION_REASONS))],
            }

        if patient_ref:
            dispense["subject"] = {"reference": patient_ref}

        if practitioner_ref:
            dispense["performer"] = [
                {
                    "actor": {"reference": practitioner_ref},
                }
            ]

        if medication_request_ref:
            dispense["authorizingPrescription"] = [{"reference": medication_request_ref}]

        if location_ref:
            dispense["location"] = {"reference": location_ref}

        return dispense
