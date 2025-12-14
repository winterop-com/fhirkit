"""Template helper functions for FHIR UI."""

from datetime import datetime
from typing import Any


def format_date(date_str: str | None) -> str:
    """Format a FHIR date/datetime for display.

    Args:
        date_str: FHIR date or datetime string

    Returns:
        Formatted date string
    """
    if not date_str:
        return ""

    try:
        # Handle various FHIR date formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m",
            "%Y",
        ]:
            try:
                dt = datetime.strptime(date_str[:26].replace("Z", "+00:00"), fmt.replace("%z", ""))
                return dt.strftime("%Y-%m-%d %H:%M") if "T" in date_str else dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def format_reference(ref: str | dict[str, Any] | None) -> tuple[str, str]:
    """Parse a FHIR reference into type and ID.

    Args:
        ref: FHIR reference string or Reference object

    Returns:
        Tuple of (resource_type, resource_id)
    """
    if not ref:
        return "", ""

    if isinstance(ref, dict):
        ref = ref.get("reference", "")

    if not isinstance(ref, str) or "/" not in ref:
        return "", ""

    parts = ref.split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return "", ""


def get_resource_display(resource: dict[str, Any]) -> str:
    """Get a human-readable display for a resource.

    Args:
        resource: FHIR resource

    Returns:
        Display string
    """
    resource_type = resource.get("resourceType", "Unknown")
    resource_id = resource.get("id", "")

    # Type-specific display logic
    if resource_type == "Patient":
        names = resource.get("name", [])
        if names:
            name = names[0]
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            if given or family:
                return f"{given} {family}".strip()
        return f"Patient/{resource_id}"

    elif resource_type == "Practitioner":
        names = resource.get("name", [])
        if names:
            name = names[0]
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            if given or family:
                return f"{given} {family}".strip()
        return f"Practitioner/{resource_id}"

    elif resource_type == "Organization":
        return resource.get("name", f"Organization/{resource_id}")

    elif resource_type == "Condition":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Condition/{resource_id}")
        return f"Condition/{resource_id}"

    elif resource_type == "Observation":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Observation/{resource_id}")
        return f"Observation/{resource_id}"

    elif resource_type == "Medication":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Medication/{resource_id}")
        return f"Medication/{resource_id}"

    elif resource_type == "MedicationRequest":
        med = resource.get("medicationCodeableConcept", {})
        if med.get("text"):
            return med["text"]
        codings = med.get("coding", [])
        if codings:
            return codings[0].get("display", f"MedicationRequest/{resource_id}")
        return f"MedicationRequest/{resource_id}"

    elif resource_type == "Encounter":
        enc_class = resource.get("class", {})
        display = enc_class.get("display", enc_class.get("code", ""))
        if display:
            return f"Encounter: {display}"
        return f"Encounter/{resource_id}"

    elif resource_type == "ValueSet":
        return resource.get("name", resource.get("title", f"ValueSet/{resource_id}"))

    elif resource_type == "CodeSystem":
        return resource.get("name", resource.get("title", f"CodeSystem/{resource_id}"))

    elif resource_type == "ConceptMap":
        return resource.get("name", resource.get("title", f"ConceptMap/{resource_id}"))

    elif resource_type == "Library":
        return resource.get("name", resource.get("title", f"Library/{resource_id}"))

    elif resource_type == "Measure":
        return resource.get("name", resource.get("title", f"Measure/{resource_id}"))

    elif resource_type == "Composition":
        return resource.get("title", f"Composition/{resource_id}")

    # Default: use resource type and ID
    return f"{resource_type}/{resource_id}"


# Resource type categories for UI organization
RESOURCE_CATEGORIES: dict[str, list[str]] = {
    "Administrative": [
        "Patient",
        "Practitioner",
        "PractitionerRole",
        "Organization",
        "Location",
        "RelatedPerson",
        "Group",
    ],
    "Clinical": [
        "Encounter",
        "Condition",
        "Observation",
        "Procedure",
        "DiagnosticReport",
        "AllergyIntolerance",
        "Immunization",
        "ClinicalImpression",
        "FamilyMemberHistory",
    ],
    "Medications": [
        "Medication",
        "MedicationRequest",
        "MedicationAdministration",
        "MedicationStatement",
        "MedicationDispense",
    ],
    "Care Management": [
        "CarePlan",
        "CareTeam",
        "Goal",
        "Task",
    ],
    "Scheduling": [
        "Appointment",
        "Schedule",
        "Slot",
        "HealthcareService",
    ],
    "Financial": [
        "Coverage",
        "Claim",
        "ExplanationOfBenefit",
    ],
    "Diagnostics": [
        "Specimen",
        "ServiceRequest",
        "DocumentReference",
        "Media",
    ],
    "Documents": [
        "Composition",
        "Questionnaire",
        "QuestionnaireResponse",
    ],
    "Terminology": [
        "ValueSet",
        "CodeSystem",
        "ConceptMap",
    ],
    "Quality & Measures": [
        "Measure",
        "MeasureReport",
        "Library",
    ],
    "Safety & Alerts": [
        "Flag",
        "DetectedIssue",
        "RiskAssessment",
        "AdverseEvent",
    ],
    "Other": [
        "Device",
        "Consent",
        "Communication",
        "NutritionOrder",
        "Bundle",
        "Provenance",
        "AuditEvent",
    ],
}


def get_resource_category(resource_type: str) -> str:
    """Get the category for a resource type.

    Args:
        resource_type: FHIR resource type

    Returns:
        Category name
    """
    for category, types in RESOURCE_CATEGORIES.items():
        if resource_type in types:
            return category
    return "Other"
