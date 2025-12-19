"""FHIR Server storage with CRUD operations.

Extends InMemoryDataSource with full CRUD operations, versioning, and search.
"""

import copy
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from fhirkit.engine.cql.datasource import InMemoryDataSource


class TransactionError(Exception):
    """Exception raised when a transaction operation fails."""

    def __init__(self, message: str, entry_index: int | None = None, original_error: Exception | None = None):
        self.message = message
        self.entry_index = entry_index
        self.original_error = original_error
        super().__init__(message)


class FHIRStore(InMemoryDataSource):
    """Extended in-memory FHIR store with CRUD operations and versioning."""

    def __init__(self) -> None:
        """Initialize the FHIR store."""
        super().__init__()
        # Version history: {"Patient/123": [v1, v2, ...]}
        self._version_history: dict[str, list[dict[str, Any]]] = {}
        # Deleted resources marker
        self._deleted: set[str] = set()
        # Transaction snapshot for rollback
        self._transaction_snapshot: dict[str, Any] | None = None

    def begin_transaction(self) -> None:
        """Begin a transaction by creating a snapshot of current state.

        This enables rollback if the transaction fails.
        """
        self._transaction_snapshot = {
            "resources": copy.deepcopy(self._resources),
            "by_id": copy.deepcopy(self._by_id),
            "version_history": copy.deepcopy(self._version_history),
            "deleted": copy.copy(self._deleted),
        }

    def commit_transaction(self) -> None:
        """Commit the current transaction.

        Clears the snapshot since changes are already applied.
        """
        self._transaction_snapshot = None

    def rollback_transaction(self) -> None:
        """Rollback to the state before the transaction began.

        Restores all data structures from the snapshot.
        """
        if self._transaction_snapshot is None:
            return  # No transaction to rollback

        self._resources = self._transaction_snapshot["resources"]
        self._by_id = self._transaction_snapshot["by_id"]
        self._version_history = self._transaction_snapshot["version_history"]
        self._deleted = self._transaction_snapshot["deleted"]
        self._transaction_snapshot = None

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for atomic transactions.

        Usage:
            with store.transaction():
                store.create(resource1)
                store.create(resource2)
                # If any operation fails, all changes are rolled back

        Raises:
            TransactionError: If any operation fails, rolls back and re-raises
        """
        self.begin_transaction()
        try:
            yield
            self.commit_transaction()
        except Exception as e:
            self.rollback_transaction()
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(str(e), original_error=e) from e

    def create(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Create a new resource.

        Args:
            resource: FHIR resource to create

        Returns:
            Created resource with assigned ID and meta
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource must have resourceType")

        # Assign ID if not present
        if "id" not in resource:
            resource["id"] = str(uuid.uuid4())

        resource_id = resource["id"]
        ref = f"{resource_type}/{resource_id}"

        # Check if already exists
        if ref in self._by_id and ref not in self._deleted:
            raise ValueError(f"Resource {ref} already exists")

        # Remove from deleted if re-creating
        self._deleted.discard(ref)

        # Set meta
        resource["meta"] = resource.get("meta", {})
        resource["meta"]["versionId"] = "1"
        resource["meta"]["lastUpdated"] = datetime.now(timezone.utc).isoformat()

        # Store resource
        self.add_resource(resource)

        # Initialize version history
        self._version_history[ref] = [resource.copy()]

        return resource

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        """Read a resource by type and ID.

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID

        Returns:
            Resource or None if not found/deleted
        """
        ref = f"{resource_type}/{resource_id}"

        if ref in self._deleted:
            return None

        return self._by_id.get(ref)

    def update(self, resource_type: str, resource_id: str, resource: dict[str, Any]) -> dict[str, Any]:
        """Update an existing resource.

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID
            resource: Updated resource

        Returns:
            Updated resource with new version
        """
        ref = f"{resource_type}/{resource_id}"

        # Check if exists
        existing = self._by_id.get(ref)
        if not existing or ref in self._deleted:
            # Create if doesn't exist (FHIR allows PUT to create)
            resource["id"] = resource_id
            resource["resourceType"] = resource_type
            return self.create(resource)

        # Ensure IDs match
        resource["id"] = resource_id
        resource["resourceType"] = resource_type

        # Increment version
        current_version = int(existing.get("meta", {}).get("versionId", "1"))
        resource["meta"] = resource.get("meta", {})
        resource["meta"]["versionId"] = str(current_version + 1)
        resource["meta"]["lastUpdated"] = datetime.now(timezone.utc).isoformat()

        # Update in storage
        self._by_id[ref] = resource

        # Update in type list
        if resource_type in self._resources:
            self._resources[resource_type] = [
                r if r.get("id") != resource_id else resource for r in self._resources[resource_type]
            ]

        # Add to version history
        if ref not in self._version_history:
            self._version_history[ref] = []
        self._version_history[ref].append(resource.copy())

        return resource

    def delete(self, resource_type: str, resource_id: str) -> bool:
        """Delete a resource (soft delete).

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID

        Returns:
            True if deleted, False if not found
        """
        ref = f"{resource_type}/{resource_id}"

        if ref not in self._by_id or ref in self._deleted:
            return False

        # Mark as deleted
        self._deleted.add(ref)

        return True

    def history(self, resource_type: str, resource_id: str) -> list[dict[str, Any]]:
        """Get version history for a resource.

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID

        Returns:
            List of resource versions (newest first)
        """
        ref = f"{resource_type}/{resource_id}"
        versions = self._version_history.get(ref, [])
        return list(reversed(versions))

    def search(
        self,
        resource_type: str,
        params: dict[str, str | list[str]],
        _count: int = 100,
        _offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search for resources with parameters.

        Args:
            resource_type: FHIR resource type
            params: Search parameters
            _count: Maximum results to return
            _offset: Results offset

        Returns:
            Tuple of (matching resources, total count)
        """
        # Get all resources of type
        resources = self._resources.get(resource_type, [])

        # Filter out deleted
        resources = [r for r in resources if f"{resource_type}/{r.get('id')}" not in self._deleted]

        # Apply search filters
        for param, value in params.items():
            # Skip special params except _id and _lastUpdated
            if param.startswith("_") and param not in ("_id", "_lastUpdated"):
                continue

            resources = self._filter_by_param(resources, resource_type, param, value)

        total = len(resources)

        # Apply pagination
        resources = resources[_offset : _offset + _count]

        return resources, total

    def _get_nested_value(self, resource: dict[str, Any], path: str) -> Any:
        """Get a nested value from a resource using dot notation.

        Args:
            resource: The resource dict
            path: Dot-separated path (e.g., "name.family")

        Returns:
            The value at the path, or None
        """
        parts = path.split(".")
        current: Any = resource

        for part in parts:
            if current is None:
                return None
            if isinstance(current, list):
                # For lists, collect values from all items
                values = []
                for item in current:
                    if isinstance(item, dict):
                        val = item.get(part)
                        if val is not None:
                            if isinstance(val, list):
                                values.extend(val)
                            else:
                                values.append(val)
                return values if values else None
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        return current

    def _filter_by_param(
        self,
        resources: list[dict[str, Any]],
        resource_type: str,
        param: str,
        value: str | list[str],
    ) -> list[dict[str, Any]]:
        """Filter resources by a search parameter.

        Args:
            resources: Resources to filter
            resource_type: FHIR resource type
            param: Search parameter name
            value: Search value(s)

        Returns:
            Filtered resources
        """
        # Build list of all search values (FHIR OR semantics)
        # Values can come from:
        # 1. Multiple params: ?_id=a&_id=b (value is list)
        # 2. Comma-separated: ?_id=a,b,c (value contains commas)
        search_values: list[str] = []
        if isinstance(value, list):
            for v in value:
                # Split each value by comma
                search_values.extend(v.split(","))
        else:
            # Single value, may contain commas
            search_values.extend(value.split(","))

        # Strip whitespace from values
        search_values = [v.strip() for v in search_values if v.strip()]

        if not search_values:
            return resources

        # Common search parameter mappings
        param_paths = self._get_search_param_paths(resource_type, param)
        if not param_paths:
            return resources  # Unknown param, return all

        result = []
        for resource in resources:
            for path in param_paths:
                resource_value = self._get_nested_value(resource, path)
                # Match if ANY of the search values match (OR semantics)
                if any(
                    self._matches_search_value(resource_value, sv, param)
                    for sv in search_values
                ):
                    result.append(resource)
                    break

        return result

    def _get_search_param_paths(self, resource_type: str, param: str) -> list[str]:
        """Get the resource paths for a search parameter.

        Args:
            resource_type: FHIR resource type
            param: Search parameter name

        Returns:
            List of paths to check
        """
        # Common parameters
        common_paths: dict[str, list[str]] = {
            "_id": ["id"],
            "identifier": ["identifier"],
        }

        # Resource-specific parameters
        resource_paths: dict[str, dict[str, list[str]]] = {
            "Patient": {
                "name": ["name"],
                "family": ["name.family"],
                "given": ["name.given"],
                "gender": ["gender"],
                "birthdate": ["birthDate"],
                "address": ["address"],
                "phone": ["telecom"],
                "email": ["telecom"],
            },
            "Condition": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "code": ["code.coding.code", "code.coding"],
                "clinical-status": ["clinicalStatus.coding.code"],
                "verification-status": ["verificationStatus.coding.code"],
                "onset-date": ["onsetDateTime"],
                "category": ["category.coding.code"],
            },
            "Observation": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "code": ["code.coding.code", "code.coding"],
                "date": ["effectiveDateTime", "effectivePeriod.start"],
                "category": ["category.coding.code"],
                "status": ["status"],
                "value-quantity": ["valueQuantity.value"],
            },
            "MedicationRequest": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "code": ["medicationCodeableConcept.coding.code"],
                "medication": ["medicationCodeableConcept.coding.code"],
                "status": ["status"],
                "authoredon": ["authoredOn"],
                "intent": ["intent"],
            },
            "Procedure": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "code": ["code.coding.code"],
                "date": ["performedDateTime", "performedPeriod.start"],
                "status": ["status"],
            },
            "Encounter": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "date": ["period.start"],
                "status": ["status"],
                "class": ["class.code"],
                "type": ["type.coding.code"],
            },
            "Practitioner": {
                "name": ["name"],
                "family": ["name.family"],
                "given": ["name.given"],
                "identifier": ["identifier.value"],
            },
            "Organization": {
                "name": ["name"],
                "identifier": ["identifier.value"],
                "type": ["type.coding.code"],
            },
            "ValueSet": {
                "url": ["url"],
                "name": ["name"],
                "status": ["status"],
            },
            "CodeSystem": {
                "url": ["url"],
                "name": ["name"],
                "status": ["status"],
            },
            "Library": {
                "url": ["url"],
                "name": ["name"],
                "version": ["version"],
                "status": ["status"],
            },
            "AllergyIntolerance": {
                "patient": ["patient.reference"],
                "code": ["code.coding.code", "code.coding"],
                "clinical-status": ["clinicalStatus.coding.code"],
                "criticality": ["criticality"],
            },
            "Immunization": {
                "patient": ["patient.reference"],
                "vaccine-code": ["vaccineCode.coding.code"],
                "status": ["status"],
                "date": ["occurrenceDateTime"],
            },
            "DiagnosticReport": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "code": ["code.coding.code"],
                "status": ["status"],
            },
            "CarePlan": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "status": ["status"],
            },
            "Goal": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "lifecycle-status": ["lifecycleStatus"],
            },
            "Coverage": {
                "patient": ["beneficiary.reference"],
                "beneficiary": ["beneficiary.reference"],
                "status": ["status"],
            },
            "Claim": {
                "patient": ["patient.reference"],
                "status": ["status"],
            },
            "ExplanationOfBenefit": {
                "patient": ["patient.reference"],
                "status": ["status"],
            },
            "Device": {
                "patient": ["patient.reference"],
                "status": ["status"],
            },
            "ServiceRequest": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "status": ["status"],
            },
            "DocumentReference": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "status": ["status"],
            },
            "CareTeam": {
                "patient": ["subject.reference"],
                "subject": ["subject.reference"],
                "status": ["status"],
            },
            "Task": {
                "patient": ["for.reference"],
                "subject": ["for.reference"],
                "status": ["status"],
            },
            "RelatedPerson": {
                "patient": ["patient.reference"],
            },
            "Appointment": {
                "patient": ["participant.actor.reference"],
                "status": ["status"],
            },
            "Medication": {
                "code": ["code.coding.code"],
                "status": ["status"],
            },
            "PractitionerRole": {
                "practitioner": ["practitioner.reference"],
                "organization": ["organization.reference"],
            },
            "Location": {
                "name": ["name"],
                "status": ["status"],
            },
            "Schedule": {
                "actor": ["actor.reference"],
            },
            "Slot": {
                "schedule": ["schedule.reference"],
                "status": ["status"],
            },
        }

        # Check common first
        if param in common_paths:
            return common_paths[param]

        # Check resource-specific
        if resource_type in resource_paths:
            if param in resource_paths[resource_type]:
                return resource_paths[resource_type][param]

        return []

    def _matches_search_value(self, resource_value: Any, search_value: str, param: str) -> bool:
        """Check if a resource value matches a search value.

        Args:
            resource_value: Value from resource
            search_value: Search value to match
            param: Parameter name (for special handling)

        Returns:
            True if matches
        """
        if resource_value is None:
            return False

        # Handle reference parameters (patient, subject)
        if param in ("patient", "subject"):
            if isinstance(resource_value, str):
                # Match "Patient/123" or just "123"
                if resource_value == search_value:
                    return True
                if resource_value.endswith(f"/{search_value}"):
                    return True
                if search_value.startswith("Patient/") and resource_value == search_value:
                    return True
            return False

        # Handle identifiers
        if param == "identifier":
            if isinstance(resource_value, list):
                for ident in resource_value:
                    if isinstance(ident, dict):
                        # Match system|value or just value
                        if "|" in search_value:
                            system, value = search_value.split("|", 1)
                            if system == "":
                                # Empty system (|value) - match any identifier with this value
                                if ident.get("value") == value:
                                    return True
                            elif ident.get("system") == system and ident.get("value") == value:
                                return True
                        elif ident.get("value") == search_value:
                            return True
            return False

        # Handle name search (HumanName)
        if param in ("name", "family", "given"):
            # For family/given, if we got a list of strings from nested path, match directly
            if isinstance(resource_value, list) and all(isinstance(v, str) for v in resource_value):
                return any(search_value.lower() in v.lower() for v in resource_value)
            return self._matches_name(resource_value, search_value, param)

        # Handle code/coding search
        if param in ("code", "medication"):
            return self._matches_code_search(resource_value, search_value)

        # Handle date search
        if param in ("date", "birthdate", "onset-date", "authoredon"):
            return self._matches_date_search(resource_value, search_value)

        # Simple string/value match - use exact match for token-like fields
        if isinstance(resource_value, str):
            # Exact match for short values (like codes, status, gender)
            if len(resource_value) < 50:
                return search_value.lower() == resource_value.lower()
            # Substring match for longer text fields
            return search_value.lower() in resource_value.lower()

        if isinstance(resource_value, (int, float, bool)):
            return str(resource_value).lower() == search_value.lower()

        if isinstance(resource_value, list):
            return any(self._matches_search_value(v, search_value, param) for v in resource_value)

        return False

    def _matches_name(self, name_value: Any, search_value: str, param: str) -> bool:
        """Match against HumanName.

        Args:
            name_value: Name value from resource
            search_value: Search value
            param: Parameter (name, family, given)

        Returns:
            True if matches
        """
        search_lower = search_value.lower()

        if isinstance(name_value, list):
            for name in name_value:
                if isinstance(name, dict):
                    if param == "family":
                        family = name.get("family", "")
                        if search_lower in family.lower():
                            return True
                    elif param == "given":
                        given = name.get("given", [])
                        if isinstance(given, list):
                            if any(search_lower in g.lower() for g in given):
                                return True
                    else:  # name - search all parts
                        family = name.get("family", "")
                        given = name.get("given", [])
                        text = name.get("text", "")

                        if search_lower in family.lower():
                            return True
                        if isinstance(given, list) and any(search_lower in g.lower() for g in given):
                            return True
                        if search_lower in text.lower():
                            return True

        return False

    def _matches_code_search(self, code_value: Any, search_value: str) -> bool:
        """Match against code/coding.

        Args:
            code_value: Code value from resource
            search_value: Search value (code or system|code)

        Returns:
            True if matches
        """
        # Parse search value
        system = None
        code = search_value
        if "|" in search_value:
            system, code = search_value.split("|", 1)

        # Handle different code structures
        if isinstance(code_value, str):
            return code_value == code

        if isinstance(code_value, dict):
            if "coding" in code_value:
                codings = code_value["coding"]
            else:
                codings = [code_value]

            for coding in codings:
                if isinstance(coding, dict):
                    if coding.get("code") == code:
                        if system is None or coding.get("system") == system:
                            return True

        if isinstance(code_value, list):
            return any(self._matches_code_search(v, search_value) for v in code_value)

        return False

    def _matches_date_search(self, date_value: Any, search_value: str) -> bool:
        """Match against date/datetime.

        Supports prefixes: eq, ne, lt, gt, le, ge, sa, eb

        Args:
            date_value: Date value from resource
            search_value: Search value with optional prefix

        Returns:
            True if matches
        """
        # Parse prefix
        prefix = "eq"
        if len(search_value) >= 2 and search_value[:2] in ("eq", "ne", "lt", "gt", "le", "ge", "sa", "eb"):
            prefix = search_value[:2]
            search_value = search_value[2:]

        if isinstance(date_value, str):
            # Simple string comparison (works for ISO dates)
            date_str = date_value[: len(search_value)]  # Compare at same precision

            if prefix == "eq":
                return date_str == search_value
            elif prefix == "ne":
                return date_str != search_value
            elif prefix == "lt":
                return date_str < search_value
            elif prefix == "gt":
                return date_str > search_value
            elif prefix == "le":
                return date_str <= search_value
            elif prefix == "ge":
                return date_str >= search_value
            elif prefix == "sa":  # starts after
                return date_str > search_value
            elif prefix == "eb":  # ends before
                return date_str < search_value

        return False

    def get_all_resources(self, resource_type: str | None = None) -> list[dict[str, Any]]:
        """Get all resources, optionally filtered by type.

        Args:
            resource_type: Optional resource type filter

        Returns:
            List of resources
        """
        if resource_type:
            resources = self._resources.get(resource_type, [])
            return [r for r in resources if f"{resource_type}/{r.get('id')}" not in self._deleted]

        all_resources = []
        for rtype, resources in self._resources.items():
            for r in resources:
                if f"{rtype}/{r.get('id')}" not in self._deleted:
                    all_resources.append(r)
        return all_resources

    def count(self, resource_type: str | None = None) -> int:
        """Count resources, optionally by type.

        Args:
            resource_type: Optional resource type filter

        Returns:
            Resource count
        """
        return len(self.get_all_resources(resource_type))
