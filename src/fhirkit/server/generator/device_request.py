"""DeviceRequest resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class DeviceRequestGenerator(FHIRResourceGenerator):
    """Generator for FHIR DeviceRequest resources."""

    STATUS_CODES = [
        "draft",
        "active",
        "on-hold",
        "revoked",
        "completed",
        "entered-in-error",
        "unknown",
    ]

    INTENT_CODES = [
        "proposal",
        "plan",
        "directive",
        "order",
        "original-order",
        "reflex-order",
        "filler-order",
        "instance-order",
        "option",
    ]

    PRIORITY_CODES = ["routine", "urgent", "asap", "stat"]

    DEVICE_TYPES = [
        {
            "system": "http://snomed.info/sct",
            "code": "14106009",
            "display": "Cardiac pacemaker",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "43252007",
            "display": "Cochlear implant",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "303619003",
            "display": "Continuous positive airway pressure unit",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "702172008",
            "display": "Home blood pressure monitor",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "469591008",
            "display": "Hospital bed",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "23562009",
            "display": "Glucose meter",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "37874008",
            "display": "Oxygen concentrator",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "261956002",
            "display": "Wheelchair",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        request_id: str | None = None,
        status: str | None = None,
        intent: str | None = None,
        priority: str | None = None,
        device_code: dict[str, Any] | None = None,
        device_reference: str | None = None,
        subject_reference: str | None = None,
        encounter_reference: str | None = None,
        authored_on: str | None = None,
        requester_reference: str | None = None,
        performer_reference: str | None = None,
        reason_codes: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DeviceRequest resource.

        Args:
            request_id: Resource ID (generates UUID if None)
            status: Request status
            intent: Request intent
            priority: Request priority
            device_code: CodeableConcept for device type
            device_reference: Reference to Device resource
            subject_reference: Reference to Patient
            encounter_reference: Reference to Encounter
            authored_on: When the request was authored
            requester_reference: Reference to requester
            performer_reference: Reference to performer
            reason_codes: Reason codes for the request

        Returns:
            DeviceRequest FHIR resource
        """
        if request_id is None:
            request_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:3])

        if intent is None:
            intent = self.faker.random_element(self.INTENT_CODES[:4])

        if device_code is None and device_reference is None:
            device_code = self.faker.random_element(self.DEVICE_TYPES)

        if authored_on is None:
            authored_on = datetime.now().isoformat()

        request: dict[str, Any] = {
            "resourceType": "DeviceRequest",
            "id": request_id,
            "status": status,
            "intent": intent,
            "authoredOn": authored_on,
        }

        # Add device code or reference
        if device_code:
            request["codeCodeableConcept"] = {
                "coding": [device_code],
                "text": device_code["display"],
            }
        elif device_reference:
            request["codeReference"] = {"reference": device_reference}

        # Add subject reference
        if subject_reference:
            request["subject"] = {"reference": subject_reference}
        else:
            request["subject"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add encounter reference
        if encounter_reference:
            request["encounter"] = {"reference": encounter_reference}

        # Add priority
        if priority:
            request["priority"] = priority
        elif self.faker.boolean(chance_of_getting_true=40):
            request["priority"] = self.faker.random_element(self.PRIORITY_CODES)

        # Add requester reference
        if requester_reference:
            request["requester"] = {"reference": requester_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            request["requester"] = {
                "reference": f"Practitioner/{self._generate_id()}",
            }

        # Add performer reference
        if performer_reference:
            request["performer"] = {"reference": performer_reference}

        # Add reason codes
        if reason_codes:
            request["reasonCode"] = [{"coding": [code], "text": code.get("display", "")} for code in reason_codes]

        # Add occurrence timing
        if self.faker.boolean(chance_of_getting_true=50):
            future_date = self.faker.date_between(start_date="today", end_date="+30d").isoformat()
            request["occurrenceDateTime"] = future_date

        return request

    def generate_for_patient(
        self,
        patient_id: str,
        device_code: dict[str, Any] | None = None,
        requester_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DeviceRequest for a specific patient.

        Args:
            patient_id: Patient ID
            device_code: Device type code
            requester_id: Requester practitioner ID

        Returns:
            DeviceRequest FHIR resource
        """
        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            device_code=device_code,
            requester_reference=(f"Practitioner/{requester_id}" if requester_id else None),
            **kwargs,
        )
