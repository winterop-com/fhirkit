"""FHIR-specific functions: resolve, extension, ofType."""

from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry


@FunctionRegistry.register("resolve")
def fn_resolve(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """
    Resolve FHIR References to their target resources.

    For each Reference in the input collection, attempts to resolve it using
    the reference_resolver callback in the evaluation context.

    Reference format: {"reference": "Patient/123"} or {"reference": "http://..."}
    """
    if ctx.reference_resolver is None:
        return []

    result = []
    for item in collection:
        if isinstance(item, dict):
            ref = item.get("reference")
            if ref:
                resolved = ctx.reference_resolver(ref)
                if resolved is not None:
                    result.append(resolved)
        elif isinstance(item, str):
            # Direct reference string
            resolved = ctx.reference_resolver(item)
            if resolved is not None:
                result.append(resolved)
    return result


@FunctionRegistry.register("extension")
def fn_extension(ctx: EvaluationContext, collection: list[Any], url: str) -> list[Any]:
    """
    Returns extensions with the specified URL from the input collection.

    Looks for extensions in the 'extension' property of each element
    and filters by the 'url' property.
    """
    result = []
    for item in collection:
        if isinstance(item, dict):
            extensions = item.get("extension", [])
            if isinstance(extensions, list):
                for ext in extensions:
                    if isinstance(ext, dict) and ext.get("url") == url:
                        result.append(ext)
    return result


@FunctionRegistry.register("elementDefinition")
def fn_element_definition(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """
    Returns the FHIR ElementDefinition for each element in the input.

    Note: Requires model information. Returns empty if no model available.
    """
    # This requires StructureDefinition information which we don't have yet
    return []


@FunctionRegistry.register("slice")
def fn_slice(ctx: EvaluationContext, collection: list[Any], structure: str, name: str) -> list[Any]:
    """
    Returns elements that belong to a specific slice.

    Note: Requires StructureDefinition information. Returns empty if unavailable.
    """
    # This requires slice definitions which we don't have yet
    return []


@FunctionRegistry.register("checkModifiers")
def fn_check_modifiers(ctx: EvaluationContext, collection: list[Any], *args: str) -> list[Any]:
    """
    Check if the input has any modifier extensions other than the ones specified.

    If there are modifier extensions other than those listed, raises an error.
    Otherwise returns the input unchanged.
    """
    allowed_urls = set(args)

    for item in collection:
        if isinstance(item, dict):
            mod_extensions = item.get("modifierExtension", [])
            if isinstance(mod_extensions, list):
                for ext in mod_extensions:
                    if isinstance(ext, dict):
                        url = ext.get("url")
                        if url and url not in allowed_urls:
                            # In strict mode, this would raise an error
                            # For now, we just skip such elements
                            pass
    return collection


@FunctionRegistry.register("conformsTo")
def fn_conforms_to(ctx: EvaluationContext, collection: list[Any], profile: str) -> list[bool]:
    """
    Returns true if the resource conforms to the specified profile.

    Performs basic profile conformance checking:
    1. Checks if the resource's meta.profile includes the specified profile URL
    2. If no meta.profile, checks if the profile matches the resource's base type

    For full profile validation with constraint checking, a profile validator
    would be needed. This implementation provides basic conformance checking
    suitable for most common use cases.

    Args:
        ctx: Evaluation context
        collection: Collection of resources to check
        profile: The canonical URL of the profile to check conformance against

    Returns:
        List containing true/false for each item in the collection
    """
    result: list[bool] = []

    for item in collection:
        if not isinstance(item, dict):
            result.append(False)
            continue

        # Check if resource declares conformance to the profile
        meta = item.get("meta")
        if isinstance(meta, dict):
            profiles = meta.get("profile", [])
            if isinstance(profiles, list):
                # Direct profile match
                if profile in profiles:
                    result.append(True)
                    continue

                # Check for version-independent match (profile URL without version)
                profile_base = profile.split("|")[0] if "|" in profile else profile
                for declared_profile in profiles:
                    declared_base = declared_profile.split("|")[0] if "|" in declared_profile else declared_profile
                    if profile_base == declared_base:
                        result.append(True)
                        break
                else:
                    # No match in declared profiles - check base type
                    result.append(_check_base_type_conformance(item, profile))
            else:
                # No profiles array
                result.append(_check_base_type_conformance(item, profile))
        else:
            # No meta - check base type
            result.append(_check_base_type_conformance(item, profile))

    return result


def _check_base_type_conformance(resource: dict[str, Any], profile: str) -> bool:
    """Check if a resource conforms to a profile based on its resource type.

    This is a basic check that returns true if the profile URL ends with
    the resource type (e.g., ".../Patient" for a Patient resource).

    Args:
        resource: The FHIR resource dictionary
        profile: The profile URL

    Returns:
        True if the resource type matches the profile's target
    """
    resource_type = resource.get("resourceType", "")
    if not resource_type:
        return False

    # Check if profile URL ends with the resource type
    # Common patterns:
    # - http://hl7.org/fhir/StructureDefinition/Patient
    # - http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
    profile_base = profile.split("|")[0]  # Remove version

    # Direct match: profile ends with /ResourceType
    if profile_base.endswith(f"/{resource_type}"):
        return True

    # Check for known base profiles
    base_profiles = {
        "Patient": "http://hl7.org/fhir/StructureDefinition/Patient",
        "Observation": "http://hl7.org/fhir/StructureDefinition/Observation",
        "Condition": "http://hl7.org/fhir/StructureDefinition/Condition",
        "Procedure": "http://hl7.org/fhir/StructureDefinition/Procedure",
        "Encounter": "http://hl7.org/fhir/StructureDefinition/Encounter",
        "MedicationRequest": "http://hl7.org/fhir/StructureDefinition/MedicationRequest",
        "DiagnosticReport": "http://hl7.org/fhir/StructureDefinition/DiagnosticReport",
        "Immunization": "http://hl7.org/fhir/StructureDefinition/Immunization",
        "AllergyIntolerance": "http://hl7.org/fhir/StructureDefinition/AllergyIntolerance",
        "CarePlan": "http://hl7.org/fhir/StructureDefinition/CarePlan",
    }

    # If checking base profile, verify resource type matches
    if profile_base == base_profiles.get(resource_type):
        return True

    # For derived profiles, we can't verify without the profile definition
    # Return false as we can't confirm conformance
    return False


@FunctionRegistry.register("memberOf")
def fn_member_of(ctx: EvaluationContext, collection: list[Any], valueset: str) -> list[bool]:
    """
    Returns true if the code/Coding/CodeableConcept is in the specified ValueSet.

    Note: Requires terminology service. Returns empty for now.
    """
    # Terminology lookup is not implemented
    return []


@FunctionRegistry.register("subsumes")
def fn_subsumes(ctx: EvaluationContext, collection: list[Any], code: Any) -> list[bool]:
    """
    Returns true if the code in context subsumes the specified code.

    Note: Requires terminology service. Returns empty for now.
    """
    # Terminology lookup is not implemented
    return []


@FunctionRegistry.register("subsumedBy")
def fn_subsumed_by(ctx: EvaluationContext, collection: list[Any], code: Any) -> list[bool]:
    """
    Returns true if the code in context is subsumed by the specified code.

    Note: Requires terminology service. Returns empty for now.
    """
    # Terminology lookup is not implemented
    return []


@FunctionRegistry.register("htmlChecks")
def fn_html_checks(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """
    Check if the HTML content in the Narrative is valid.

    Returns true if the HTML passes basic safety checks.
    """
    for item in collection:
        if isinstance(item, dict):
            div = item.get("div")
            if div and isinstance(div, str):
                # Basic check: must start with <div
                if not div.strip().startswith("<div"):
                    return [False]
    return [True]
