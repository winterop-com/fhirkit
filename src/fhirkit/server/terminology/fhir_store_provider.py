"""FHIRStore-backed terminology provider."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .provider import TerminologyProvider

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore


class FHIRStoreTerminologyProvider(TerminologyProvider):
    """Terminology operations using FHIRStore as backend.

    Provides FHIR terminology operations ($expand, $lookup, $validate-code, $subsumes)
    using resources stored in the FHIR server's data store.
    """

    def __init__(self, store: "FHIRStore"):
        """Initialize with a FHIRStore instance.

        Args:
            store: The FHIR data store to use for terminology lookups
        """
        self._store = store
        # Cache for CodeSystem hierarchies: {system_url: {code: set[ancestor_codes]}}
        self._hierarchy_cache: dict[str, dict[str, set[str]]] = {}

    def expand_valueset(
        self,
        url: str | None = None,
        valueset_id: str | None = None,
        filter_text: str | None = None,
        count: int = 100,
        offset: int = 0,
    ) -> dict[str, Any] | None:
        """Expand a ValueSet to list all codes."""
        valueset = self._get_valueset(url, valueset_id)
        if not valueset:
            return None

        codes = self._extract_codes_from_valueset(valueset)

        # Apply text filter
        if filter_text:
            filter_lower = filter_text.lower()
            codes = [
                c
                for c in codes
                if filter_lower in (c.get("display", "").lower()) or filter_lower in (c.get("code", "").lower())
            ]

        # Apply pagination
        total = len(codes)
        paginated_codes = codes[offset : offset + count]

        # Build expansion
        return {
            "resourceType": "ValueSet",
            "id": valueset.get("id"),
            "url": valueset.get("url"),
            "status": valueset.get("status", "active"),
            "expansion": {
                "identifier": f"urn:uuid:{uuid.uuid4()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total": total,
                "offset": offset,
                "contains": paginated_codes,
            },
        }

    def validate_code(
        self,
        valueset_url: str | None = None,
        valueset_id: str | None = None,
        code: str | None = None,
        system: str | None = None,
        coding: dict[str, Any] | None = None,
        codeable_concept: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate a code against a ValueSet."""
        valueset = self._get_valueset(valueset_url, valueset_id)
        if not valueset:
            return self._make_parameters(result=False, message=f"ValueSet not found: {valueset_url or valueset_id}")

        # Extract code and system from inputs
        codes_to_check = self._extract_codes_to_validate(code, system, coding, codeable_concept)
        if not codes_to_check:
            return self._make_parameters(result=False, message="No code provided for validation")

        # Get all codes in the ValueSet
        valueset_codes = self._extract_codes_from_valueset(valueset)

        # Check each code
        for check_code, check_system in codes_to_check:
            for vs_code in valueset_codes:
                vs_code_value = vs_code.get("code")
                vs_system = vs_code.get("system")

                # Match code value
                if vs_code_value == check_code:
                    # If system specified, it must match
                    if check_system and vs_system and check_system != vs_system:
                        continue
                    return self._make_parameters(result=True, display=vs_code.get("display"))

        return self._make_parameters(
            result=False, message=f"Code '{code or coding or codeable_concept}' not found in ValueSet"
        )

    def lookup_code(
        self,
        system: str,
        code: str,
        version: str | None = None,
    ) -> dict[str, Any] | None:
        """Look up code information from a CodeSystem."""
        codesystem = self._get_codesystem(system, version)
        if not codesystem:
            return None

        # Search for code in concept hierarchy
        concept = self._find_concept_in_codesystem(codesystem, code)
        if not concept:
            return None

        params: list[dict[str, Any]] = [
            {"name": "name", "valueString": codesystem.get("name", "")},
            {"name": "display", "valueString": concept.get("display", "")},
            {"name": "code", "valueCode": code},
            {"name": "system", "valueUri": system},
        ]

        if concept.get("definition"):
            params.append({"name": "definition", "valueString": concept["definition"]})

        if version:
            params.append({"name": "version", "valueString": version})

        return {"resourceType": "Parameters", "parameter": params}

    def subsumes(
        self,
        system: str,
        code_a: str,
        code_b: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Check subsumption relationship between two codes."""
        # Same codes are equivalent
        if code_a == code_b:
            return self._make_subsumes_result("equivalent")

        codesystem = self._get_codesystem(system, version)
        if not codesystem:
            return self._make_subsumes_result("not-subsumed", message=f"CodeSystem not found: {system}")

        # Build hierarchy if not cached
        cache_key = f"{system}|{version or ''}"
        if cache_key not in self._hierarchy_cache:
            self._hierarchy_cache[cache_key] = self._build_hierarchy(codesystem)

        hierarchy = self._hierarchy_cache[cache_key]

        # Check if code_a subsumes code_b (code_a is ancestor of code_b)
        ancestors_of_b = hierarchy.get(code_b, set())
        if code_a in ancestors_of_b:
            return self._make_subsumes_result("subsumes")

        # Check if code_b subsumes code_a (code_a is subsumed by code_b)
        ancestors_of_a = hierarchy.get(code_a, set())
        if code_b in ancestors_of_a:
            return self._make_subsumes_result("subsumed-by")

        return self._make_subsumes_result("not-subsumed")

    def member_of(
        self,
        valueset_url: str,
        code: str,
        system: str,
    ) -> bool:
        """Check if code is a member of a ValueSet."""
        result = self.validate_code(valueset_url=valueset_url, code=code, system=system)
        params = result.get("parameter", [])
        for param in params:
            if param.get("name") == "result":
                return param.get("valueBoolean", False)
        return False

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _get_valueset(self, url: str | None, valueset_id: str | None) -> dict[str, Any] | None:
        """Get ValueSet by URL or ID."""
        if valueset_id:
            return self._store.read("ValueSet", valueset_id)

        if url:
            results, _ = self._store.search("ValueSet", {"url": url})
            return results[0] if results else None

        return None

    def _get_codesystem(self, system: str, version: str | None = None) -> dict[str, Any] | None:
        """Get CodeSystem by URL and optional version."""
        params: dict[str, Any] = {"url": system}
        if version:
            params["version"] = version

        results, _ = self._store.search("CodeSystem", params)
        return results[0] if results else None

    def _extract_codes_from_valueset(self, valueset: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract all codes from a ValueSet (compose or expansion)."""
        codes: list[dict[str, Any]] = []

        # Check expansion first (pre-expanded)
        expansion = valueset.get("expansion", {})
        if expansion.get("contains"):
            return expansion["contains"]

        # Extract from compose
        compose = valueset.get("compose", {})
        for include in compose.get("include", []):
            system = include.get("system", "")

            # Direct concept list
            for concept in include.get("concept", []):
                codes.append(
                    {
                        "system": system,
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                    }
                )

            # If no concepts but system specified, try to expand from CodeSystem
            if not include.get("concept") and system:
                codesystem = self._get_codesystem(system)
                if codesystem:
                    codes.extend(self._extract_codes_from_codesystem(codesystem))

            # Include codes from referenced ValueSets
            for vs_ref in include.get("valueSet", []):
                ref_vs = self._get_valueset(vs_ref, None)
                if ref_vs:
                    codes.extend(self._extract_codes_from_valueset(ref_vs))

        return codes

    def _extract_codes_from_codesystem(self, codesystem: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract all codes from a CodeSystem recursively."""
        codes: list[dict[str, Any]] = []
        system = codesystem.get("url", "")

        def extract_recursive(concepts: list[dict[str, Any]]) -> None:
            for concept in concepts:
                codes.append(
                    {
                        "system": system,
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                    }
                )
                # Recurse into nested concepts
                if concept.get("concept"):
                    extract_recursive(concept["concept"])

        extract_recursive(codesystem.get("concept", []))
        return codes

    def _extract_codes_to_validate(
        self,
        code: str | None,
        system: str | None,
        coding: dict[str, Any] | None,
        codeable_concept: dict[str, Any] | None,
    ) -> list[tuple[str, str | None]]:
        """Extract (code, system) pairs from various input formats."""
        result: list[tuple[str, str | None]] = []

        if code:
            result.append((code, system))

        if coding:
            result.append((coding.get("code", ""), coding.get("system")))

        if codeable_concept:
            for c in codeable_concept.get("coding", []):
                result.append((c.get("code", ""), c.get("system")))

        return [(c, s) for c, s in result if c]  # Filter out empty codes

    def _find_concept_in_codesystem(self, codesystem: dict[str, Any], code: str) -> dict[str, Any] | None:
        """Find a concept by code in a CodeSystem (searches hierarchy)."""

        def search_recursive(concepts: list[dict[str, Any]]) -> dict[str, Any] | None:
            for concept in concepts:
                if concept.get("code") == code:
                    return concept
                # Search children
                if concept.get("concept"):
                    found = search_recursive(concept["concept"])
                    if found:
                        return found
            return None

        return search_recursive(codesystem.get("concept", []))

    def _build_hierarchy(self, codesystem: dict[str, Any]) -> dict[str, set[str]]:
        """Build a map of code -> set of ancestor codes from CodeSystem hierarchy."""
        hierarchy: dict[str, set[str]] = {}

        def build_recursive(concepts: list[dict[str, Any]], ancestors: set[str]) -> None:
            for concept in concepts:
                code = concept.get("code", "")
                if code:
                    hierarchy[code] = ancestors.copy()

                    # Recurse with this code added to ancestors
                    if concept.get("concept"):
                        new_ancestors = ancestors | {code}
                        build_recursive(concept["concept"], new_ancestors)

        build_recursive(codesystem.get("concept", []), set())
        return hierarchy

    def _make_parameters(
        self,
        result: bool,
        display: str | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Create a FHIR Parameters resource for validate-code response."""
        params: list[dict[str, Any]] = [{"name": "result", "valueBoolean": result}]

        if display:
            params.append({"name": "display", "valueString": display})

        if message:
            params.append({"name": "message", "valueString": message})

        return {"resourceType": "Parameters", "parameter": params}

    def _make_subsumes_result(self, outcome: str, message: str | None = None) -> dict[str, Any]:
        """Create a FHIR Parameters resource for $subsumes response."""
        params: list[dict[str, Any]] = [{"name": "outcome", "valueCode": outcome}]

        if message:
            params.append({"name": "message", "valueString": message})

        return {"resourceType": "Parameters", "parameter": params}
