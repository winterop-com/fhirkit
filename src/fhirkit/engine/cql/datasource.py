"""FHIR data source implementations for CQL evaluation.

This module provides concrete implementations of the DataSource protocol
for retrieving FHIR resources during CQL evaluation.

Classes:
    FHIRDataSource: Abstract base class defining the data source interface
    InMemoryDataSource: In-memory storage for FHIR resources
    BundleDataSource: Data source backed by a FHIR Bundle
"""

from typing import TYPE_CHECKING, Any

from .types import CQLCode, CQLConcept, CQLInterval

if TYPE_CHECKING:
    from .context import CQLContext


class FHIRDataSource:
    """Abstract base class for FHIR data sources.

    Provides the interface for retrieving FHIR resources during CQL evaluation.
    Concrete implementations should override the retrieve and resolve_reference methods.
    """

    def retrieve(
        self,
        resource_type: str,
        context: "CQLContext | None" = None,
        code_path: str | None = None,
        codes: list[Any] | None = None,
        valueset: str | None = None,
        date_path: str | None = None,
        date_range: CQLInterval | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve resources of a given type with optional filters.

        Args:
            resource_type: FHIR resource type (e.g., "Patient", "Condition")
            context: CQL evaluation context (for patient-scoped retrieval)
            code_path: Path to the code element for filtering
            codes: List of codes to filter by
            valueset: ValueSet URL to filter by
            date_path: Path to the date element for filtering
            date_range: Date interval to filter by

        Returns:
            List of matching FHIR resources as dictionaries
        """
        raise NotImplementedError

    def resolve_reference(self, reference: str) -> dict[str, Any] | None:
        """Resolve a FHIR reference to a resource.

        Args:
            reference: FHIR reference string (e.g., "Patient/123")

        Returns:
            The referenced resource or None if not found
        """
        raise NotImplementedError

    def _get_nested_value(self, resource: dict[str, Any], path: str) -> Any:
        """Get a nested value from a resource using dot notation.

        Args:
            resource: FHIR resource dictionary
            path: Dot-separated path (e.g., "code.coding.0.code")

        Returns:
            The value at the path, or None if not found
        """
        parts = path.split(".")
        current: Any = resource

        for part in parts:
            if current is None:
                return None

            # Handle array index
            if part.isdigit():
                index = int(part)
                if isinstance(current, list) and index < len(current):
                    current = current[index]
                else:
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                # Return all values from array
                results = []
                for item in current:
                    if isinstance(item, dict):
                        val = item.get(part)
                        if val is not None:
                            if isinstance(val, list):
                                results.extend(val)
                            else:
                                results.append(val)
                return results if results else None
            else:
                return None

        return current

    def _matches_code(
        self,
        resource: dict[str, Any],
        code_path: str,
        codes: list[Any] | None = None,
        valueset_codes: list[CQLCode] | None = None,
    ) -> bool:
        """Check if a resource matches code criteria.

        Args:
            resource: FHIR resource to check
            code_path: Path to the code element
            codes: List of codes to match against
            valueset_codes: List of valueset codes to match against

        Returns:
            True if the resource matches the code criteria
        """
        code_value = self._get_nested_value(resource, code_path)
        if code_value is None:
            return False

        # Extract coding array from CodeableConcept
        codings = []
        if isinstance(code_value, dict):
            if "coding" in code_value:
                codings = code_value["coding"]
            elif "code" in code_value:
                # Already a Coding
                codings = [code_value]
        elif isinstance(code_value, list):
            # Could be array of CodeableConcepts or Codings
            for item in code_value:
                if isinstance(item, dict):
                    if "coding" in item:
                        codings.extend(item["coding"])
                    elif "code" in item:
                        codings.append(item)

        if not codings:
            return False

        # Check against provided codes
        if codes:
            for coding in codings:
                code = coding.get("code")
                system = coding.get("system")

                for match_code in codes:
                    if isinstance(match_code, CQLCode):
                        if match_code.code == code and match_code.system == system:
                            return True
                    elif isinstance(match_code, CQLConcept):
                        for concept_code in match_code.codes:
                            if concept_code.code == code and concept_code.system == system:
                                return True
                    elif isinstance(match_code, dict):
                        if match_code.get("code") == code:
                            if "system" not in match_code or match_code.get("system") == system:
                                return True
                    elif isinstance(match_code, str):
                        if match_code == code:
                            return True

        # Check against valueset codes
        if valueset_codes:
            for coding in codings:
                code = coding.get("code")
                system = coding.get("system")

                for vs_code in valueset_codes:
                    if vs_code.code == code and vs_code.system == system:
                        return True

        # If no codes specified, any coded value matches
        if not codes and not valueset_codes:
            return True

        return False

    def _matches_date_range(
        self,
        resource: dict[str, Any],
        date_path: str,
        date_range: CQLInterval,
    ) -> bool:
        """Check if a resource's date falls within a range.

        Args:
            resource: FHIR resource to check
            date_path: Path to the date element
            date_range: Date interval to check against

        Returns:
            True if the resource's date falls within the range
        """
        from ..types import FHIRDate, FHIRDateTime

        date_value = self._get_nested_value(resource, date_path)
        if date_value is None:
            return True  # No date to filter by

        # Parse date value
        if isinstance(date_value, str):
            if "T" in date_value:
                date_value = FHIRDateTime.parse(date_value)
            else:
                date_value = FHIRDate.parse(date_value)
        elif isinstance(date_value, dict):
            # Period type - check start and end
            start = date_value.get("start")
            end = date_value.get("end")
            if start:
                start = FHIRDateTime.parse(start) if "T" in start else FHIRDate.parse(start)
            if end:
                end = FHIRDateTime.parse(end) if "T" in end else FHIRDate.parse(end)

            # Check if period overlaps with date_range
            if start and date_range.high:
                if start > date_range.high:
                    return False
            if end and date_range.low:
                if end < date_range.low:
                    return False
            return True

        # Check if date is in range
        return date_value in date_range

    def _get_patient_reference(self, resource: dict[str, Any]) -> str | None:
        """Get the patient reference from a resource.

        Args:
            resource: FHIR resource

        Returns:
            Patient reference string or None
        """
        resource_type = resource.get("resourceType", "")

        # Map resource types to their patient reference paths
        patient_paths = {
            "Condition": ["subject.reference", "patient.reference"],
            "Observation": ["subject.reference", "patient.reference"],
            "MedicationRequest": ["subject.reference", "patient.reference"],
            "MedicationStatement": ["subject.reference", "patient.reference"],
            "Procedure": ["subject.reference", "patient.reference"],
            "Encounter": ["subject.reference", "patient.reference"],
            "DiagnosticReport": ["subject.reference", "patient.reference"],
            "CarePlan": ["subject.reference", "patient.reference"],
            "Goal": ["subject.reference", "patient.reference"],
            "AllergyIntolerance": ["patient.reference"],
            "Immunization": ["patient.reference"],
            "Device": ["patient.reference"],
            "Coverage": ["beneficiary.reference"],
            "Claim": ["patient.reference"],
            "ExplanationOfBenefit": ["patient.reference"],
        }

        paths = patient_paths.get(resource_type, ["subject.reference", "patient.reference"])

        for path in paths:
            ref = self._get_nested_value(resource, path)
            if ref:
                return ref

        return None


class InMemoryDataSource(FHIRDataSource):
    """In-memory FHIR data source.

    Stores FHIR resources in memory and provides retrieval with filtering.
    Useful for testing and scenarios where resources are already loaded.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory data source."""
        # Resources indexed by type: {"Patient": [resource1, resource2], ...}
        self._resources: dict[str, list[dict[str, Any]]] = {}
        # Resources indexed by id: {"Patient/123": resource, ...}
        self._by_id: dict[str, dict[str, Any]] = {}
        # Expanded valuesets: {"http://example.org/vs": [CQLCode, ...]}
        self._valuesets: dict[str, list[CQLCode]] = {}

    def add_resource(self, resource: dict[str, Any]) -> None:
        """Add a resource to the data source.

        Args:
            resource: FHIR resource to add
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            return

        if resource_type not in self._resources:
            self._resources[resource_type] = []

        self._resources[resource_type].append(resource)

        # Index by ID
        resource_id = resource.get("id")
        if resource_id:
            ref = f"{resource_type}/{resource_id}"
            self._by_id[ref] = resource

    def add_resources(self, resources: list[dict[str, Any]]) -> None:
        """Add multiple resources to the data source.

        Args:
            resources: List of FHIR resources to add
        """
        for resource in resources:
            self.add_resource(resource)

    def add_valueset(self, url: str, codes: list[CQLCode]) -> None:
        """Add an expanded valueset.

        Args:
            url: ValueSet URL
            codes: List of codes in the valueset
        """
        self._valuesets[url] = codes

    def get_valueset_codes(self, url: str) -> list[CQLCode] | None:
        """Get the codes in a valueset.

        Args:
            url: ValueSet URL

        Returns:
            List of codes or None if valueset not found
        """
        return self._valuesets.get(url)

    def clear(self) -> None:
        """Clear all resources from the data source."""
        self._resources.clear()
        self._by_id.clear()
        self._valuesets.clear()

    def retrieve(
        self,
        resource_type: str,
        context: "CQLContext | None" = None,
        code_path: str | None = None,
        codes: list[Any] | None = None,
        valueset: str | None = None,
        date_path: str | None = None,
        date_range: CQLInterval | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve resources with filtering.

        Args:
            resource_type: FHIR resource type
            context: CQL evaluation context
            code_path: Path to code element for filtering
            codes: Codes to filter by
            valueset: ValueSet URL to filter by
            date_path: Path to date element for filtering
            date_range: Date interval to filter by

        Returns:
            List of matching resources
        """
        # Handle resourceType in kwargs (from visitor)
        if "resourceType" in kwargs:
            resource_type = kwargs["resourceType"]
        if "codePath" in kwargs:
            code_path = kwargs["codePath"]
        if "code" in kwargs:
            codes = [kwargs["code"]] if kwargs["code"] else None

        # Get all resources of the type
        resources = self._resources.get(resource_type, [])

        # Apply context filtering (patient scope)
        if context and context.resource:
            patient_id = context.resource.get("id")
            if patient_id and resource_type != "Patient":
                patient_ref = f"Patient/{patient_id}"
                resources = [r for r in resources if self._get_patient_reference(r) == patient_ref]

        # Apply code filtering
        if code_path and (codes or valueset):
            valueset_codes = None
            if valueset:
                valueset_codes = self.get_valueset_codes(valueset)

            resources = [r for r in resources if self._matches_code(r, code_path, codes, valueset_codes)]

        # Apply date filtering
        if date_path and date_range:
            resources = [r for r in resources if self._matches_date_range(r, date_path, date_range)]

        return resources

    def resolve_reference(self, reference: str) -> dict[str, Any] | None:
        """Resolve a FHIR reference.

        Args:
            reference: FHIR reference string

        Returns:
            The referenced resource or None
        """
        return self._by_id.get(reference)


class BundleDataSource(FHIRDataSource):
    """Data source backed by a FHIR Bundle.

    Extracts resources from a FHIR Bundle and provides retrieval.
    """

    def __init__(self, bundle: dict[str, Any] | None = None) -> None:
        """Initialize with an optional bundle.

        Args:
            bundle: FHIR Bundle resource
        """
        self._in_memory = InMemoryDataSource()

        if bundle:
            self.load_bundle(bundle)

    def load_bundle(self, bundle: dict[str, Any]) -> None:
        """Load resources from a FHIR Bundle.

        Args:
            bundle: FHIR Bundle resource
        """
        if bundle.get("resourceType") != "Bundle":
            # Single resource
            self._in_memory.add_resource(bundle)
            return

        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource")
            if resource:
                self._in_memory.add_resource(resource)

    def add_valueset(self, url: str, codes: list[CQLCode]) -> None:
        """Add an expanded valueset.

        Args:
            url: ValueSet URL
            codes: List of codes in the valueset
        """
        self._in_memory.add_valueset(url, codes)

    def get_valueset_codes(self, url: str) -> list[CQLCode] | None:
        """Get the codes in a valueset.

        Args:
            url: ValueSet URL

        Returns:
            List of codes or None if valueset not found
        """
        return self._in_memory.get_valueset_codes(url)

    @property
    def resources(self) -> dict[str, list[dict[str, Any]]]:
        """Get all resources indexed by type."""
        return self._in_memory._resources

    def retrieve(
        self,
        resource_type: str,
        context: "CQLContext | None" = None,
        code_path: str | None = None,
        codes: list[Any] | None = None,
        valueset: str | None = None,
        date_path: str | None = None,
        date_range: CQLInterval | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve resources from the bundle.

        Args:
            resource_type: FHIR resource type
            context: CQL evaluation context
            code_path: Path to code element for filtering
            codes: Codes to filter by
            valueset: ValueSet URL to filter by
            date_path: Path to date element for filtering
            date_range: Date interval to filter by

        Returns:
            List of matching resources
        """
        return self._in_memory.retrieve(
            resource_type=resource_type,
            context=context,
            code_path=code_path,
            codes=codes,
            valueset=valueset,
            date_path=date_path,
            date_range=date_range,
            **kwargs,
        )

    def resolve_reference(self, reference: str) -> dict[str, Any] | None:
        """Resolve a FHIR reference.

        Args:
            reference: FHIR reference string

        Returns:
            The referenced resource or None
        """
        return self._in_memory.resolve_reference(reference)


class PatientBundleDataSource(BundleDataSource):
    """Data source for a patient-centric bundle.

    Automatically sets up patient context from the bundle.
    """

    def __init__(self, bundle: dict[str, Any] | None = None) -> None:
        """Initialize with an optional patient bundle.

        Args:
            bundle: FHIR Bundle containing patient and related resources
        """
        super().__init__(bundle)
        self._patient: dict[str, Any] | None = None

        if bundle:
            self._extract_patient()

    def _extract_patient(self) -> None:
        """Extract the patient resource from the loaded resources."""
        patients = self._in_memory._resources.get("Patient", [])
        if patients:
            self._patient = patients[0]

    @property
    def patient(self) -> dict[str, Any] | None:
        """Get the patient resource."""
        return self._patient

    def retrieve(
        self,
        resource_type: str,
        context: "CQLContext | None" = None,
        code_path: str | None = None,
        codes: list[Any] | None = None,
        valueset: str | None = None,
        date_path: str | None = None,
        date_range: CQLInterval | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve resources, filtered to the bundle's patient.

        Args:
            resource_type: FHIR resource type
            context: CQL evaluation context
            code_path: Path to code element for filtering
            codes: Codes to filter by
            valueset: ValueSet URL to filter by
            date_path: Path to date element for filtering
            date_range: Date interval to filter by

        Returns:
            List of matching resources for the patient
        """
        # Create a context with patient if not provided
        if context is None and self._patient:
            from .context import PatientContext

            context = PatientContext(resource=self._patient)

        return super().retrieve(
            resource_type=resource_type,
            context=context,
            code_path=code_path,
            codes=codes,
            valueset=valueset,
            date_path=date_path,
            date_range=date_range,
            **kwargs,
        )
