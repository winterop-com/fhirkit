"""EnrollmentResponse resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class EnrollmentResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR EnrollmentResponse resources."""

    STATUS_CODES = ["active", "cancelled", "draft", "entered-in-error"]

    OUTCOME_CODES = ["queued", "complete", "error", "partial"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        status: str = "active",
        outcome: str | None = None,
        disposition: str | None = None,
        created: str | None = None,
        organization_reference: str | None = None,
        request_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EnrollmentResponse resource.

        Args:
            response_id: Resource ID (generates UUID if None)
            status: Response status
            outcome: Processing outcome
            disposition: Disposition message
            created: Creation date
            organization_reference: Reference to insurance organization
            request_reference: Reference to EnrollmentRequest

        Returns:
            EnrollmentResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        if outcome is None:
            outcome = self.faker.random_element(self.OUTCOME_CODES[:2])

        if created is None:
            created = datetime.now(timezone.utc).isoformat()

        enrollment_response: dict[str, Any] = {
            "resourceType": "EnrollmentResponse",
            "id": response_id,
            "meta": self._generate_meta(),
            "status": status,
            "outcome": outcome,
            "created": created,
        }

        # Add identifier
        enrollment_response["identifier"] = [
            {
                "system": "http://example.org/enrollment-responses",
                "value": f"ENRR-{self.faker.random_number(digits=8, fix_len=True)}",
            }
        ]

        # Add request reference
        if request_reference:
            enrollment_response["request"] = {"reference": request_reference}

        # Add organization
        if organization_reference:
            enrollment_response["organization"] = {"reference": organization_reference}
        else:
            enrollment_response["organization"] = {
                "reference": f"Organization/{self._generate_id()}",
                "display": f"{self.faker.company()} Insurance",
            }

        # Add disposition based on outcome
        if disposition:
            enrollment_response["disposition"] = disposition
        else:
            if outcome == "complete":
                enrollment_response["disposition"] = "Enrollment request processed successfully"
            elif outcome == "error":
                enrollment_response["disposition"] = "Unable to process enrollment request"
            elif outcome == "partial":
                enrollment_response["disposition"] = "Enrollment request partially processed"
            else:
                enrollment_response["disposition"] = "Enrollment request queued for processing"

        return enrollment_response

    def generate_for_request(
        self,
        request_id: str,
        outcome: str = "complete",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an EnrollmentResponse for a specific request.

        Args:
            request_id: EnrollmentRequest ID
            outcome: Processing outcome

        Returns:
            EnrollmentResponse FHIR resource
        """
        return self.generate(
            request_reference=f"EnrollmentRequest/{request_id}",
            outcome=outcome,
            **kwargs,
        )
