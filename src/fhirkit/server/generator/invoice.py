"""Invoice resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class InvoiceGenerator(FHIRResourceGenerator):
    """Generator for FHIR Invoice resources."""

    STATUS_CODES = ["draft", "issued", "balanced", "cancelled", "entered-in-error"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        invoice_id: str | None = None,
        status: str | None = None,
        subject_reference: str | None = None,
        date: str | None = None,
        issuer_reference: str | None = None,
        total_net: float | None = None,
        total_gross: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an Invoice resource."""
        if invoice_id is None:
            invoice_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:3])

        if date is None:
            date = datetime.now().isoformat()

        if total_net is None:
            total_net = float(self.faker.random_int(100, 5000))

        if total_gross is None:
            total_gross = total_net * 1.08

        invoice: dict[str, Any] = {
            "resourceType": "Invoice",
            "id": invoice_id,
            "status": status,
            "date": date,
            "totalNet": {"value": total_net, "currency": "USD"},
            "totalGross": {"value": total_gross, "currency": "USD"},
        }

        if subject_reference:
            invoice["subject"] = {"reference": subject_reference}
        else:
            invoice["subject"] = {"reference": f"Patient/{self._generate_id()}"}

        if issuer_reference:
            invoice["issuer"] = {"reference": issuer_reference}

        return invoice
