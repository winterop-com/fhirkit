"""FHIR compartment and reference definitions.

This module defines the Patient compartment and reference paths used for:
- Patient $everything operation
- Compartment search (e.g., GET /Patient/{id}/Condition)
- _include/_revinclude search parameters

Based on FHIR R4 compartment definitions:
https://hl7.org/fhir/R4/compartmentdefinition-patient.html
"""

from typing import Any

# Patient compartment: maps resource types to search parameters that link to Patient
# These are the search parameters that can be used to find resources belonging to a patient
PATIENT_COMPARTMENT: dict[str, list[str]] = {
    "Condition": ["patient", "subject"],
    "Observation": ["patient", "subject"],
    "MedicationRequest": ["patient", "subject"],
    "Encounter": ["patient", "subject"],
    "Procedure": ["patient", "subject"],
    "DiagnosticReport": ["patient", "subject"],
    "CarePlan": ["patient", "subject"],
    "AllergyIntolerance": ["patient"],
    "Immunization": ["patient"],
    "ServiceRequest": ["patient", "subject"],
    "Goal": ["patient", "subject"],
    "ClinicalImpression": ["patient", "subject"],
    "RiskAssessment": ["patient", "subject"],
    "FamilyMemberHistory": ["patient"],
    "DocumentReference": ["patient", "subject"],
    "MeasureReport": ["patient", "subject"],
    "Consent": ["patient"],
}

# Reference paths: maps resource types and search parameters to the dotted path
# within the resource where the reference value can be found
# Format: {ResourceType: {searchParam: [dotted.path.to.reference]}}
REFERENCE_PATHS: dict[str, dict[str, list[str]]] = {
    "Condition": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "asserter": ["asserter.reference"],
    },
    "Observation": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "performer": ["performer.reference"],
        "device": ["device.reference"],
    },
    "MedicationRequest": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "requester": ["requester.reference"],
        "performer": ["performer.reference"],
    },
    "Encounter": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "participant": ["participant.individual.reference"],
        "service-provider": ["serviceProvider.reference"],
        "practitioner": ["participant.individual.reference"],
    },
    "Procedure": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "performer": ["performer.actor.reference"],
    },
    "DiagnosticReport": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "performer": ["performer.reference"],
    },
    "CarePlan": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
    },
    "AllergyIntolerance": {
        "patient": ["patient.reference"],
        "recorder": ["recorder.reference"],
        "asserter": ["asserter.reference"],
    },
    "Immunization": {
        "patient": ["patient.reference"],
        "performer": ["performer.actor.reference"],
    },
    "ServiceRequest": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "encounter": ["encounter.reference"],
        "requester": ["requester.reference"],
        "performer": ["performer.reference"],
    },
    "Goal": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
    },
    "DocumentReference": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "author": ["author.reference"],
        "encounter": ["context.encounter.reference"],
        "custodian": ["custodian.reference"],
    },
    "Patient": {
        "general-practitioner": ["generalPractitioner.reference"],
        "organization": ["managingOrganization.reference"],
        "link": ["link.other.reference"],
    },
    "Practitioner": {
        # Practitioner doesn't have references to other resources typically
    },
    "Organization": {
        "partof": ["partOf.reference"],
    },
    "MeasureReport": {
        "patient": ["subject.reference"],
        "subject": ["subject.reference"],
        "reporter": ["reporter.reference"],
        "evaluated-resource": ["evaluatedResource.reference"],
    },
    "Measure": {
        # Measure is a definitional resource, no patient references
    },
}


def get_patient_reference_paths(resource_type: str) -> list[str]:
    """Get all paths that could contain a patient reference for a resource type.

    Args:
        resource_type: The FHIR resource type (e.g., "Condition", "Observation")

    Returns:
        List of dotted paths to patient reference fields (e.g., ["subject.reference"])
    """
    paths: list[str] = []
    compartment_params = PATIENT_COMPARTMENT.get(resource_type, [])

    for param in compartment_params:
        ref_paths = REFERENCE_PATHS.get(resource_type, {}).get(param, [])
        for path in ref_paths:
            if path not in paths:
                paths.append(path)

    return paths


def get_reference_path(resource_type: str, search_param: str) -> list[str]:
    """Get the reference paths for a specific search parameter.

    Args:
        resource_type: The FHIR resource type
        search_param: The search parameter name (e.g., "patient", "subject", "encounter")

    Returns:
        List of dotted paths to the reference field
    """
    return REFERENCE_PATHS.get(resource_type, {}).get(search_param, [])


def get_reference_from_path(resource: dict[str, Any], path: str) -> str | None:
    """Extract a reference value from a resource using a dotted path.

    Handles nested paths like "subject.reference" or "performer.actor.reference".
    For array fields, returns the first matching reference found.

    Args:
        resource: The FHIR resource dictionary
        path: Dotted path to the reference field

    Returns:
        The reference string (e.g., "Patient/123") or None if not found
    """
    parts = path.split(".")
    current: Any = resource

    for part in parts:
        if current is None:
            return None

        if isinstance(current, list):
            # For arrays, search through items for the first match
            for item in current:
                if isinstance(item, dict) and part in item:
                    val = item[part]
                    if isinstance(val, str):
                        return val
                    elif isinstance(val, dict):
                        # Continue traversing
                        current = val
                        break
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current if isinstance(current, str) else None


def get_all_references_from_path(resource: dict[str, Any], path: str) -> list[str]:
    """Extract all reference values from a resource using a dotted path.

    Similar to get_reference_from_path but returns all matching references
    when the path traverses array fields.

    Args:
        resource: The FHIR resource dictionary
        path: Dotted path to the reference field

    Returns:
        List of reference strings found
    """
    parts = path.split(".")
    current_values: list[Any] = [resource]

    for part in parts:
        next_values: list[Any] = []

        for current in current_values:
            if current is None:
                continue

            if isinstance(current, list):
                for item in current:
                    if isinstance(item, dict) and part in item:
                        val = item[part]
                        if isinstance(val, list):
                            next_values.extend(val)
                        else:
                            next_values.append(val)
            elif isinstance(current, dict):
                val = current.get(part)
                if val is not None:
                    if isinstance(val, list):
                        next_values.extend(val)
                    else:
                        next_values.append(val)

        current_values = next_values

    # Filter to only string values (actual references)
    return [v for v in current_values if isinstance(v, str)]


def is_in_patient_compartment(resource_type: str) -> bool:
    """Check if a resource type is part of the Patient compartment.

    Args:
        resource_type: The FHIR resource type

    Returns:
        True if the resource type belongs to the Patient compartment
    """
    return resource_type in PATIENT_COMPARTMENT


def get_compartment_resource_types() -> list[str]:
    """Get all resource types that are part of the Patient compartment.

    Returns:
        List of resource type names
    """
    return list(PATIENT_COMPARTMENT.keys())
