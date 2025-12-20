"""VerificationResult resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class VerificationResultGenerator(FHIRResourceGenerator):
    """Generator for FHIR VerificationResult resources."""

    STATUS_CODES = [
        "attested",
        "validated",
        "in-process",
        "req-revalid",
        "val-fail",
        "reval-fail",
    ]

    VALIDATION_TYPES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/validation-type",
            "code": "nothing",
            "display": "Nothing",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/validation-type",
            "code": "primary",
            "display": "Primary Source",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/validation-type",
            "code": "multi",
            "display": "Multiple Sources",
        },
    ]

    NEED_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/need",
            "code": "none",
            "display": "None",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/need",
            "code": "initial",
            "display": "Initial",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/need",
            "code": "periodic",
            "display": "Periodic",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        result_id: str | None = None,
        status: str | None = None,
        target_references: list[str] | None = None,
        validation_type: dict[str, Any] | None = None,
        need: dict[str, Any] | None = None,
        status_date: str | None = None,
        frequency: dict[str, Any] | None = None,
        last_performed: str | None = None,
        next_scheduled: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a VerificationResult resource.

        Args:
            result_id: Resource ID (generates UUID if None)
            status: Verification status
            target_references: References to verified resources
            validation_type: Type of validation
            need: Validation need
            status_date: When status was set
            frequency: How often revalidation is needed
            last_performed: When last performed
            next_scheduled: When next scheduled

        Returns:
            VerificationResult FHIR resource
        """
        if result_id is None:
            result_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:2])

        if status_date is None:
            status_date = datetime.now(timezone.utc).isoformat()

        verification_result: dict[str, Any] = {
            "resourceType": "VerificationResult",
            "id": result_id,
            "meta": self._generate_meta(),
            "status": status,
            "statusDate": status_date,
        }

        # Add target references
        if target_references:
            verification_result["target"] = [{"reference": ref} for ref in target_references]
        else:
            # Default to practitioner or organization verification
            verification_result["target"] = [{"reference": f"Practitioner/{self._generate_id()}"}]

        # Add validation type
        if validation_type:
            verification_result["validationType"] = {"coding": [validation_type]}
        else:
            vtype = self.faker.random_element(self.VALIDATION_TYPES)
            verification_result["validationType"] = {
                "coding": [vtype],
                "text": vtype["display"],
            }

        # Add need
        if need:
            verification_result["need"] = {"coding": [need]}
        else:
            need_code = self.faker.random_element(self.NEED_CODES)
            verification_result["need"] = {
                "coding": [need_code],
                "text": need_code["display"],
            }

        # Add frequency
        if frequency:
            verification_result["frequency"] = frequency
        elif self.faker.boolean(chance_of_getting_true=60):
            verification_result["frequency"] = {
                "repeat": {
                    "frequency": 1,
                    "period": 1,
                    "periodUnit": "a",  # annually
                }
            }

        # Add last performed
        if last_performed:
            verification_result["lastPerformed"] = last_performed
        elif status in ["validated", "attested"]:
            last = datetime.now(timezone.utc) - timedelta(days=self.faker.random_int(1, 180))
            verification_result["lastPerformed"] = last.isoformat()

        # Add next scheduled
        if next_scheduled:
            verification_result["nextScheduled"] = next_scheduled
        elif status == "validated" and self.faker.boolean(chance_of_getting_true=70):
            next_date = datetime.now(timezone.utc) + timedelta(days=self.faker.random_int(180, 365))
            verification_result["nextScheduled"] = next_date.strftime("%Y-%m-%d")

        return verification_result

    def generate_for_practitioner(
        self,
        practitioner_id: str,
        status: str = "validated",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a VerificationResult for a practitioner.

        Args:
            practitioner_id: Practitioner ID
            status: Verification status

        Returns:
            VerificationResult FHIR resource
        """
        return self.generate(
            status=status,
            target_references=[f"Practitioner/{practitioner_id}"],
            **kwargs,
        )
