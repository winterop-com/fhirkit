"""Validation rules for FHIR R4 resources.

This module defines the validation rules for each supported FHIR resource type,
including required fields and code bindings to ValueSets.
"""

from typing import Any

# Valid resource types
VALID_RESOURCE_TYPES = {
    "Patient",
    "Practitioner",
    "Organization",
    "Encounter",
    "Condition",
    "Observation",
    "MedicationRequest",
    "Procedure",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Immunization",
    "CarePlan",
    "Goal",
    "ServiceRequest",
    "DocumentReference",
    "Medication",
    "Measure",
    "MeasureReport",
    "ValueSet",
    "CodeSystem",
    "Library",
    "Bundle",
    "OperationOutcome",
    "Parameters",
    "CapabilityStatement",
}

# Validation rules per resource type
# Each rule defines:
#   - required: list of required field paths (using dot notation for nested)
#   - code_bindings: dict mapping field paths to ValueSet URLs
#   - cardinality: dict mapping field paths to (min, max) where max can be "*"
RESOURCE_RULES: dict[str, dict[str, Any]] = {
    "Patient": {
        "required": [],
        "code_bindings": {
            "gender": {
                "valueset": "http://hl7.org/fhir/ValueSet/administrative-gender",
                "strength": "required",
                "allowed_values": ["male", "female", "other", "unknown"],
            },
            "maritalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/marital-status",
                "strength": "extensible",
            },
        },
    },
    "Observation": {
        "required": ["status", "code"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/observation-status",
                "strength": "required",
                "allowed_values": [
                    "registered",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "Condition": {
        "required": ["subject"],
        "code_bindings": {
            "clinicalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/condition-clinical",
                "strength": "required",
                "allowed_values": ["active", "recurrence", "relapse", "inactive", "remission", "resolved"],
            },
            "verificationStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/condition-ver-status",
                "strength": "required",
                "allowed_values": [
                    "unconfirmed",
                    "provisional",
                    "differential",
                    "confirmed",
                    "refuted",
                    "entered-in-error",
                ],
            },
        },
    },
    "Encounter": {
        "required": ["status", "class"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/encounter-status",
                "strength": "required",
                "allowed_values": [
                    "planned",
                    "arrived",
                    "triaged",
                    "in-progress",
                    "onleave",
                    "finished",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "MedicationRequest": {
        "required": ["status", "intent", "medication[x]", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
                "strength": "required",
                "allowed_values": [
                    "active",
                    "on-hold",
                    "cancelled",
                    "completed",
                    "entered-in-error",
                    "stopped",
                    "draft",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/medicationrequest-intent",
                "strength": "required",
                "allowed_values": [
                    "proposal",
                    "plan",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ],
            },
        },
    },
    "Procedure": {
        "required": ["status", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/event-status",
                "strength": "required",
                "allowed_values": [
                    "preparation",
                    "in-progress",
                    "not-done",
                    "on-hold",
                    "stopped",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "DiagnosticReport": {
        "required": ["status", "code"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/diagnostic-report-status",
                "strength": "required",
                "allowed_values": [
                    "registered",
                    "partial",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "appended",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "AllergyIntolerance": {
        "required": ["patient"],
        "code_bindings": {
            "clinicalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/allergyintolerance-clinical",
                "strength": "required",
                "allowed_values": ["active", "inactive", "resolved"],
            },
            "verificationStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/allergyintolerance-verification",
                "strength": "required",
                "allowed_values": ["unconfirmed", "confirmed", "refuted", "entered-in-error"],
            },
        },
    },
    "Immunization": {
        "required": ["status", "vaccineCode", "patient", "occurrence[x]"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/immunization-status",
                "strength": "required",
                "allowed_values": ["completed", "entered-in-error", "not-done"],
            },
        },
    },
    "CarePlan": {
        "required": ["status", "intent", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-status",
                "strength": "required",
                "allowed_values": [
                    "draft",
                    "active",
                    "on-hold",
                    "revoked",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/care-plan-intent",
                "strength": "required",
                "allowed_values": ["proposal", "plan", "order", "option"],
            },
        },
    },
    "Goal": {
        "required": ["lifecycleStatus", "description", "subject"],
        "code_bindings": {
            "lifecycleStatus": {
                "valueset": "http://hl7.org/fhir/ValueSet/goal-status",
                "strength": "required",
                "allowed_values": [
                    "proposed",
                    "planned",
                    "accepted",
                    "active",
                    "on-hold",
                    "completed",
                    "cancelled",
                    "entered-in-error",
                    "rejected",
                ],
            },
        },
    },
    "ServiceRequest": {
        "required": ["status", "intent", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-status",
                "strength": "required",
                "allowed_values": [
                    "draft",
                    "active",
                    "on-hold",
                    "revoked",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-intent",
                "strength": "required",
                "allowed_values": [
                    "proposal",
                    "plan",
                    "directive",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ],
            },
        },
    },
    "DocumentReference": {
        "required": ["status", "content"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/document-reference-status",
                "strength": "required",
                "allowed_values": ["current", "superseded", "entered-in-error"],
            },
        },
    },
    "Medication": {
        "required": [],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/medication-status",
                "strength": "required",
                "allowed_values": ["active", "inactive", "entered-in-error"],
            },
        },
    },
    "Practitioner": {
        "required": [],
        "code_bindings": {
            "gender": {
                "valueset": "http://hl7.org/fhir/ValueSet/administrative-gender",
                "strength": "required",
                "allowed_values": ["male", "female", "other", "unknown"],
            },
        },
    },
    "Organization": {
        "required": [],
        "code_bindings": {},
    },
    "Measure": {
        "required": ["status"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "MeasureReport": {
        "required": ["status", "type", "measure"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/measure-report-status",
                "strength": "required",
                "allowed_values": ["complete", "pending", "error"],
            },
            "type": {
                "valueset": "http://hl7.org/fhir/ValueSet/measure-report-type",
                "strength": "required",
                "allowed_values": [
                    "individual",
                    "subject-list",
                    "summary",
                    "data-collection",
                ],
            },
        },
    },
    "ValueSet": {
        "required": ["status"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "CodeSystem": {
        "required": ["status", "content"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
            "content": {
                "valueset": "http://hl7.org/fhir/ValueSet/codesystem-content-mode",
                "strength": "required",
                "allowed_values": ["not-present", "example", "fragment", "complete", "supplement"],
            },
        },
    },
    "Library": {
        "required": ["status", "type"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "Bundle": {
        "required": ["type"],
        "code_bindings": {
            "type": {
                "valueset": "http://hl7.org/fhir/ValueSet/bundle-type",
                "strength": "required",
                "allowed_values": [
                    "document",
                    "message",
                    "transaction",
                    "transaction-response",
                    "batch",
                    "batch-response",
                    "history",
                    "searchset",
                    "collection",
                ],
            },
        },
    },
}


def get_rules(resource_type: str) -> dict[str, Any]:
    """Get validation rules for a resource type.

    Args:
        resource_type: The FHIR resource type

    Returns:
        Validation rules dict, or empty rules if not defined
    """
    return RESOURCE_RULES.get(
        resource_type,
        {
            "required": [],
            "code_bindings": {},
        },
    )
