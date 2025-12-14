"""Handler for _include and _revinclude search parameters.

This module implements the FHIR _include and _revinclude search parameters:
- _include: Follow references FROM search results to include related resources
- _revinclude: Find resources that REFERENCE the search results

Example usage:
    GET /Condition?_include=Condition:subject
    -> Returns Conditions + the Patients they reference

    GET /Patient?_revinclude=Condition:patient
    -> Returns Patients + Conditions that reference them

See: https://hl7.org/fhir/R4/search.html#include
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .compartments import (
    REFERENCE_PATHS,
    get_all_references_from_path,
    get_reference_path,
)

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore


class IncludeHandler:
    """Handler for processing _include and _revinclude search parameters."""

    def __init__(self, store: FHIRStore) -> None:
        """Initialize the handler.

        Args:
            store: The FHIR store to resolve references from
        """
        self.store = store

    def parse_include_param(self, param: str) -> tuple[str, str, str | None]:
        """Parse an _include or _revinclude parameter.

        Format: ResourceType:searchParam[:targetType]
        Examples:
            - "Condition:subject" -> ("Condition", "subject", None)
            - "Condition:subject:Patient" -> ("Condition", "subject", "Patient")

        Args:
            param: The include parameter string

        Returns:
            Tuple of (source_type, search_param, target_type)
        """
        parts = param.split(":")
        source_type = parts[0] if parts else ""
        search_param = parts[1] if len(parts) > 1 else ""
        target_type = parts[2] if len(parts) > 2 else None
        return source_type, search_param, target_type

    def process_include(
        self,
        resources: list[dict[str, Any]],
        include_params: list[str],
    ) -> list[dict[str, Any]]:
        """Process _include parameters.

        _include follows references FROM search results to get related resources.
        For example, Condition?_include=Condition:subject includes the Patient
        resources that are referenced by the Conditions.

        Args:
            resources: The primary search results
            include_params: List of _include parameter values

        Returns:
            List of included resources (deduplicated)
        """
        included: dict[str, dict[str, Any]] = {}  # ref -> resource (for dedup)

        for param in include_params:
            source_type, search_param, target_type = self.parse_include_param(param)

            if not source_type or not search_param:
                continue

            # Get the reference paths for this search parameter
            ref_paths = get_reference_path(source_type, search_param)
            if not ref_paths:
                # Try to find paths from REFERENCE_PATHS directly
                ref_paths = REFERENCE_PATHS.get(source_type, {}).get(search_param, [])

            for resource in resources:
                # Only process resources of the source type
                if resource.get("resourceType") != source_type:
                    continue

                # Extract references from all paths
                for path in ref_paths:
                    refs = get_all_references_from_path(resource, path)

                    for ref in refs:
                        # Apply target type filter if specified
                        if target_type and not ref.startswith(f"{target_type}/"):
                            continue

                        # Skip if already included
                        if ref in included:
                            continue

                        # Resolve the reference
                        resolved = self._resolve_reference(ref)
                        if resolved:
                            included[ref] = resolved

        return list(included.values())

    def process_revinclude(
        self,
        resources: list[dict[str, Any]],
        revinclude_params: list[str],
    ) -> list[dict[str, Any]]:
        """Process _revinclude parameters.

        _revinclude finds resources that REFERENCE the search results.
        For example, Patient?_revinclude=Condition:patient includes all
        Conditions that have a patient reference to the returned Patients.

        Args:
            resources: The primary search results
            revinclude_params: List of _revinclude parameter values

        Returns:
            List of included resources (deduplicated)
        """
        included: dict[str, dict[str, Any]] = {}  # ref -> resource (for dedup)

        # Build a set of references from the search results
        result_refs: set[str] = set()
        for resource in resources:
            rtype = resource.get("resourceType")
            rid = resource.get("id")
            if rtype and rid:
                result_refs.add(f"{rtype}/{rid}")

        for param in revinclude_params:
            source_type, search_param, target_type = self.parse_include_param(param)

            if not source_type or not search_param:
                continue

            # Get the reference paths for this search parameter
            ref_paths = get_reference_path(source_type, search_param)
            if not ref_paths:
                ref_paths = REFERENCE_PATHS.get(source_type, {}).get(search_param, [])

            if not ref_paths:
                continue

            # Get all resources of the source type
            all_source_resources = self.store.get_all_resources(source_type)

            for resource in all_source_resources:
                # Check if this resource references any of our search results
                for path in ref_paths:
                    refs = get_all_references_from_path(resource, path)

                    for ref in refs:
                        # Check if this reference points to one of our results
                        if ref in result_refs:
                            ref_key = f"{source_type}/{resource.get('id')}"
                            if ref_key not in included:
                                included[ref_key] = resource
                            break
                    else:
                        continue
                    break  # Found a match, no need to check other paths

        return list(included.values())

    def _resolve_reference(self, ref: str) -> dict[str, Any] | None:
        """Resolve a reference string to a resource.

        Args:
            ref: Reference string like "Patient/123"

        Returns:
            The resolved resource or None if not found
        """
        # Use the store's _by_id dict directly for efficiency
        if ref in self.store._deleted:
            return None
        return self.store._by_id.get(ref)


def get_search_includes(resource_type: str) -> list[str]:
    """Get the list of valid _include parameters for a resource type.

    Used to populate CapabilityStatement.rest.resource.searchInclude.

    Args:
        resource_type: The FHIR resource type

    Returns:
        List of include parameter names (e.g., ["Condition:subject", "Condition:encounter"])
    """
    ref_paths = REFERENCE_PATHS.get(resource_type, {})
    return [f"{resource_type}:{param}" for param in ref_paths.keys()]


def get_search_rev_includes(resource_type: str) -> list[str]:
    """Get the list of valid _revinclude parameters for a resource type.

    Used to populate CapabilityStatement.rest.resource.searchRevInclude.
    Returns all resource types that have a search parameter referencing
    this resource type.

    Args:
        resource_type: The FHIR resource type (target of references)

    Returns:
        List of revinclude parameter names
    """
    rev_includes: list[str] = []

    for source_type, params in REFERENCE_PATHS.items():
        for param, paths in params.items():
            # Check if any path could reference our resource type
            # This is a heuristic - we look for params like "patient", "subject"
            # that commonly reference the target type
            if resource_type == "Patient" and param in ("patient", "subject"):
                rev_includes.append(f"{source_type}:{param}")
            elif resource_type == "Encounter" and param == "encounter":
                rev_includes.append(f"{source_type}:{param}")
            elif resource_type == "Practitioner" and param in (
                "performer",
                "requester",
                "asserter",
                "practitioner",
            ):
                rev_includes.append(f"{source_type}:{param}")
            elif resource_type == "Organization" and param in (
                "organization",
                "service-provider",
            ):
                rev_includes.append(f"{source_type}:{param}")

    return rev_includes
