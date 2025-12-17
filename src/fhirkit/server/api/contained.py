"""Contained resource handling for FHIR resources.

Implements proper handling of contained resources per FHIR R4 spec:
https://hl7.org/fhir/R4/references.html#contained
"""

from typing import Any


class ContainedResourceError(Exception):
    """Error in contained resource handling."""

    def __init__(self, message: str, resource_id: str | None = None):
        self.message = message
        self.resource_id = resource_id
        super().__init__(message)


def validate_contained_resources(resource: dict[str, Any]) -> list[str]:
    """Validate contained resources in a FHIR resource.

    Checks:
    - Each contained resource has an id
    - Contained resource IDs are unique within the resource
    - Internal references (#id) point to existing contained resources

    Args:
        resource: FHIR resource with potential contained resources

    Returns:
        List of validation issues (empty if valid)
    """
    issues: list[str] = []
    contained = resource.get("contained", [])

    if not contained:
        return issues

    # Check each contained resource
    contained_ids: set[str] = set()
    for idx, contained_resource in enumerate(contained):
        # Must have resourceType
        if "resourceType" not in contained_resource:
            issues.append(f"Contained resource at index {idx} missing resourceType")
            continue

        # Must have id
        resource_id = contained_resource.get("id")
        if not resource_id:
            issues.append(f"Contained {contained_resource.get('resourceType', 'resource')} at index {idx} missing id")
            continue

        # ID should not have # prefix in stored form
        clean_id = resource_id.lstrip("#")

        # Check for duplicate IDs
        if clean_id in contained_ids:
            issues.append(f"Duplicate contained resource id: {clean_id}")
        contained_ids.add(clean_id)

    # Validate internal references
    internal_refs = find_internal_references(resource)
    for ref_path, ref_value in internal_refs:
        ref_id = ref_value.lstrip("#")
        if ref_id not in contained_ids:
            issues.append(f"Internal reference '{ref_value}' at {ref_path} not found in contained resources")

    return issues


def find_internal_references(obj: Any, path: str = "") -> list[tuple[str, str]]:
    """Find all internal references (#id) in a resource.

    Args:
        obj: Object to search (resource or nested object)
        path: Current path in the resource

    Returns:
        List of (path, reference) tuples for internal references
    """
    refs: list[tuple[str, str]] = []

    if isinstance(obj, dict):
        # Skip the contained array itself
        if path.endswith(".contained") or path == "contained":
            return refs

        # Check for reference field
        if "reference" in obj:
            ref_value = obj["reference"]
            if isinstance(ref_value, str) and ref_value.startswith("#"):
                refs.append((f"{path}.reference" if path else "reference", ref_value))

        # Recurse into nested objects
        for key, value in obj.items():
            if key == "contained":
                continue  # Skip contained array
            child_path = f"{path}.{key}" if path else key
            refs.extend(find_internal_references(value, child_path))

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            child_path = f"{path}[{idx}]"
            refs.extend(find_internal_references(item, child_path))

    return refs


def normalize_contained_ids(resource: dict[str, Any]) -> dict[str, Any]:
    """Normalize contained resource IDs (remove # prefix if present).

    FHIR spec says contained resource IDs should NOT have # prefix in storage,
    but references TO them should use #id format.

    Args:
        resource: FHIR resource to normalize

    Returns:
        Resource with normalized contained IDs
    """
    if "contained" not in resource:
        return resource

    resource = dict(resource)
    resource["contained"] = [_normalize_contained_resource(c) for c in resource["contained"]]

    return resource


