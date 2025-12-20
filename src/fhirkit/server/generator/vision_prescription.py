"""VisionPrescription resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class VisionPrescriptionGenerator(FHIRResourceGenerator):
    """Generator for FHIR VisionPrescription resources."""

    STATUS_CODES = ["active", "cancelled", "draft", "entered-in-error"]

    PRODUCT_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-visionprescriptionproduct",
            "code": "lens",
            "display": "Lens",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/ex-visionprescriptionproduct",
            "code": "contact",
            "display": "Contact Lens",
        },
    ]

    EYE_CODES = ["right", "left"]

    BASE_CODES = ["up", "down", "in", "out"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        prescription_id: str | None = None,
        status: str | None = None,
        patient_reference: str | None = None,
        encounter_reference: str | None = None,
        date_written: str | None = None,
        prescriber_reference: str | None = None,
        lens_specifications: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a VisionPrescription resource.

        Args:
            prescription_id: Resource ID (generates UUID if None)
            status: Prescription status
            patient_reference: Reference to Patient
            encounter_reference: Reference to Encounter
            date_written: Date prescription was written
            prescriber_reference: Reference to prescriber Practitioner
            lens_specifications: Lens specification details

        Returns:
            VisionPrescription FHIR resource
        """
        if prescription_id is None:
            prescription_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:2])

        if date_written is None:
            date_written = datetime.now().strftime("%Y-%m-%d")

        prescription: dict[str, Any] = {
            "resourceType": "VisionPrescription",
            "id": prescription_id,
            "status": status,
            "created": date_written,
            "dateWritten": date_written,
        }

        # Add patient reference
        if patient_reference:
            prescription["patient"] = {"reference": patient_reference}
        else:
            prescription["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add encounter reference
        if encounter_reference:
            prescription["encounter"] = {"reference": encounter_reference}

        # Add prescriber reference
        if prescriber_reference:
            prescription["prescriber"] = {"reference": prescriber_reference}
        else:
            prescription["prescriber"] = {"reference": f"Practitioner/{self._generate_id()}"}

        # Add lens specifications
        if lens_specifications:
            prescription["lensSpecification"] = lens_specifications
        else:
            prescription["lensSpecification"] = self._generate_lens_specs()

        return prescription

    def _generate_lens_specs(self) -> list[dict[str, Any]]:
        """Generate lens specifications for both eyes."""
        specs = []

        for eye in self.EYE_CODES:
            product = self.faker.random_element(self.PRODUCT_CODES)
            spec: dict[str, Any] = {
                "product": {
                    "coding": [product],
                },
                "eye": eye,
            }

            # Add sphere (diopters)
            sphere = round(self.faker.pyfloat(min_value=-10, max_value=10), 2)
            spec["sphere"] = sphere

            # Add cylinder (diopters) - sometimes needed for astigmatism
            if self.faker.boolean(chance_of_getting_true=60):
                cylinder = round(self.faker.pyfloat(min_value=-4, max_value=4), 2)
                spec["cylinder"] = cylinder
                spec["axis"] = self.faker.random_int(1, 180)

            # Add prism if needed
            if self.faker.boolean(chance_of_getting_true=20):
                spec["prism"] = [
                    {
                        "amount": round(self.faker.pyfloat(min_value=0.5, max_value=5), 2),
                        "base": self.faker.random_element(self.BASE_CODES),
                    }
                ]

            # Add add power for reading glasses
            if self.faker.boolean(chance_of_getting_true=40):
                spec["add"] = round(self.faker.pyfloat(min_value=0.75, max_value=3.5), 2)

            specs.append(spec)

        return specs

    def generate_for_patient(
        self,
        patient_id: str,
        prescriber_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a VisionPrescription for a patient.

        Args:
            patient_id: Patient ID
            prescriber_id: Prescriber Practitioner ID

        Returns:
            VisionPrescription FHIR resource
        """
        return self.generate(
            patient_reference=f"Patient/{patient_id}",
            prescriber_reference=(f"Practitioner/{prescriber_id}" if prescriber_id else None),
            **kwargs,
        )
