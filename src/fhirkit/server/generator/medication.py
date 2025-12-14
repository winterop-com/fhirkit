"""Medication resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    MEDICATION_DOSE_FORMS,
    MEDICATION_INGREDIENT_STRENGTHS,
    MEDICATIONS_RXNORM,
    RXNORM_SYSTEM,
    SNOMED_SYSTEM,
)


class MedicationGenerator(FHIRResourceGenerator):
    """Generator for FHIR Medication resources.

    Medication represents a medication that can be prescribed, dispensed,
    or administered. This is a catalog-style resource.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        medication_id: str | None = None,
        status: str | None = None,
        manufacturer_ref: str | None = None,
        include_batch: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Medication resource.

        Args:
            medication_id: Medication ID (generates UUID if None)
            status: Status (active, inactive, entered-in-error)
            manufacturer_ref: Manufacturer (Organization) reference
            include_batch: Whether to include batch information

        Returns:
            Medication FHIR resource
        """
        if medication_id is None:
            medication_id = self._generate_id()

        # Status
        if status is None:
            status = self.faker.random_element(elements=["active"] * 90 + ["inactive"] * 8 + ["entered-in-error"] * 2)

        # Select medication
        med = self.faker.random_element(MEDICATIONS_RXNORM)

        # Select dose form
        dose_form = self.faker.random_element(MEDICATION_DOSE_FORMS)

        # Select strength
        strength = self.faker.random_element(MEDICATION_INGREDIENT_STRENGTHS)

        medication: dict[str, Any] = {
            "resourceType": "Medication",
            "id": medication_id,
            "meta": self._generate_meta(),
            "status": status,
            "code": {
                "coding": [
                    {
                        "system": RXNORM_SYSTEM,
                        "code": med["code"],
                        "display": med["display"],
                    }
                ],
                "text": f"{med['display']} {strength['value']}{strength['unit']}",
            },
            "form": {
                "coding": [
                    {
                        "system": SNOMED_SYSTEM,
                        "code": dose_form["code"],
                        "display": dose_form["display"],
                    }
                ],
                "text": dose_form["display"],
            },
        }

        if manufacturer_ref:
            medication["manufacturer"] = {"reference": manufacturer_ref}

        # Add ingredient (active ingredient)
        medication["ingredient"] = [
            {
                "itemCodeableConcept": {
                    "coding": [
                        {
                            "system": RXNORM_SYSTEM,
                            "code": med["code"],
                            "display": med["display"],
                        }
                    ],
                    "text": med["display"],
                },
                "isActive": True,
                "strength": {
                    "numerator": {
                        "value": strength["value"],
                        "unit": strength["unit"],
                        "system": "http://unitsofmeasure.org",
                        "code": strength["unit"],
                    },
                    "denominator": {
                        "value": 1,
                        "unit": dose_form["display"].lower(),
                        "system": "http://terminology.hl7.org/CodeSystem/v3-orderableDrugForm",
                        "code": "TAB" if "tablet" in dose_form["display"].lower() else "CAP",
                    },
                },
            }
        ]

        # Add batch information
        if include_batch and status == "active":
            medication["batch"] = self._generate_batch_info()

        return medication

    def _generate_batch_info(self) -> dict[str, Any]:
        """Generate batch/lot information."""
        # Lot number format: 2 letters, 4 digits, 2 digits
        lot_number = self.faker.bothify("??####-##").upper()

        # Expiration date 6-36 months from now
        exp_date = (self.faker.date_between(start_date="+6m", end_date="+3y")).isoformat()

        return {
            "lotNumber": lot_number,
            "expirationDate": exp_date,
        }

    def generate_tablet(
        self,
        medication_id: str | None = None,
        manufacturer_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a tablet medication.

        Returns:
            Medication resource for a tablet formulation
        """
        med = self.generate(
            medication_id=medication_id,
            manufacturer_ref=manufacturer_ref,
        )
        # Override form to tablet
        tablet_form = next(
            (f for f in MEDICATION_DOSE_FORMS if "Tablet" in f.get("display", "")), MEDICATION_DOSE_FORMS[0]
        )
        med["form"] = {
            "coding": [
                {
                    "system": SNOMED_SYSTEM,
                    "code": tablet_form["code"],
                    "display": tablet_form["display"],
                }
            ],
            "text": tablet_form["display"],
        }
        return med

    def generate_injection(
        self,
        medication_id: str | None = None,
        manufacturer_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate an injection medication.

        Returns:
            Medication resource for an injection formulation
        """
        med = self.generate(
            medication_id=medication_id,
            manufacturer_ref=manufacturer_ref,
        )
        # Override form to injection
        injection_form = next(
            (f for f in MEDICATION_DOSE_FORMS if "Injection" in f.get("display", "")), MEDICATION_DOSE_FORMS[0]
        )
        med["form"] = {
            "coding": [
                {
                    "system": SNOMED_SYSTEM,
                    "code": injection_form["code"],
                    "display": injection_form["display"],
                }
            ],
            "text": injection_form["display"],
        }
        return med
