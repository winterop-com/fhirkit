"""PaymentNotice resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class PaymentNoticeGenerator(FHIRResourceGenerator):
    """Generator for FHIR PaymentNotice resources."""

    PAYMENT_STATUSES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/paymentstatus",
            "code": "paid",
            "display": "Paid",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/paymentstatus",
            "code": "cleared",
            "display": "Cleared",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        notice_id: str | None = None,
        status: str = "active",
        payment_date: str | None = None,
        created: str | None = None,
        recipient_reference: str | None = None,
        provider_reference: str | None = None,
        request_reference: str | None = None,
        response_reference: str | None = None,
        payment_reference: str | None = None,
        amount: float | None = None,
        payment_status: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PaymentNotice resource.

        Args:
            notice_id: Resource ID (generates UUID if None)
            status: Notice status
            payment_date: Date of payment
            created: Creation date
            recipient_reference: Reference to recipient Organization
            provider_reference: Reference to provider Practitioner/Organization
            request_reference: Reference to request resource
            response_reference: Reference to response resource
            payment_reference: Reference to PaymentReconciliation
            amount: Payment amount
            payment_status: Payment status code

        Returns:
            PaymentNotice FHIR resource
        """
        if notice_id is None:
            notice_id = self._generate_id()

        if created is None:
            created = datetime.now().isoformat()

        if payment_date is None:
            payment_date = self.faker.date_between(start_date="-30d", end_date="today").isoformat()

        if amount is None:
            amount = float(self.faker.random_int(100, 10000))

        if payment_status is None:
            payment_status = self.faker.random_element(self.PAYMENT_STATUSES)

        notice: dict[str, Any] = {
            "resourceType": "PaymentNotice",
            "id": notice_id,
            "status": status,
            "created": created,
            "paymentDate": payment_date,
            "amount": {
                "value": amount,
                "currency": "USD",
            },
            "paymentStatus": {
                "coding": [payment_status],
            },
        }

        # Add recipient reference
        if recipient_reference:
            notice["recipient"] = {"reference": recipient_reference}
        else:
            notice["recipient"] = {"reference": f"Organization/{self._generate_id()}"}

        # Add provider reference
        if provider_reference:
            notice["provider"] = {"reference": provider_reference}

        # Add request reference if provided
        if request_reference:
            notice["request"] = {"reference": request_reference}

        # Add response reference if provided
        if response_reference:
            notice["response"] = {"reference": response_reference}

        # Add payment reference if provided
        if payment_reference:
            notice["payment"] = {"reference": payment_reference}

        return notice

    def generate_for_claim(
        self,
        claim_id: str,
        claim_response_id: str | None = None,
        amount: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PaymentNotice for a claim.

        Args:
            claim_id: Claim ID
            claim_response_id: ClaimResponse ID
            amount: Payment amount

        Returns:
            PaymentNotice FHIR resource
        """
        return self.generate(
            request_reference=f"Claim/{claim_id}",
            response_reference=(f"ClaimResponse/{claim_response_id}" if claim_response_id else None),
            amount=amount,
            **kwargs,
        )
