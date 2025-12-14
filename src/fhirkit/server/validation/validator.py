"""FHIR Resource Validator.

This module provides validation of FHIR R4 resources against structure rules,
required fields, code bindings, and reference validity.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .rules import RESOURCE_RULES, VALID_RESOURCE_TYPES

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore


@dataclass
class ValidationIssue:
    """A single validation issue."""

    severity: str  # fatal | error | warning | information
    code: str  # FHIR issue-type code
    location: str  # FHIRPath to element
    message: str


@dataclass
class ValidationResult:
    """Result of resource validation."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_operation_outcome(self) -> dict[str, Any]:
        """Convert to FHIR OperationOutcome resource."""
        return {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": issue.severity,
                    "code": issue.code,
                    "location": [issue.location],
                    "diagnostics": issue.message,
                }
                for issue in self.issues
            ],
        }


class FHIRValidator:
    """Validator for FHIR R4 resources.

    Performs validation checks including:
    - Resource type validation
    - Required field validation
    - Code binding validation
    - Reference validation (if store provided)

    Args:
        store: Optional FHIRStore for reference validation
    """

    def __init__(self, store: "FHIRStore | None" = None):
        self._store = store

    def validate(self, resource: dict[str, Any], mode: str = "validation") -> ValidationResult:
        """Validate a FHIR resource.

        Args:
            resource: The FHIR resource to validate
            mode: Validation mode (validation, create, update, delete)

        Returns:
            ValidationResult with issues found
        """
        issues: list[ValidationIssue] = []

        # 1. Check resourceType exists and is valid
        issues.extend(self._validate_resource_type(resource))

        # If resourceType is invalid, skip further validation
        resource_type = resource.get("resourceType")
        if not resource_type or resource_type not in VALID_RESOURCE_TYPES:
            return ValidationResult(
                valid=not any(i.severity in ("fatal", "error") for i in issues),
                issues=issues,
            )

        # 2. Check required fields
        issues.extend(self._validate_required_fields(resource))

        # 3. Check code bindings against ValueSets
        issues.extend(self._validate_code_bindings(resource))

        # 4. Check reference targets exist (if store provided)
        if self._store:
            issues.extend(self._validate_references(resource))

        return ValidationResult(
            valid=not any(i.severity in ("fatal", "error") for i in issues),
            issues=issues,
        )

    def _validate_resource_type(self, resource: dict[str, Any]) -> list[ValidationIssue]:
        """Validate that resourceType is present and valid."""
        issues = []

        resource_type = resource.get("resourceType")

        if not resource_type:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="required",
                    location="Resource",
                    message="Missing required field: resourceType",
                )
            )
        elif resource_type not in VALID_RESOURCE_TYPES:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="invalid",
                    location="Resource.resourceType",
                    message=f"Invalid resourceType: {resource_type}",
                )
            )

        return issues

    def _validate_required_fields(self, resource: dict[str, Any]) -> list[ValidationIssue]:
        """Validate that all required fields are present."""
        issues: list[ValidationIssue] = []

        resource_type = resource.get("resourceType")
        if not resource_type:
            return issues

        rules = RESOURCE_RULES.get(resource_type, {})
        required_fields = rules.get("required", [])

        for field_path in required_fields:
            if not self._field_exists(resource, field_path):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="required",
                        location=f"{resource_type}.{field_path}",
                        message=f"Missing required field: {field_path}",
                    )
                )

        return issues

    def _field_exists(self, resource: dict[str, Any], field_path: str) -> bool:
        """Check if a field exists in the resource.

        Handles choice types like medication[x] by checking for any variant.
        """
        # Handle choice types (e.g., medication[x])
        if "[x]" in field_path:
            base_name = field_path.replace("[x]", "")
            # Check for common choice type suffixes
            suffixes = [
                "CodeableConcept",
                "Reference",
                "DateTime",
                "Period",
                "Timing",
                "String",
                "Boolean",
                "Integer",
                "Quantity",
                "Range",
                "Ratio",
                "Age",
                "Duration",
            ]
            for suffix in suffixes:
                if base_name + suffix in resource:
                    return True
            return False

        # Handle simple field paths
        parts = field_path.split(".")
        current = resource

        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list):
                # For arrays, check if at least one element has the field
                if not current:
                    return False
                # Continue with first element for nested checks
                if isinstance(current[0], dict) and part in current[0]:
                    current = current[0][part]
                else:
                    return False
            else:
                return False

        return current is not None

    def _validate_code_bindings(self, resource: dict[str, Any]) -> list[ValidationIssue]:
        """Validate code fields against their ValueSet bindings."""
        issues: list[ValidationIssue] = []

        resource_type = resource.get("resourceType")
        if not resource_type:
            return issues

        rules = RESOURCE_RULES.get(resource_type, {})
        code_bindings = rules.get("code_bindings", {})

        for field_path, binding in code_bindings.items():
            value = self._get_field_value(resource, field_path)

            if value is None:
                continue  # Field not present, skip

            strength = binding.get("strength", "required")
            allowed_values = binding.get("allowed_values", [])

            if allowed_values and value not in allowed_values:
                severity = "error" if strength == "required" else "warning"
                issues.append(
                    ValidationIssue(
                        severity=severity,
                        code="code-invalid",
                        location=f"{resource_type}.{field_path}",
                        message=f"Invalid code value '{value}' for {field_path}. "
                        f"Allowed values: {', '.join(allowed_values)}",
                    )
                )

        return issues

    def _get_field_value(self, resource: dict[str, Any], field_path: str) -> Any:
        """Get the value of a field at the given path.

        Handles nested paths like 'clinicalStatus.coding.code'.
        """
        parts = field_path.split(".")
        current: Any = resource

        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    return None
                current = current[part]
            elif isinstance(current, list):
                # For arrays, get the first element's value
                if not current:
                    return None
                if isinstance(current[0], dict) and part in current[0]:
                    current = current[0][part]
                else:
                    return None
            else:
                return None

        return current

    def _validate_references(self, resource: dict[str, Any]) -> list[ValidationIssue]:
        """Validate that reference targets exist."""
        issues: list[ValidationIssue] = []

        if not self._store:
            return issues

        references = self._find_references(resource)

        for ref_path, ref_value in references:
            if not self._reference_exists(ref_value):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="not-found",
                        location=ref_path,
                        message=f"Reference target not found: {ref_value}",
                    )
                )

        return issues

    def _find_references(self, obj: Any, path: str = "") -> list[tuple[str, str]]:
        """Find all Reference fields in a resource."""
        references = []

        if isinstance(obj, dict):
            # Check if this is a Reference
            if "reference" in obj and isinstance(obj["reference"], str):
                ref_value = obj["reference"]
                # Only validate internal references (not absolute URLs)
                if not ref_value.startswith("http://") and not ref_value.startswith("https://"):
                    references.append((path or "reference", ref_value))

            # Recurse into child fields
            for key, value in obj.items():
                child_path = f"{path}.{key}" if path else key
                references.extend(self._find_references(value, child_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                child_path = f"{path}[{i}]"
                references.extend(self._find_references(item, child_path))

        return references

    def _reference_exists(self, reference: str) -> bool:
        """Check if a reference target exists in the store."""
        if not self._store:
            return True

        # Parse reference format: "ResourceType/id"
        parts = reference.split("/")
        if len(parts) != 2:
            return True  # Can't validate malformed references

        resource_type, resource_id = parts

        # Check if resource exists
        return self._store.read(resource_type, resource_id) is not None
