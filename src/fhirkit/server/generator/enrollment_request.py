"""EnrollmentRequest resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EnrollmentRequestGenerator(FHIRResourceGenerator):
    """Generator for FHIR EnrollmentRequest resources."""

    STATUS_CODES = ["active", "cancelled", "draft", "entered-in-error"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        request_id: str | None = None,
        status: str = "active",
        created: str | None = None,
        insurer_reference: str | None = None,
        provider_reference: str | None = None,
        candidate_reference: str | None = None,
        coverage_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EnrollmentRequest resource.

        Args:
            request_id: Resource ID (generates UUID if None)
            status: Request status
            created: Creation date
            insurer_reference: Reference to insurance organization
            provider_reference: Reference to requesting provider
            candidate_reference: Reference to patient
            coverage_reference: Reference to coverage

        Returns:
            EnrollmentRequest FHIR resource
        """
        if request_id is None:
            request_id = self._generate_id()

        if created is None:
            created = datetime.now(timezone.utc).isoformat()

        enrollment_request: dict[str, Any] = {
            "resourceType": "EnrollmentRequest",
            "id": request_id,
            "meta": self._generate_meta(),
            "status": status,
            "created": created,
        }

        # Add identifier
        enrollment_request["identifier"] = [
            {
                "system": "http://example.org/enrollment-requests",
                "value": f"ENR-{self.faker.random_number(digits=8, fix_len=True)}",
            }
        ]

        # Add insurer
        if insurer_reference:
            enrollment_request["insurer"] = {"reference": insurer_reference}
        else:
            enrollment_request["insurer"] = {
                "reference": f"Organization/{self._generate_id()}",
                "display": f"{self.faker.company()} Insurance",
            }

        # Add provider
        if provider_reference:
            enrollment_request["provider"] = {"reference": provider_reference}
        elif self.faker.boolean(chance_of_getting_true=70):
            enrollment_request["provider"] = {
                "reference": f"Practitioner/{self._generate_id()}",
                "display": f"Dr. {self.faker.last_name()}",
            }

        # Add candidate
        if candidate_reference:
            enrollment_request["candidate"] = {"reference": candidate_reference}
        else:
            enrollment_request["candidate"] = {
                "reference": f"Patient/{self._generate_id()}",
            }

        # Add coverage
        if coverage_reference:
            enrollment_request["coverage"] = {"reference": coverage_reference}

        return enrollment_request

    def generate_for_patient(
        self,
        patient_id: str,
        insurer_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EnrollmentRequest for a specific patient.

        Args:
            patient_id: Patient ID
            insurer_id: Optional insurer organization ID

        Returns:
            EnrollmentRequest FHIR resource
        """
        return self.generate(
            candidate_reference=f"Patient/{patient_id}",
            insurer_reference=f"Organization/{insurer_id}" if insurer_id else None,
            **kwargs,
        )
