"""CDS Hooks CQL execution integration."""

from pathlib import Path
from typing import Any

from ...engine.cql import CQLEvaluator
from ...engine.cql.datasource import InMemoryDataSource
from ..config.settings import CDSHooksSettings, CDSServiceConfig
from ..models.request import CDSRequest


class CDSExecutor:
    """Executes CQL logic for CDS services."""

    def __init__(self, settings: CDSHooksSettings):
        self._settings = settings
        self._evaluator_cache: dict[str, CQLEvaluator] = {}
        self._library_cache: dict[str, str] = {}

    def execute(
        self,
        service: CDSServiceConfig,
        request: CDSRequest,
    ) -> dict[str, Any]:
        """Execute CQL definitions for a CDS service.

        Args:
            service: Service configuration
            request: CDS Hook request

        Returns:
            Dictionary mapping definition names to their evaluated values
        """
        # Get or create evaluator for this service
        evaluator = self._get_evaluator(service)

        # Build data source from prefetch
        data_source = self._build_data_source(request)

        # Get patient resource for context
        patient = self._extract_patient(request)

        # Evaluate each configured definition
        results: dict[str, Any] = {}
        for definition_name in service.evaluateDefinitions:
            try:
                result = evaluator.evaluate_definition(
                    definition_name,
                    resource=patient,
                    data_source=data_source,
                )
                results[definition_name] = self._serialize_result(result)
            except Exception as e:
                results[definition_name] = {
                    "_error": str(e),
                    "_type": type(e).__name__,
                }

        # Add context information
        results["_context"] = {
            "patientId": request.context.get("patientId"),
            "userId": request.context.get("userId"),
            "hookInstance": str(request.hookInstance),
        }

        return results

    def _get_evaluator(self, service: CDSServiceConfig) -> CQLEvaluator:
        """Get or create cached CQL evaluator for service."""
        if service.id not in self._evaluator_cache:
            evaluator = CQLEvaluator()

            # Find and load CQL library
            cql_source = self._load_cql_library(service.cqlLibrary)
            evaluator.compile(cql_source)

            self._evaluator_cache[service.id] = evaluator

        return self._evaluator_cache[service.id]

    def _load_cql_library(self, library_path: str) -> str:
        """Load CQL library source from file."""
        if library_path in self._library_cache:
            return self._library_cache[library_path]

        # Try with base path first
        if self._settings.cql_library_path:
            full_path = Path(self._settings.cql_library_path) / library_path
            if full_path.exists():
                source = full_path.read_text()
                self._library_cache[library_path] = source
                return source

        # Try as absolute/relative path
        path = Path(library_path)
        if path.exists():
            source = path.read_text()
            self._library_cache[library_path] = source
            return source

        raise FileNotFoundError(f"CQL library not found: {library_path}")

    def _build_data_source(self, request: CDSRequest) -> InMemoryDataSource:
        """Build data source from prefetch data."""
        data_source = InMemoryDataSource()

        if request.prefetch:
            for key, value in request.prefetch.items():
                if value is None:
                    continue

                if isinstance(value, dict):
                    resource_type = value.get("resourceType")
                    if resource_type == "Bundle":
                        # Extract resources from bundle
                        for entry in value.get("entry", []):
                            resource = entry.get("resource")
                            if resource:
                                data_source.add_resource(resource)
                    elif resource_type:
                        # Single resource
                        data_source.add_resource(value)

        return data_source

    def _extract_patient(self, request: CDSRequest) -> dict[str, Any] | None:
        """Extract patient resource from prefetch."""
        if not request.prefetch:
            return None

        # Look for patient in common prefetch keys
        for key in ["patient", "Patient"]:
            if key in request.prefetch:
                resource = request.prefetch[key]
                if isinstance(resource, dict) and resource.get("resourceType") == "Patient":
                    return resource

        return None

    def _serialize_result(self, result: Any) -> Any:
        """Serialize CQL result for JSON response."""
        if result is None:
            return None

        if isinstance(result, (str, int, float, bool)):
            return result

        if isinstance(result, list):
            return [self._serialize_result(item) for item in result]

        if isinstance(result, dict):
            return {k: self._serialize_result(v) for k, v in result.items()}

        # Handle CQL types
        if hasattr(result, "elements"):
            # CQLTuple
            return {k: self._serialize_result(v) for k, v in result.elements.items()}

        if hasattr(result, "value") and hasattr(result, "unit"):
            # Quantity
            return {"value": result.value, "unit": result.unit}

        if hasattr(result, "low") and hasattr(result, "high"):
            # Interval
            return {
                "low": self._serialize_result(result.low),
                "high": self._serialize_result(result.high),
            }

        if hasattr(result, "code") and hasattr(result, "system"):
            # Code/Concept
            return {
                "code": result.code,
                "system": result.system,
                "display": getattr(result, "display", None),
            }

        # Date/datetime
        if hasattr(result, "isoformat"):
            return result.isoformat()

        # Fallback to string representation
        return str(result)

    def clear_cache(self, service_id: str | None = None) -> None:
        """Clear evaluator cache."""
        if service_id:
            self._evaluator_cache.pop(service_id, None)
        else:
            self._evaluator_cache.clear()
            self._library_cache.clear()
