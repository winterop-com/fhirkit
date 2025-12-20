"""DeviceUseStatement resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class DeviceUseStatementGenerator(FHIRResourceGenerator):
    """Generator for FHIR DeviceUseStatement resources."""

    STATUS_CODES = ["active", "completed", "entered-in-error", "intended", "stopped", "on-hold"]

    BODY_SITES = [
        {
            "system": "http://snomed.info/sct",
            "code": "368208006",
            "display": "Left upper arm",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "368209003",
            "display": "Right upper arm",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "7569003",
            "display": "Finger",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "774007",
            "display": "Head and neck",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "51185008",
            "display": "Thorax",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        statement_id: str | None = None,
        status: str | None = None,
        subject_reference: str | None = None,
        device_reference: str | None = None,
        timing_period_start: str | None = None,
        timing_period_end: str | None = None,
        body_site: dict[str, Any] | None = None,
        reason_references: list[str] | None = None,
        source_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DeviceUseStatement resource.

        Args:
            statement_id: Resource ID (generates UUID if None)
            status: Statement status
            subject_reference: Reference to Patient
            device_reference: Reference to Device
            timing_period_start: Start of usage period
            timing_period_end: End of usage period
            body_site: Body site where device is used
            reason_references: References to conditions/observations
            source_reference: Reference to source of information

        Returns:
            DeviceUseStatement FHIR resource
        """
        if statement_id is None:
            statement_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:2])

        statement: dict[str, Any] = {
            "resourceType": "DeviceUseStatement",
            "id": statement_id,
            "meta": self._generate_meta(),
            "status": status,
        }

        # Add subject
        if subject_reference:
            statement["subject"] = {"reference": subject_reference}
        else:
            statement["subject"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add device reference
        if device_reference:
            statement["device"] = {"reference": device_reference}
        else:
            statement["device"] = {"reference": f"Device/{self._generate_id()}"}

        # Add timing
        if timing_period_start is None:
            start_date = self.faker.date_between(start_date="-1y", end_date="today")
            timing_period_start = start_date.isoformat()
        else:
            start_date = datetime.fromisoformat(timing_period_start).date()

        if timing_period_end is None and status == "completed":
            end_date = start_date + timedelta(days=self.faker.random_int(1, 180))
            timing_period_end = end_date.isoformat()

        statement["timingPeriod"] = {"start": timing_period_start}
        if timing_period_end:
            statement["timingPeriod"]["end"] = timing_period_end

        # Add recorded on date
        statement["recordedOn"] = datetime.now(timezone.utc).isoformat()

        # Add body site
        if body_site:
            statement["bodySite"] = body_site
        elif self.faker.boolean(chance_of_getting_true=60):
            site = self.faker.random_element(self.BODY_SITES)
            statement["bodySite"] = {"coding": [site], "text": site["display"]}

        # Add reason references
        if reason_references:
            statement["reasonReference"] = [{"reference": ref} for ref in reason_references]

        # Add source
        if source_reference:
            statement["source"] = {"reference": source_reference}

        return statement

    def generate_for_patient(
        self,
        patient_id: str,
        device_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DeviceUseStatement for a specific patient.

        Args:
            patient_id: Patient ID
            device_id: Optional device ID

        Returns:
            DeviceUseStatement FHIR resource
        """
        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            device_reference=f"Device/{device_id}" if device_id else None,
            **kwargs,
        )
