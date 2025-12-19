"""Profile Validator for FHIR StructureDefinition profiles.

This module provides validation of FHIR resources against StructureDefinition
profiles, checking cardinality, fixed values, patterns, and constraints.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from .validator import ValidationIssue, ValidationResult

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore

logger = logging.getLogger(__name__)


class ProfileValidator:
    """Validator for FHIR resources against StructureDefinition profiles.

    Validates resources against profile constraints including:
    - Cardinality (min/max occurrence)
    - Required elements
    - Fixed values (fixed[x])
    - Pattern values (pattern[x])
    - Code bindings
    - FHIRPath constraints

    Args:
        store: FHIRStore for loading StructureDefinition resources
    """

    def __init__(self, store: FHIRStore):
        self._store = store
        self._profile_cache: dict[str, dict[str, Any] | None] = {}

    def validate_against_profile(
        self,
        resource: dict[str, Any],
        profile_url: str,
    ) -> ValidationResult:
        """Validate a resource against a StructureDefinition profile.

        Args:
            resource: The FHIR resource to validate
            profile_url: Canonical URL of the StructureDefinition profile

        Returns:
            ValidationResult with issues found
        """
        issues: list[ValidationIssue] = []

        # Load the profile
        profile = self._load_profile(profile_url)
        if profile is None:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="not-found",
                    location="meta.profile",
                    message=f"Profile not found: {profile_url}",
                )
            )
            return ValidationResult(valid=False, issues=issues)

        # Check resource type matches profile type
        profile_type = profile.get("type")
        resource_type = resource.get("resourceType")
        if profile_type and resource_type != profile_type:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="invalid",
                    location="resourceType",
                    message=f"Resource type '{resource_type}' does not match profile type '{profile_type}'",
                )
            )
            return ValidationResult(valid=False, issues=issues)

        # Get element definitions from snapshot or differential
        elements = self._get_element_definitions(profile)

        # Validate each element definition
        for element in elements:
            element_issues = self._validate_element(resource, element)
            issues.extend(element_issues)

        # Validate FHIRPath constraints
        constraint_issues = self._validate_constraints(resource, profile)
        issues.extend(constraint_issues)

        return ValidationResult(
            valid=not any(i.severity in ("fatal", "error") for i in issues),
            issues=issues,
        )

    def _load_profile(self, url: str) -> dict[str, Any] | None:
        """Load a StructureDefinition by canonical URL.

        Uses caching to avoid repeated lookups.

        Args:
            url: Canonical URL of the profile (may include version: url|version)

        Returns:
            StructureDefinition resource or None if not found
        """
        # Check cache first
        if url in self._profile_cache:
            return self._profile_cache[url]

        # Parse URL and version
        base_url = url
        version = None
        if "|" in url:
            base_url, version = url.split("|", 1)

        # Search for the profile
        search_params: dict[str, Any] = {"url": base_url}
        if version:
            search_params["version"] = version

        results, total = self._store.search("StructureDefinition", search_params, _count=1, _offset=0)

        profile = results[0] if results else None
        self._profile_cache[url] = profile
        return profile

    def _get_element_definitions(self, profile: dict[str, Any]) -> list[dict[str, Any]]:
        """Get element definitions from profile.

        Prefers snapshot over differential for complete element definitions.

        Args:
            profile: StructureDefinition resource

        Returns:
            List of ElementDefinition dictionaries
        """
        # Try snapshot first (more complete)
        snapshot = profile.get("snapshot", {})
        if snapshot.get("element"):
            return snapshot["element"]

        # Fall back to differential
        differential = profile.get("differential", {})
        return differential.get("element", [])

    def _validate_element(
        self,
        resource: dict[str, Any],
        element_def: dict[str, Any],
    ) -> list[ValidationIssue]:
        """Validate a resource against an element definition.

        Args:
            resource: The FHIR resource
            element_def: ElementDefinition from the profile

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        path = element_def.get("id", element_def.get("path", ""))
        if not path:
            return issues

        # Skip the root element (e.g., "Patient")
        if "." not in path:
            return issues

        # Get the field path relative to the resource
        field_path = self._element_path_to_field_path(path)
        if not field_path:
            return issues

        # Get the actual value from the resource
        value = self._get_value_at_path(resource, field_path)

        # Validate cardinality
        cardinality_issues = self._validate_cardinality(value, element_def, field_path)
        issues.extend(cardinality_issues)

        # Validate fixed value
        fixed_issues = self._validate_fixed_value(value, element_def, field_path)
        issues.extend(fixed_issues)

        # Validate pattern
        pattern_issues = self._validate_pattern(value, element_def, field_path)
        issues.extend(pattern_issues)

        # Validate binding
        binding_issues = self._validate_binding(value, element_def, field_path)
        issues.extend(binding_issues)

        return issues

    def _element_path_to_field_path(self, element_path: str) -> str:
        """Convert an ElementDefinition path to a resource field path.

        Examples:
            "Patient.name" -> "name"
            "Patient.name.given" -> "name.given"
            "Patient.deceased[x]" -> "deceased"

        Args:
            element_path: Path from ElementDefinition

        Returns:
            Field path relative to resource root
        """
        # Remove the resource type prefix
        parts = element_path.split(".", 1)
        if len(parts) < 2:
            return ""

        field_path = parts[1]

        # Handle choice types - remove [x] suffix for checking
        field_path = re.sub(r"\[x\]$", "", field_path)

        return field_path

    def _get_value_at_path(self, resource: dict[str, Any], path: str) -> Any:
        """Get value from resource at the given path.

        Handles array notation and choice types.

        Args:
            resource: FHIR resource
            path: Dot-separated path

        Returns:
            Value at path or None if not found
        """
        if not path:
            return resource

        parts = path.split(".")
        current: Any = resource

        for part in parts:
            if current is None:
                return None

            # Handle choice types (e.g., deceased -> deceasedBoolean or deceasedDateTime)
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    # Try choice type variants
                    choice_value = self._get_choice_value(current, part)
                    if choice_value is not None:
                        current = choice_value
                    else:
                        return None
            elif isinstance(current, list):
                # Collect values from all items in the array
                values = []
                for item in current:
                    if isinstance(item, dict) and part in item:
                        values.append(item[part])
                current = values if values else None
            else:
                return None

        return current

    def _get_choice_value(self, obj: dict[str, Any], base_name: str) -> Any:
        """Get value for a choice type field.

        Args:
            obj: Dictionary to search
            base_name: Base name without type suffix (e.g., "deceased")

        Returns:
            Value if found, None otherwise
        """
        suffixes = [
            "Boolean",
            "Integer",
            "Decimal",
            "String",
            "Uri",
            "Date",
            "DateTime",
            "Time",
            "Instant",
            "CodeableConcept",
            "Coding",
            "Quantity",
            "Range",
            "Ratio",
            "Period",
            "Reference",
            "Attachment",
            "Identifier",
            "Address",
            "ContactPoint",
            "HumanName",
            "Age",
            "Duration",
            "Timing",
            "Annotation",
            "Signature",
        ]

        for suffix in suffixes:
            key = base_name + suffix
            if key in obj:
                return obj[key]

        return None

    def _validate_cardinality(
        self,
        value: Any,
        element_def: dict[str, Any],
        path: str,
    ) -> list[ValidationIssue]:
        """Validate element cardinality (min/max).

        Args:
            value: Current value from resource
            element_def: ElementDefinition
            path: Field path for error reporting

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        min_val = element_def.get("min", 0)
        max_val = element_def.get("max", "*")

        # Count occurrences
        if value is None:
            count = 0
        elif isinstance(value, list):
            count = len(value)
        else:
            count = 1

        # Check minimum
        if count < min_val:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="required" if min_val == 1 else "structure",
                    location=path,
                    message=f"Element '{path}' has {count} occurrences, minimum required is {min_val}",
                )
            )

        # Check maximum
        if max_val != "*":
            try:
                max_int = int(max_val)
                if count > max_int:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="structure",
                            location=path,
                            message=f"Element '{path}' has {count} occurrences, maximum allowed is {max_int}",
                        )
                    )
            except ValueError:
                pass  # Invalid max value, skip check

        return issues

    def _validate_fixed_value(
        self,
        value: Any,
        element_def: dict[str, Any],
        path: str,
    ) -> list[ValidationIssue]:
        """Validate fixed[x] values.

        Args:
            value: Current value from resource
            element_def: ElementDefinition
            path: Field path for error reporting

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        # Find fixed[x] property
        fixed_value = None
        fixed_key = None
        for key in element_def:
            if key.startswith("fixed"):
                fixed_value = element_def[key]
                fixed_key = key
                break

        if fixed_value is None:
            return issues

        if value is None:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="value",
                    location=path,
                    message=f"Element '{path}' must have fixed value specified by {fixed_key}",
                )
            )
        elif not self._values_equal(value, fixed_value):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="value",
                    location=path,
                    message=f"Element '{path}' value does not match fixed value. Expected: {fixed_value}, Got: {value}",
                )
            )

        return issues

    def _validate_pattern(
        self,
        value: Any,
        element_def: dict[str, Any],
        path: str,
    ) -> list[ValidationIssue]:
        """Validate pattern[x] values.

        Pattern validation is less strict than fixed - the value must
        contain at least what's in the pattern.

        Args:
            value: Current value from resource
            element_def: ElementDefinition
            path: Field path for error reporting

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        # Find pattern[x] property
        pattern_value = None
        pattern_key = None
        for key in element_def:
            if key.startswith("pattern"):
                pattern_value = element_def[key]
                pattern_key = key
                break

        if pattern_value is None:
            return issues

        if value is None:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="value",
                    location=path,
                    message=f"Element '{path}' must match pattern specified by {pattern_key}",
                )
            )
        elif not self._matches_pattern(value, pattern_value):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="value",
                    location=path,
                    message=f"Element '{path}' value does not match pattern. Pattern: {pattern_value}",
                )
            )

        return issues

    def _validate_binding(
        self,
        value: Any,
        element_def: dict[str, Any],
        path: str,
    ) -> list[ValidationIssue]:
        """Validate code bindings.

        Args:
            value: Current value from resource
            element_def: ElementDefinition
            path: Field path for error reporting

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        binding = element_def.get("binding")
        if not binding:
            return issues

        strength = binding.get("strength", "example")
        value_set = binding.get("valueSet", "")

        # Skip example and preferred bindings
        if strength in ("example", "preferred"):
            return issues

        if value is None:
            return issues

        # For extensible/required bindings, we note that full validation
        # would require ValueSet expansion. For now, log info only.
        if strength == "required":
            # Would need to validate against ValueSet
            # This is a placeholder for future terminology service integration
            logger.debug(f"Binding validation skipped for {path}: ValueSet {value_set} (strength: {strength})")

        return issues

    def _validate_constraints(
        self,
        resource: dict[str, Any],
        profile: dict[str, Any],
    ) -> list[ValidationIssue]:
        """Validate FHIRPath constraints defined in the profile.

        Args:
            resource: FHIR resource
            profile: StructureDefinition

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        elements = self._get_element_definitions(profile)

        for element in elements:
            constraints = element.get("constraint", [])
            for constraint in constraints:
                key = constraint.get("key", "")
                expression = constraint.get("expression", "")
                human = constraint.get("human", "")
                severity = constraint.get("severity", "error")

                if not expression:
                    continue

                # Evaluate FHIRPath expression
                try:
                    from fhirkit.engine.fhirpath import FHIRPathEvaluator

                    evaluator = FHIRPathEvaluator()
                    result = evaluator.evaluate(expression, resource)

                    # Constraint should evaluate to true
                    if not self._is_truthy(result):
                        issues.append(
                            ValidationIssue(
                                severity=severity,
                                code="invariant",
                                location=element.get("path", ""),
                                message=f"Constraint {key} failed: {human}",
                            )
                        )
                except Exception as e:
                    logger.warning(f"Could not evaluate constraint {key}: {e}")

        return issues

    def _values_equal(self, value1: Any, value2: Any) -> bool:
        """Check if two values are equal.

        Handles complex types like CodeableConcept.
        """
        if type(value1) is not type(value2):
            return False

        if isinstance(value1, dict):
            return all(k in value1 and self._values_equal(value1[k], v) for k, v in value2.items())

        if isinstance(value1, list):
            if len(value1) != len(value2):
                return False
            return all(self._values_equal(v1, v2) for v1, v2 in zip(value1, value2))

        return value1 == value2

    def _matches_pattern(self, value: Any, pattern: Any) -> bool:
        """Check if value matches pattern.

        Pattern matching is inclusive - value must contain at least
        what's specified in the pattern.
        """
        if pattern is None:
            return True

        if value is None:
            return False

        if isinstance(pattern, dict):
            if isinstance(value, list):
                # If value is a list and pattern is a single object,
                # pattern matches if ANY element in the list matches
                return any(self._matches_pattern(v, pattern) for v in value)
            if not isinstance(value, dict):
                return False
            # All pattern keys must be present in value
            return all(k in value and self._matches_pattern(value[k], v) for k, v in pattern.items())

        if isinstance(pattern, list):
            if not isinstance(value, list):
                return False
            # Each pattern item must match at least one value item
            return all(any(self._matches_pattern(v, p) for v in value) for p in pattern)

        return value == pattern

    def _is_truthy(self, result: Any) -> bool:
        """Check if a FHIRPath result is truthy.

        Per FHIRPath spec:
        - Empty collection is false
        - Single true boolean is true
        - Single false boolean is false
        - Non-empty, non-boolean collection is true
        """
        if result is None:
            return False
        if isinstance(result, list):
            if len(result) == 0:
                return False
            if len(result) == 1 and isinstance(result[0], bool):
                return result[0]
            return True
        if isinstance(result, bool):
            return result
        return True

    def clear_cache(self) -> None:
        """Clear the profile cache."""
        self._profile_cache.clear()
