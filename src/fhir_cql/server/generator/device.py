"""Device resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class DeviceGenerator(FHIRResourceGenerator):
    """Generator for FHIR Device resources."""

    # Device types (SNOMED CT)
    DEVICE_TYPES = [
        {"code": "43770009", "display": "Sphygmomanometer", "system": "http://snomed.info/sct"},
        {"code": "19257004", "display": "Defibrillator", "system": "http://snomed.info/sct"},
        {"code": "303607000", "display": "Cochlear implant", "system": "http://snomed.info/sct"},
        {"code": "272265001", "display": "Bone prosthesis", "system": "http://snomed.info/sct"},
        {"code": "37299003", "display": "Glucose monitor", "system": "http://snomed.info/sct"},
        {"code": "53350007", "display": "Pacemaker", "system": "http://snomed.info/sct"},
        {"code": "462894001", "display": "Insulin pump", "system": "http://snomed.info/sct"},
        {"code": "360063003", "display": "CPAP unit", "system": "http://snomed.info/sct"},
        {"code": "304070002", "display": "Wheelchair", "system": "http://snomed.info/sct"},
        {"code": "702127004", "display": "Pulse oximeter", "system": "http://snomed.info/sct"},
    ]

    # Device status codes
    STATUS_CODES = ["active", "inactive", "entered-in-error", "unknown"]

    # Device name types
    NAME_TYPES = ["udi-label-name", "user-friendly-name", "patient-reported-name", "manufacturer-name", "model-name"]

    # Manufacturers
    MANUFACTURERS = [
        "Medtronic",
        "Abbott",
        "Boston Scientific",
        "Philips Healthcare",
        "GE Healthcare",
        "Siemens Healthineers",
        "Johnson & Johnson",
        "Stryker",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        device_id: str | None = None,
        patient_ref: str | None = None,
        owner_ref: str | None = None,
        location_ref: str | None = None,
        device_type: str | None = None,
        status: str = "active",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Device resource.

        Args:
            device_id: Device ID (generates UUID if None)
            patient_ref: Reference to Patient (who uses the device)
            owner_ref: Reference to Organization (owner)
            location_ref: Reference to Location
            device_type: SNOMED CT device type code (random if None)
            status: Device status

        Returns:
            Device FHIR resource
        """
        if device_id is None:
            device_id = self._generate_id()

        # Select device type
        if device_type is None:
            type_coding = self.faker.random_element(self.DEVICE_TYPES)
        else:
            type_coding = next(
                (t for t in self.DEVICE_TYPES if t["code"] == device_type),
                self.DEVICE_TYPES[0],
            )

        manufacturer = self.faker.random_element(self.MANUFACTURERS)
        model_number = f"{self.faker.lexify('???').upper()}-{self.faker.numerify('####')}"
        serial_number = self.faker.numerify("SN-############")
        lot_number = f"LOT-{self.faker.numerify('####')}-{self.faker.lexify('??').upper()}"

        # Generate dates
        manufacture_year = self.faker.random_int(min=2019, max=2024)
        expiration_year = manufacture_year + self.faker.random_int(min=3, max=7)

        device: dict[str, Any] = {
            "resourceType": "Device",
            "id": device_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/device-ids",
                    value=f"DEV-{self.faker.numerify('########')}",
                ),
            ],
            "udiCarrier": [
                {
                    "deviceIdentifier": self.faker.numerify("##############"),
                    "carrierHRF": (
                        f"(01){self.faker.numerify('##############')}(17){manufacture_year}0101(10){lot_number}"
                    ),
                }
            ],
            "status": status,
            "manufacturer": manufacturer,
            "manufactureDate": f"{manufacture_year}-{self.faker.numerify('##')}-{self.faker.numerify('##')}".replace(
                "-0", "-1"
            ),
            "expirationDate": f"{expiration_year}-12-31",
            "lotNumber": lot_number,
            "serialNumber": serial_number,
            "deviceName": [
                {
                    "name": f"{manufacturer} {type_coding['display']}",
                    "type": "user-friendly-name",
                },
                {
                    "name": model_number,
                    "type": "model-name",
                },
            ],
            "modelNumber": model_number,
            "type": {
                "coding": [type_coding],
                "text": type_coding["display"],
            },
            "note": [
                {
                    "text": f"Device assigned for {'patient' if patient_ref else 'general'} use",
                }
            ],
        }

        if patient_ref:
            device["patient"] = {"reference": patient_ref}

        if owner_ref:
            device["owner"] = {"reference": owner_ref}

        if location_ref:
            device["location"] = {"reference": location_ref}

        return device