def _normalize_contained_resource(contained: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single contained resource."""
    if "id" in contained:
        contained = dict(contained)
        contained["id"] = contained["id"].lstrip("#")
    return contained


def resolve_contained_reference(resource: dict[str, Any], reference: str) -> dict[str, Any] | None:
    """Resolve an internal reference to a contained resource.

    Args:
        resource: The parent resource containing the contained resources
        reference: The reference string (e.g., "#med1")

    Returns:
        The contained resource or None if not found
    """
    if not reference.startswith("#"):
        return None

    ref_id = reference.lstrip("#")
    for contained in resource.get("contained", []):
        if contained.get("id") == ref_id or contained.get("id") == f"#{ref_id}":
            return contained

    return None


def extract_contained_resources(resource: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all contained resources from a resource.

    Args:
        resource: FHIR resource

    Returns:
        List of contained resources with parent context
    """
    contained = resource.get("contained", [])
    parent_type = resource.get("resourceType", "Unknown")
    parent_id = resource.get("id", "unknown")

    result = []
    for c in contained:
        # Create a copy with parent context
        extracted = dict(c)
        extracted["_containedIn"] = {
            "resourceType": parent_type,
            "id": parent_id,
        }
        result.append(extracted)

    return result


def get_contained_by_type(resource: dict[str, Any], resource_type: str) -> list[dict[str, Any]]:
    """Get contained resources of a specific type.

    Args:
        resource: Parent resource
        resource_type: Type of contained resources to return

    Returns:
        List of contained resources matching the type
    """
    return [c for c in resource.get("contained", []) if c.get("resourceType") == resource_type]


def add_contained_resource(
    resource: dict[str, Any],
    contained: dict[str, Any],
    auto_id: bool = True,
) -> tuple[dict[str, Any], str]:
    """Add a contained resource to a parent resource.

    Args:
        resource: Parent resource
        contained: Resource to contain
        auto_id: Whether to auto-generate ID if missing

    Returns:
        Tuple of (updated resource, contained resource ID)

    Raises:
        ContainedResourceError: If contained resource is invalid
    """
    if "resourceType" not in contained:
        raise ContainedResourceError("Contained resource missing resourceType")

    resource = dict(resource)
    if "contained" not in resource:
        resource["contained"] = []
    else:
        resource["contained"] = list(resource["contained"])

    contained = dict(contained)

    # Generate ID if needed
    if "id" not in contained:
        if not auto_id:
            raise ContainedResourceError("Contained resource missing id")
        # Generate unique ID
        existing_ids = {c.get("id", "").lstrip("#") for c in resource["contained"]}
        idx = 1
        while f"{contained['resourceType'].lower()}-{idx}" in existing_ids:
            idx += 1
        contained["id"] = f"{contained['resourceType'].lower()}-{idx}"

    # Normalize ID (remove # prefix)
    contained["id"] = contained["id"].lstrip("#")
    contained_id = contained["id"]

    # Check for duplicate
    if any(c.get("id") == contained_id for c in resource["contained"]):
        raise ContainedResourceError(f"Duplicate contained resource id: {contained_id}", contained_id)

    resource["contained"].append(contained)

    return resource, contained_id


def create_internal_reference(contained_id: str) -> dict[str, str]:
    """Create an internal reference to a contained resource.

    Args:
        contained_id: The ID of the contained resource

    Returns:
        Reference object with #id format
    """
    clean_id = contained_id.lstrip("#")
    return {"reference": f"#{clean_id}"}


def replace_contained_resource(
    resource: dict[str, Any],
    contained_id: str,
    new_contained: dict[str, Any],
) -> dict[str, Any]:
    """Replace a contained resource.

    Args:
        resource: Parent resource
        contained_id: ID of contained resource to replace
        new_contained: New contained resource

    Returns:
        Updated resource

    Raises:
        ContainedResourceError: If contained resource not found
    """
    clean_id = contained_id.lstrip("#")
    resource = dict(resource)
    resource["contained"] = list(resource.get("contained", []))

    for idx, c in enumerate(resource["contained"]):
        if c.get("id") == clean_id or c.get("id") == f"#{clean_id}":
            new_contained = dict(new_contained)
            new_contained["id"] = clean_id
            resource["contained"][idx] = new_contained
            return resource

    raise ContainedResourceError(f"Contained resource not found: {contained_id}", contained_id)


def remove_contained_resource(resource: dict[str, Any], contained_id: str) -> dict[str, Any]:
    """Remove a contained resource.

    Args:
        resource: Parent resource
        contained_id: ID of contained resource to remove

    Returns:
        Updated resource

    Raises:
        ContainedResourceError: If contained resource not found or still referenced
    """
    clean_id = contained_id.lstrip("#")

    # Check if still referenced
    refs = find_internal_references(resource)
    for ref_path, ref_value in refs:
        if ref_value.lstrip("#") == clean_id:
            raise ContainedResourceError(
                f"Cannot remove contained resource '{clean_id}': still referenced at {ref_path}",
                clean_id,
            )

    resource = dict(resource)
    resource["contained"] = [c for c in resource.get("contained", []) if c.get("id") != clean_id]

    return resource
