"""OperationOutcome resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class OperationOutcomeGenerator(FHIRResourceGenerator):
    """Generator for FHIR OperationOutcome resources."""

    SEVERITY_CODES = ["fatal", "error", "warning", "information"]

    ISSUE_CODES = [
        "invalid",
        "structure",
        "required",
        "value",
        "invariant",
        "security",
        "login",
        "unknown",
        "expired",
        "forbidden",
        "suppressed",
        "processing",
        "not-supported",
        "duplicate",
        "multiple-matches",
        "not-found",
        "deleted",
        "too-long",
        "code-invalid",
        "extension",
        "too-costly",
        "business-rule",
        "conflict",
        "transient",
        "lock-error",
        "no-store",
        "exception",
        "timeout",
        "incomplete",
        "throttled",
        "informational",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        outcome_id: str | None = None,
        issues: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an OperationOutcome resource.

        Args:
            outcome_id: Resource ID (generates UUID if None)
            issues: List of issue details

        Returns:
            OperationOutcome FHIR resource
        """
        if outcome_id is None:
            outcome_id = self._generate_id()

        operation_outcome: dict[str, Any] = {
            "resourceType": "OperationOutcome",
            "id": outcome_id,
            "meta": self._generate_meta(),
        }

        if issues:
            operation_outcome["issue"] = issues
        else:
            operation_outcome["issue"] = [self._generate_issue()]

        return operation_outcome

    def _generate_issue(
        self,
        severity: str | None = None,
        code: str | None = None,
        diagnostics: str | None = None,
    ) -> dict[str, Any]:
        """Generate an issue."""
        if severity is None:
            severity = self.faker.random_element(self.SEVERITY_CODES)

        if code is None:
            code = self.faker.random_element(self.ISSUE_CODES)

        issue: dict[str, Any] = {
            "severity": severity,
            "code": code,
        }

        if diagnostics:
            issue["diagnostics"] = diagnostics
        else:
            issue["diagnostics"] = f"Operation {code}: {self.faker.sentence()}"

        return issue

    def generate_success(self, message: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Generate a successful OperationOutcome.

        Args:
            message: Success message

        Returns:
            OperationOutcome FHIR resource
        """
        issues = [
            {
                "severity": "information",
                "code": "informational",
                "diagnostics": message or "Operation completed successfully",
            }
        ]

        return self.generate(issues=issues, **kwargs)

    def generate_error(
        self,
        error_code: str = "processing",
        message: str | None = None,
        location: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an error OperationOutcome.

        Args:
            error_code: Error code
            message: Error message
            location: Error location

        Returns:
            OperationOutcome FHIR resource
        """
        issue: dict[str, Any] = {
            "severity": "error",
            "code": error_code,
            "diagnostics": message or "An error occurred during processing",
        }

        if location:
            issue["location"] = location

        return self.generate(issues=[issue], **kwargs)

    def generate_validation_error(
        self,
        field: str,
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a validation error OperationOutcome.

        Args:
            field: Field with validation error
            message: Validation message

        Returns:
            OperationOutcome FHIR resource
        """
        issues = [
            {
                "severity": "error",
                "code": "value",
                "diagnostics": message,
                "location": [field],
                "expression": [field],
            }
        ]

        return self.generate(issues=issues, **kwargs)

    def generate_not_found(
        self,
        resource_type: str,
        resource_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a not found OperationOutcome.

        Args:
            resource_type: Resource type
            resource_id: Resource ID

        Returns:
            OperationOutcome FHIR resource
        """
        issues = [
            {
                "severity": "error",
                "code": "not-found",
                "diagnostics": f"{resource_type}/{resource_id} not found",
            }
        ]

        return self.generate(issues=issues, **kwargs)
