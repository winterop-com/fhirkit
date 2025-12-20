"""ChargeItem resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ChargeItemGenerator(FHIRResourceGenerator):
    """Generator for FHIR ChargeItem resources."""

    STATUS_CODES = [
        "planned",
        "billable",
        "not-billable",
        "aborted",
        "billed",
        "entered-in-error",
        "unknown",
    ]

    CHARGE_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/chargeitem-billingcodes",
            "code": "1100",
            "display": "Unspecified room and board charge",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/chargeitem-billingcodes",
            "code": "1210",
            "display": "Medical/surgical nursing care charge",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/chargeitem-billingcodes",
            "code": "1310",
            "display": "ICU nursing care charge",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "243114000",
            "display": "Laboratory procedure",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "429858000",
            "display": "Diagnostic imaging procedure",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "387713003",
            "display": "Surgical procedure",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        charge_id: str | None = None,
        status: str | None = None,
        code: dict[str, Any] | None = None,
        subject_reference: str | None = None,
        context_reference: str | None = None,
        occurrence_datetime: str | None = None,
        performer_reference: str | None = None,
        performing_organization_reference: str | None = None,
        requesting_organization_reference: str | None = None,
        quantity: float | None = None,
        price_override: dict[str, Any] | None = None,
        enterer_reference: str | None = None,
        entered_date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ChargeItem resource.

        Args:
            charge_id: Resource ID (generates UUID if None)
            status: Charge item status
            code: Charge code
            subject_reference: Reference to Patient
            context_reference: Reference to Encounter or EpisodeOfCare
            occurrence_datetime: When the service was provided
            performer_reference: Reference to performer
            performing_organization_reference: Ref to performing org
            requesting_organization_reference: Ref to requesting org
            quantity: Quantity of charges
            price_override: Override price
            enterer_reference: Reference to enterer
            entered_date: Date entered

        Returns:
            ChargeItem FHIR resource
        """
        if charge_id is None:
            charge_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:3])

        if code is None:
            code = self.faker.random_element(self.CHARGE_CODES)

        if occurrence_datetime is None:
            occurrence_datetime = datetime.now().isoformat()

        charge: dict[str, Any] = {
            "resourceType": "ChargeItem",
            "id": charge_id,
            "status": status,
            "code": {
                "coding": [code],
                "text": code["display"],
            },
            "occurrenceDateTime": occurrence_datetime,
        }

        # Add subject reference
        if subject_reference:
            charge["subject"] = {"reference": subject_reference}
        else:
            charge["subject"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add context reference
        if context_reference:
            charge["context"] = {"reference": context_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            charge["context"] = {"reference": f"Encounter/{self._generate_id()}"}

        # Add performer
        if performer_reference:
            charge["performer"] = [
                {
                    "actor": {"reference": performer_reference},
                }
            ]
        elif self.faker.boolean(chance_of_getting_true=60):
            charge["performer"] = [
                {
                    "actor": {"reference": f"Practitioner/{self._generate_id()}"},
                }
            ]

        # Add performing organization
        if performing_organization_reference:
            charge["performingOrganization"] = {"reference": performing_organization_reference}

        # Add requesting organization
        if requesting_organization_reference:
            charge["requestingOrganization"] = {"reference": requesting_organization_reference}

        # Add quantity
        if quantity:
            charge["quantity"] = {"value": quantity}
        else:
            charge["quantity"] = {"value": 1}

        # Add price override
        if price_override:
            charge["priceOverride"] = price_override
        elif self.faker.boolean(chance_of_getting_true=50):
            charge["priceOverride"] = {
                "value": float(self.faker.random_int(50, 5000)),
                "currency": "USD",
            }

        # Add enterer
        if enterer_reference:
            charge["enterer"] = {"reference": enterer_reference}

        # Add entered date
        if entered_date:
            charge["enteredDate"] = entered_date
        else:
            charge["enteredDate"] = datetime.now().isoformat()

        return charge

    def generate_for_encounter(
        self,
        patient_id: str,
        encounter_id: str,
        code: dict[str, Any] | None = None,
        quantity: float = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ChargeItem for an encounter.

        Args:
            patient_id: Patient ID
            encounter_id: Encounter ID
            code: Charge code
            quantity: Quantity

        Returns:
            ChargeItem FHIR resource
        """
        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            context_reference=f"Encounter/{encounter_id}",
            code=code,
            quantity=quantity,
            **kwargs,
        )
