"""Template helper functions for FHIR UI."""

import re
from datetime import datetime
from pathlib import Path
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

    elif resource_type == "PractitionerRole":
        # Try to get role code and specialty
        parts = []
        codes = resource.get("code", [])
        if codes:
            code_display = codes[0].get("coding", [{}])[0].get("display", "")
            if code_display:
                parts.append(code_display)
        specialties = resource.get("specialty", [])
        if specialties:
            spec_display = specialties[0].get("coding", [{}])[0].get("display", "")
            if spec_display:
                parts.append(spec_display)
        if parts:
            return " - ".join(parts)
        return f"PractitionerRole/{resource_id}"

    elif resource_type == "Location":
        return resource.get("name", f"Location/{resource_id}")

    elif resource_type == "Procedure":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Procedure/{resource_id}")
        return f"Procedure/{resource_id}"

    elif resource_type == "DiagnosticReport":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"DiagnosticReport/{resource_id}")
        return f"DiagnosticReport/{resource_id}"

    elif resource_type == "AllergyIntolerance":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"AllergyIntolerance/{resource_id}")
        return f"AllergyIntolerance/{resource_id}"

    elif resource_type == "Immunization":
        code = resource.get("vaccineCode", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Immunization/{resource_id}")
        return f"Immunization/{resource_id}"

    elif resource_type == "CarePlan":
        title = resource.get("title")
        if title:
            return title
        categories = resource.get("category", [])
        if categories:
            cat_text = categories[0].get("text")
            if cat_text:
                return cat_text
            codings = categories[0].get("coding", [])
            if codings:
                return codings[0].get("display", f"CarePlan/{resource_id}")
        return f"CarePlan/{resource_id}"

    elif resource_type == "CareTeam":
        return resource.get("name", f"CareTeam/{resource_id}")

    elif resource_type == "Goal":
        desc = resource.get("description", {})
        if desc.get("text"):
            return desc["text"]
        return f"Goal/{resource_id}"

    elif resource_type == "ServiceRequest":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"ServiceRequest/{resource_id}")
        return f"ServiceRequest/{resource_id}"

    elif resource_type == "Coverage":
        type_info = resource.get("type", {})
        if type_info.get("text"):
            return type_info["text"]
        codings = type_info.get("coding", [])
        if codings:
            return codings[0].get("display", f"Coverage/{resource_id}")
        return f"Coverage/{resource_id}"

    elif resource_type == "DocumentReference":
        desc = resource.get("description")
        if desc:
            return desc
        type_info = resource.get("type", {})
        if type_info.get("text"):
            return type_info["text"]
        codings = type_info.get("coding", [])
        if codings:
            return codings[0].get("display", f"DocumentReference/{resource_id}")
        return f"DocumentReference/{resource_id}"

    elif resource_type == "Questionnaire":
        return resource.get("title", resource.get("name", f"Questionnaire/{resource_id}"))

    elif resource_type == "QuestionnaireResponse":
        questionnaire = resource.get("questionnaire", "")
        if questionnaire:
            # Extract just the name/id from the reference
            parts = questionnaire.split("/")
            return f"Response: {parts[-1][:30]}" if parts else f"QuestionnaireResponse/{resource_id}"
        return f"QuestionnaireResponse/{resource_id}"

    elif resource_type == "Flag":
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Flag/{resource_id}")
        return f"Flag/{resource_id}"

    elif resource_type == "Device":
        names = resource.get("deviceName", [])
        if names:
            return names[0].get("name", f"Device/{resource_id}")
        type_info = resource.get("type", {})
        if type_info.get("text"):
            return type_info["text"]
        codings = type_info.get("coding", [])
        if codings:
            return codings[0].get("display", f"Device/{resource_id}")
        return f"Device/{resource_id}"

    elif resource_type == "RelatedPerson":
        names = resource.get("name", [])
        if names:
            name = names[0]
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            if given or family:
                return f"{given} {family}".strip()
        relationships = resource.get("relationship", [])
        if relationships:
            rel = relationships[0]
            if rel.get("text"):
                return rel["text"]
            codings = rel.get("coding", [])
            if codings:
                return codings[0].get("display", f"RelatedPerson/{resource_id}")
        return f"RelatedPerson/{resource_id}"

    elif resource_type == "Schedule":
        # Use specialty + service type for display
        specialties = resource.get("specialty", [])
        service_types = resource.get("serviceType", [])
        parts = []
        if specialties:
            spec_text = specialties[0].get("text")
            if spec_text:
                parts.append(spec_text)
            else:
                codings = specialties[0].get("coding", [])
                if codings:
                    parts.append(codings[0].get("display", ""))
        if service_types:
            svc_text = service_types[0].get("text")
            if svc_text:
                parts.append(svc_text)
            else:
                codings = service_types[0].get("coding", [])
                if codings:
                    parts.append(codings[0].get("display", ""))
        if parts:
            return " - ".join(filter(None, parts))
        return f"Schedule/{resource_id}"

    elif resource_type == "MeasureReport":
        # Use type + measure name for display
        report_type = resource.get("type", "")
        measure = resource.get("measure", "")
        parts = []
        if report_type:
            parts.append(report_type.replace("-", " ").title())
        if measure:
            # Extract measure name from canonical URL
            measure_name = measure.split("/")[-1] if "/" in measure else measure
            parts.append(measure_name)
        if parts:
            return " - ".join(parts)
        return f"MeasureReport/{resource_id}"

    elif resource_type == "Group":
        return resource.get("name", f"Group/{resource_id}")

    elif resource_type == "Task":
        desc = resource.get("description")
        if desc:
            return desc[:50] + "..." if len(desc) > 50 else desc
        code = resource.get("code", {})
        if code.get("text"):
            return code["text"]
        codings = code.get("coding", [])
        if codings:
            return codings[0].get("display", f"Task/{resource_id}")
        return f"Task/{resource_id}"

    elif resource_type == "Appointment":
        desc = resource.get("description")
        if desc:
            return desc
        appt_type = resource.get("appointmentType", {})
        if appt_type.get("text"):
            return appt_type["text"]
        codings = appt_type.get("coding", [])
        if codings:
            return codings[0].get("display", f"Appointment/{resource_id}")
        return f"Appointment/{resource_id}"

    elif resource_type == "Slot":
        comment = resource.get("comment")
        if comment:
            return comment
        service_types = resource.get("serviceType", [])
        if service_types:
            svc_text = service_types[0].get("text")
            if svc_text:
                return svc_text
            codings = service_types[0].get("coding", [])
            if codings:
                return codings[0].get("display", f"Slot/{resource_id}")
        return f"Slot/{resource_id}"

    elif resource_type == "Claim":
        claim_type = resource.get("type", {})
        use = resource.get("use", "")
        parts = []
        if claim_type.get("text"):
            parts.append(claim_type["text"])
        elif claim_type.get("coding"):
            parts.append(claim_type["coding"][0].get("display", ""))
        if use:
            parts.append(use.title())
        if parts:
            return " - ".join(filter(None, parts))
        return f"Claim/{resource_id}"

    elif resource_type == "ExplanationOfBenefit":
        eob_type = resource.get("type", {})
        if eob_type.get("text"):
            return eob_type["text"]
        codings = eob_type.get("coding", [])
        if codings:
            return codings[0].get("display", f"ExplanationOfBenefit/{resource_id}")
        return f"ExplanationOfBenefit/{resource_id}"

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
        "Person",
    ],
    "Clinical": [
        "Encounter",
        "Condition",
        "Observation",
        "Procedure",
        "DiagnosticReport",
        "AllergyIntolerance",
        "Immunization",
        "ImmunizationRecommendation",
        "ClinicalImpression",
        "FamilyMemberHistory",
        "VisionPrescription",
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
    "Clinical Workflow": [
        "ActivityDefinition",
        "PlanDefinition",
        "GuidanceResponse",
        "DeviceRequest",
    ],
    "Scheduling": [
        "Appointment",
        "AppointmentResponse",
        "Schedule",
        "Slot",
        "HealthcareService",
    ],
    "Financial": [
        "Coverage",
        "Claim",
        "ClaimResponse",
        "ExplanationOfBenefit",
        "Account",
        "CoverageEligibilityRequest",
        "CoverageEligibilityResponse",
        "PaymentNotice",
        "PaymentReconciliation",
        "ChargeItem",
        "ChargeItemDefinition",
        "Contract",
        "Invoice",
    ],
    "Diagnostics": [
        "Specimen",
        "ServiceRequest",
        "DocumentReference",
        "DocumentManifest",
        "Media",
        "Substance",
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
    "Messaging": [
        "MessageHeader",
    ],
    "Conformance": [
        "SearchParameter",
        "StructureDefinition",
        "Subscription",
        "OperationDefinition",
        "ImplementationGuide",
        "CompartmentDefinition",
        "MessageDefinition",
        "StructureMap",
        "GraphDefinition",
        "NamingSystem",
    ],
    "Testing": [
        "TestScript",
        "TestReport",
    ],
    "Verification": [
        "VerificationResult",
    ],
    "Definitions": [
        "EventDefinition",
        "ObservationDefinition",
        "SpecimenDefinition",
    ],
    "Insurance": [
        "InsurancePlan",
        "EnrollmentRequest",
        "EnrollmentResponse",
    ],
    "Linkage": [
        "Linkage",
    ],
    "Device Usage": [
        "DeviceUseStatement",
    ],
    "Foundation": [
        "Bundle",
        "Parameters",
        "Basic",
        "CapabilityStatement",
        "OperationOutcome",
        "TerminologyCapabilities",
    ],
    "Evidence-Based Medicine": [
        "Evidence",
        "EvidenceVariable",
        "EffectEvidenceSynthesis",
        "RiskEvidenceSynthesis",
        "ResearchDefinition",
        "ResearchElementDefinition",
    ],
    "Laboratory & Genomics": [
        "MolecularSequence",
        "BiologicallyDerivedProduct",
    ],
    "Catalog": [
        "CatalogEntry",
    ],
    "Immunization Assessment": [
        "ImmunizationEvaluation",
    ],
    "Substance Specialized": [
        "SubstanceNucleicAcid",
        "SubstancePolymer",
        "SubstanceProtein",
        "SubstanceReferenceInformation",
        "SubstanceSourceMaterial",
        "SubstanceSpecification",
    ],
    "Workflow Examples": [
        "ExampleScenario",
    ],
    "Other": [
        "Device",
        "Consent",
        "Communication",
        "NutritionOrder",
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


def _get_docs_path() -> Path:
    """Get the path to the documentation directory.

    Returns:
        Path to docs/fhir-server/resources/
    """
    # Navigate from src/fhirkit/server/ui/ to docs/fhir-server/resources/
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent.parent
    return project_root / "docs" / "fhir-server" / "resources"


def _resource_type_to_filename(resource_type: str) -> str:
    """Convert a resource type to its documentation filename.

    Args:
        resource_type: FHIR resource type (e.g., "MedicationRequest")

    Returns:
        Filename with dashes (e.g., "medication-request.md")
    """
    # Convert CamelCase to kebab-case
    # Insert dash before uppercase letters (except at start)
    result = re.sub(r"(?<!^)(?=[A-Z])", "-", resource_type)
    return result.lower() + ".md"


def parse_markdown_sections(content: str) -> dict[str, str]:
    """Parse markdown content into sections by headers.

    Splits markdown by ## headers and returns a dict of section name -> content.

    Args:
        content: Full markdown content

    Returns:
        Dict mapping section names to their content
    """
    sections: dict[str, str] = {}

    # Split by ## headers (level 2)
    parts = re.split(r"^## ", content, flags=re.MULTILINE)

    # First part is the intro/overview (before first ##)
    if parts:
        intro = parts[0].strip()
        # Extract title from # header if present
        title_match = re.match(r"^# (.+?)(?:\n|$)", intro)
        if title_match:
            sections["title"] = title_match.group(1).strip()
            # Content after title is overview
            overview = intro[title_match.end() :].strip()
            if overview:
                sections["overview"] = overview
        elif intro:
            sections["overview"] = intro

    # Process remaining sections
    for part in parts[1:]:
        lines = part.split("\n", 1)
        if lines:
            section_name = lines[0].strip()
            section_content = lines[1].strip() if len(lines) > 1 else ""
            # Normalize section name to lowercase key
            key = section_name.lower().replace(" ", "_")
            sections[key] = section_content

    return sections


def load_resource_documentation(resource_type: str) -> dict[str, Any]:
    """Load and parse markdown documentation for a resource type.

    Reads the documentation file for a resource and parses it into
    structured sections for display in the UI.

    Args:
        resource_type: FHIR resource type (e.g., "Patient", "MedicationRequest")

    Returns:
        Dict containing parsed documentation:
        - exists: bool indicating if documentation file exists
        - title: Resource title from # header
        - overview: Introduction/overview text
        - supported_fields: Fields section content
        - search_parameters: Search params section content
        - examples: CRUD/usage examples section
        - generator_usage: Python generator usage section
        - related_resources: Links to related resources
        - raw_content: Full raw markdown content
    """
    docs_path = _get_docs_path()
    filename = _resource_type_to_filename(resource_type)
    file_path = docs_path / filename

    result: dict[str, Any] = {
        "exists": False,
        "title": resource_type,
        "overview": "",
        "supported_fields": "",
        "search_parameters": "",
        "examples": "",
        "generator_usage": "",
        "related_resources": "",
        "raw_content": "",
    }

    if not file_path.exists():
        return result

    try:
        content = file_path.read_text(encoding="utf-8")
        result["exists"] = True
        result["raw_content"] = content

        sections = parse_markdown_sections(content)

        # Map parsed sections to result keys
        if "title" in sections:
            result["title"] = sections["title"]
        if "overview" in sections:
            result["overview"] = sections["overview"]
        if "supported_fields" in sections:
            result["supported_fields"] = sections["supported_fields"]
        if "search_parameters" in sections:
            result["search_parameters"] = sections["search_parameters"]
        if "examples" in sections:
            result["examples"] = sections["examples"]
        if "crud_examples" in sections:
            result["examples"] = sections["crud_examples"]
        if "generator_usage" in sections:
            result["generator_usage"] = sections["generator_usage"]
        if "related_resources" in sections:
            result["related_resources"] = sections["related_resources"]

    except Exception:
        # If any error reading/parsing, return with exists=False
        result["exists"] = False

    return result


def get_resource_description(resource_type: str) -> str:
    """Get a brief description for a resource type (for tooltips).

    Args:
        resource_type: FHIR resource type

    Returns:
        Brief description string (first paragraph of overview)
    """
    doc = load_resource_documentation(resource_type)
    if not doc["exists"] or not doc["overview"]:
        return f"FHIR R4 {resource_type} resource"

    # Return first paragraph/sentence for tooltip
    overview = doc["overview"]
    # Get first paragraph (up to double newline or first 200 chars)
    first_para = overview.split("\n\n")[0]
    if len(first_para) > 200:
        # Truncate at word boundary
        first_para = first_para[:197].rsplit(" ", 1)[0] + "..."
    return first_para
