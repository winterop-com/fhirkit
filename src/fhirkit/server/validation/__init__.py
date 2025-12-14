"""FHIR Resource Validation.

This module provides validation of FHIR R4 resources against structure rules,
required fields, code bindings, and reference validity.

Example:
    from fhirkit.server.validation import FHIRValidator

    validator = FHIRValidator()
    result = validator.validate({
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]}
    })

    if result.valid:
        print("Resource is valid")
    else:
        for issue in result.issues:
            print(f"{issue.severity}: {issue.message} at {issue.location}")
"""

from .rules import RESOURCE_RULES
from .validator import FHIRValidator, ValidationIssue, ValidationResult

__all__ = [
    "FHIRValidator",
    "ValidationResult",
    "ValidationIssue",
    "RESOURCE_RULES",
]
