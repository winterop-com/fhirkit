"""PaymentReconciliation resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class PaymentReconciliationGenerator(FHIRResourceGenerator):
    """Generator for FHIR PaymentReconciliation resources."""

    OUTCOME_CODES = ["queued", "complete", "error", "partial"]

    DETAIL_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/payment-type",
            "code": "payment",
            "display": "Payment",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/payment-type",
            "code": "adjustment",
            "display": "Adjustment",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/payment-type",
            "code": "advance",
            "display": "Advance",
        },
    ]

    FORM_CODES = [
        {"code": "1", "display": "Check"},
        {"code": "2", "display": "Electronic Funds Transfer"},
        {"code": "3", "display": "Virtual Payment Card"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        reconciliation_id: str | None = None,
        status: str = "active",
        period_start: str | None = None,
        period_end: str | None = None,
        created: str | None = None,
        payment_issuer_reference: str | None = None,
        payment_date: str | None = None,
        payment_amount: float | None = None,
        outcome: str | None = None,
        disposition: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PaymentReconciliation resource.

        Args:
            reconciliation_id: Resource ID (generates UUID if None)
            status: Reconciliation status
            period_start: Period start date
            period_end: Period end date
            created: Creation date
            payment_issuer_reference: Reference to issuer Organization
            payment_date: Date of payment
            payment_amount: Total payment amount
            outcome: Processing outcome
            disposition: Disposition message

        Returns:
            PaymentReconciliation FHIR resource
        """
        if reconciliation_id is None:
            reconciliation_id = self._generate_id()

        if created is None:
            created = datetime.now().isoformat()

        if payment_date is None:
            payment_date = self.faker.date_between(start_date="-30d", end_date="today").isoformat()

        if period_start is None:
            period_start = self.faker.date_between(start_date="-60d", end_date="-30d").isoformat()

        if period_end is None:
            period_end = payment_date

        if payment_amount is None:
            payment_amount = float(self.faker.random_int(1000, 100000))

        if outcome is None:
            outcome = self.faker.random_element(self.OUTCOME_CODES[:2])

        if disposition is None:
            disposition = "Payment processed successfully"

        form_code = self.faker.random_element(self.FORM_CODES)

        reconciliation: dict[str, Any] = {
            "resourceType": "PaymentReconciliation",
            "id": reconciliation_id,
            "status": status,
            "period": {
                "start": period_start,
                "end": period_end,
            },
            "created": created,
            "paymentDate": payment_date,
            "paymentAmount": {
                "value": payment_amount,
                "currency": "USD",
            },
            "outcome": outcome,
            "disposition": disposition,
            "formCode": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/forms-codes",
                        "code": form_code["code"],
                        "display": form_code["display"],
                    }
                ],
            },
        }

        # Add payment issuer reference
        if payment_issuer_reference:
            reconciliation["paymentIssuer"] = {"reference": payment_issuer_reference}
        else:
            reconciliation["paymentIssuer"] = {"reference": f"Organization/{self._generate_id()}"}

        # Add payment identifier
        reconciliation["paymentIdentifier"] = {
            "system": "http://example.org/payment-ids",
            "value": f"PAY-{self.faker.random_number(digits=10, fix_len=True)}",
        }

        # Add detail items
        num_details = self.faker.random_int(1, 3)
        details = []
        for i in range(num_details):
            detail_type = self.faker.random_element(self.DETAIL_TYPES)
            detail_amount = float(self.faker.random_int(100, int(payment_amount / num_details)))
            details.append(
                {
                    "type": {
                        "coding": [detail_type],
                    },
                    "date": payment_date,
                    "amount": {
                        "value": detail_amount,
                        "currency": "USD",
                    },
                }
            )
        reconciliation["detail"] = details

        return reconciliation

    def generate_for_organization(
        self,
        organization_id: str,
        payment_amount: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a PaymentReconciliation for an organization.

        Args:
            organization_id: Organization ID
            payment_amount: Total payment amount

        Returns:
            PaymentReconciliation FHIR resource
        """
        return self.generate(
            payment_issuer_reference=f"Organization/{organization_id}",
            payment_amount=payment_amount,
            **kwargs,
        )
