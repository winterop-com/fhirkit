"""Account resource generator."""

from datetime import datetime, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class AccountGenerator(FHIRResourceGenerator):
    """Generator for FHIR Account resources."""

    ACCOUNT_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "PBILLACCT",
            "display": "patient billing account",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "ACCTRECEIVABLE",
            "display": "account receivable",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "CASH",
            "display": "Cash",
        },
    ]

    ACCOUNT_STATUSES = ["active", "inactive", "entered-in-error", "on-hold", "unknown"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        account_id: str | None = None,
        status: str | None = None,
        account_type: dict[str, Any] | None = None,
        name: str | None = None,
        subject_reference: str | None = None,
        service_period_start: str | None = None,
        service_period_end: str | None = None,
        owner_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Account resource.

        Args:
            account_id: Resource ID (generates UUID if None)
            status: Account status (active, inactive, etc.)
            account_type: Type of account
            name: Human readable account name
            subject_reference: Reference to Patient or other subject
            service_period_start: Start of service period
            service_period_end: End of service period
            owner_reference: Reference to Organization that owns account

        Returns:
            Account FHIR resource
        """
        if account_id is None:
            account_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.ACCOUNT_STATUSES[:2])

        if account_type is None:
            account_type = self.faker.random_element(self.ACCOUNT_TYPES)

        if name is None:
            name = f"Account {self.faker.random_number(digits=6, fix_len=True)}"

        # Generate service period
        if service_period_start is None:
            start_date = self.faker.date_between(start_date="-1y", end_date="today")
            service_period_start = start_date.isoformat()
        else:
            start_date = datetime.fromisoformat(service_period_start).date()

        if service_period_end is None:
            end_date = start_date + timedelta(days=self.faker.random_int(30, 365))
            service_period_end = end_date.isoformat()

        account: dict[str, Any] = {
            "resourceType": "Account",
            "id": account_id,
            "status": status,
            "type": {
                "coding": [account_type],
                "text": account_type["display"],
            },
            "name": name,
            "servicePeriod": {
                "start": service_period_start,
                "end": service_period_end,
            },
        }

        # Add subject if provided
        if subject_reference:
            account["subject"] = [{"reference": subject_reference}]

        # Add owner if provided
        if owner_reference:
            account["owner"] = {"reference": owner_reference}

        # Add description
        account["description"] = "Billing account for patient services"

        return account

    def generate_for_patient(
        self,
        patient_id: str,
        organization_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Account for a specific patient.

        Args:
            patient_id: Patient ID
            organization_id: Optional organization ID

        Returns:
            Account FHIR resource
        """
        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            owner_reference=f"Organization/{organization_id}" if organization_id else None,
            **kwargs,
        )
