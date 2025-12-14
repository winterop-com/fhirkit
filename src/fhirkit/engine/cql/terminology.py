"""Terminology adapter for CQL evaluation.

This module provides an adapter that connects CQL evaluation to the
FHIR server's terminology provider, enabling ValueSet expansion and
code membership testing during CQL evaluation.
"""

from typing import TYPE_CHECKING, Any

from .types import CQLCode

if TYPE_CHECKING:
    from ...server.storage.fhir_store import FHIRStore
    from ...server.terminology import FHIRStoreTerminologyProvider
    from .datasource import InMemoryDataSource


class CQLTerminologyAdapter:
    """Adapter connecting CQL evaluation to FHIR terminology services.

    This adapter provides ValueSet expansion and code membership testing
    for CQL evaluation by delegating to the FHIR server's terminology
    provider.

    Example:
        from fhirkit.server.storage.fhir_store import FHIRStore
        from fhirkit.engine.cql.terminology import CQLTerminologyAdapter
        from fhirkit.engine.cql.datasource import InMemoryDataSource

        store = FHIRStore()
        # ... populate store with terminology resources ...

        adapter = CQLTerminologyAdapter(store)
        data_source = InMemoryDataSource()

        # Expand a ValueSet and add codes to the data source
        codes = adapter.expand_valueset("http://example.org/ValueSet/diabetes")
        data_source.add_valueset("http://example.org/ValueSet/diabetes", codes)
    """

    def __init__(self, store: "FHIRStore"):
        """Initialize the terminology adapter.

        Args:
            store: The FHIR data store containing terminology resources
        """
        self._store = store
        self._provider: "FHIRStoreTerminologyProvider | None" = None
        # Cache for expanded valuesets: {url: [CQLCode, ...]}
        self._cache: dict[str, list[CQLCode]] = {}

    @property
    def provider(self) -> "FHIRStoreTerminologyProvider":
        """Get or create the terminology provider (lazy initialization)."""
        if self._provider is None:
            from ...server.terminology import FHIRStoreTerminologyProvider

            self._provider = FHIRStoreTerminologyProvider(self._store)
        return self._provider

    def expand_valueset(self, url: str, use_cache: bool = True) -> list[CQLCode]:
        """Expand a ValueSet to a list of CQL codes.

        Args:
            url: ValueSet URL (canonical identifier)
            use_cache: Whether to use cached expansion (default: True)

        Returns:
            List of CQLCode objects from the expanded ValueSet.
            Returns empty list if ValueSet not found.

        Example:
            codes = adapter.expand_valueset("http://example.org/ValueSet/diabetes")
            for code in codes:
                print(f"{code.system}|{code.code}: {code.display}")
        """
        # Check cache first
        if use_cache and url in self._cache:
            return self._cache[url]

        # Expand using terminology provider
        expansion = self.provider.expand_valueset(url=url)
        if not expansion:
            return []

        # Extract codes from expansion
        codes: list[CQLCode] = []
        contains = expansion.get("expansion", {}).get("contains", [])

        for item in contains:
            code = CQLCode(
                code=item.get("code", ""),
                system=item.get("system", ""),
                display=item.get("display"),
            )
            codes.append(code)

        # Cache the result
        self._cache[url] = codes

        return codes

    def in_valueset(self, code: CQLCode | str, system: str | None, valueset_url: str) -> bool:
        """Check if a code is a member of a ValueSet.

        Args:
            code: CQL code or code string
            system: Code system URI (required if code is string)
            valueset_url: ValueSet URL to check against

        Returns:
            True if the code is in the ValueSet, False otherwise

        Example:
            # With CQLCode
            code = CQLCode(code="E11.9", system="http://hl7.org/fhir/sid/icd-10")
            is_member = adapter.in_valueset(code, None, "http://example.org/vs/diabetes")

            # With string code
            is_member = adapter.in_valueset(
                "E11.9",
                "http://hl7.org/fhir/sid/icd-10",
                "http://example.org/vs/diabetes"
            )
        """
        # Extract code and system
        if isinstance(code, CQLCode):
            code_value = code.code
            code_system = code.system
        else:
            code_value = code
            code_system = system or ""

        # Use the provider's member_of method
        return self.provider.member_of(valueset_url, code_value, code_system)

    def lookup_code(self, code: str, system: str) -> dict[str, Any] | None:
        """Look up code information from a CodeSystem.

        Args:
            code: Code value
            system: CodeSystem URL

        Returns:
            Dictionary with code information or None if not found

        Example:
            info = adapter.lookup_code("E11.9", "http://hl7.org/fhir/sid/icd-10")
            if info:
                print(f"Display: {info.get('display')}")
        """
        result = self.provider.lookup_code(system, code)
        if not result:
            return None

        # Extract relevant information from Parameters
        info: dict[str, Any] = {"code": code, "system": system}
        for param in result.get("parameter", []):
            name = param.get("name")
            if name == "display":
                info["display"] = param.get("valueString")
            elif name == "definition":
                info["definition"] = param.get("valueString")
            elif name == "name":
                info["name"] = param.get("valueString")

        return info

    def subsumes(self, system: str, code_a: str, code_b: str) -> str:
        """Check subsumption relationship between two codes.

        Args:
            system: CodeSystem URL
            code_a: First code (potential ancestor)
            code_b: Second code (potential descendant)

        Returns:
            Relationship string: "equivalent", "subsumes", "subsumed-by", or "not-subsumed"

        Example:
            result = adapter.subsumes(
                "http://snomed.info/sct",
                "73211009",  # Diabetes mellitus
                "44054006"   # Type 2 diabetes
            )
            if result == "subsumes":
                print("Diabetes mellitus is a parent of Type 2 diabetes")
        """
        result = self.provider.subsumes(system, code_a, code_b)

        # Extract outcome from Parameters
        for param in result.get("parameter", []):
            if param.get("name") == "outcome":
                return param.get("valueCode", "not-subsumed")

        return "not-subsumed"

    def clear_cache(self) -> None:
        """Clear the ValueSet expansion cache."""
        self._cache.clear()

    def preload_valueset(self, url: str) -> None:
        """Preload a ValueSet into the cache.

        Useful for warming the cache before CQL evaluation to avoid
        repeated expansions during evaluation.

        Args:
            url: ValueSet URL to preload
        """
        self.expand_valueset(url, use_cache=False)

    def preload_valuesets(self, urls: list[str]) -> None:
        """Preload multiple ValueSets into the cache.

        Args:
            urls: List of ValueSet URLs to preload
        """
        for url in urls:
            self.preload_valueset(url)


def create_terminology_datasource(
    store: "FHIRStore",
    valueset_urls: list[str] | None = None,
) -> tuple["InMemoryDataSource", CQLTerminologyAdapter]:
    """Create a data source with terminology support.

    Convenience function that creates both an InMemoryDataSource and
    a CQLTerminologyAdapter, optionally preloading ValueSets.

    Args:
        store: FHIR data store with terminology resources
        valueset_urls: Optional list of ValueSet URLs to preload

    Returns:
        Tuple of (data_source, terminology_adapter)

    Example:
        store = FHIRStore()
        # ... populate store ...

        data_source, adapter = create_terminology_datasource(
            store,
            valueset_urls=[
                "http://example.org/vs/diabetes-codes",
                "http://example.org/vs/a1c-codes"
            ]
        )

        # Now use data_source with CQL evaluator
        evaluator = CQLEvaluator(data_source=data_source)
    """
    from .datasource import InMemoryDataSource

    data_source = InMemoryDataSource()
    adapter = CQLTerminologyAdapter(store)

    # Preload and register ValueSets
    if valueset_urls:
        for url in valueset_urls:
            codes = adapter.expand_valueset(url)
            data_source.add_valueset(url, codes)

    return data_source, adapter
