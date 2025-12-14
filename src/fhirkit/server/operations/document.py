"""Composition $document operation implementation.

Generates complete Document bundles from Composition resources.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from ..storage.fhir_store import FHIRStore


class DocumentGenerator:
    """Generator for Document bundles from Compositions.

    Implements the FHIR $document operation per:
    https://hl7.org/fhir/R4/composition-operation-document.html
    """

    def __init__(self, store: FHIRStore):
        """Initialize the document generator.

        Args:
            store: FHIR store containing resources
        """
        self.store = store

    def generate_document(
        self,
        composition: dict[str, Any],
        persist: bool = True,
    ) -> dict[str, Any]:
        """Generate a Document bundle from a Composition.

        Args:
            composition: The Composition resource to create a document from
            persist: Whether to persist the generated Bundle

        Returns:
            Document Bundle containing Composition and all referenced resources
        """
        # Track resources already added to avoid duplicates
        added_ids: set[str] = set()
        entries: list[dict[str, Any]] = []

        # Composition must be the first entry
        comp_id = composition.get("id", "")
        entries.append(self._create_entry(composition))
        added_ids.add(f"Composition/{comp_id}")

        # Resolve subject (Patient)
        subject_ref = composition.get("subject", {}).get("reference")
        if subject_ref:
            self._resolve_and_add(subject_ref, entries, added_ids)

        # Resolve encounter
        encounter_ref = composition.get("encounter", {}).get("reference")
        if encounter_ref:
            self._resolve_and_add(encounter_ref, entries, added_ids)

        # Resolve authors
        for author in composition.get("author", []):
            author_ref = author.get("reference")
            if author_ref:
                self._resolve_and_add(author_ref, entries, added_ids)

        # Resolve custodian
        custodian_ref = composition.get("custodian", {}).get("reference")
        if custodian_ref:
            self._resolve_and_add(custodian_ref, entries, added_ids)

        # Resolve attester references
        for attester in composition.get("attester", []):
            party_ref = attester.get("party", {}).get("reference")
            if party_ref:
                self._resolve_and_add(party_ref, entries, added_ids)

        # Resolve section entries
        for section in composition.get("section", []):
            self._resolve_section_entries(section, entries, added_ids)

        # Build the document bundle
        bundle = self._build_bundle(entries, composition)

        # Optionally persist the bundle
        if persist:
            self.store.create(bundle)

        return bundle

    def _resolve_and_add(
        self,
        reference: str,
        entries: list[dict[str, Any]],
        added_ids: set[str],
        depth: int = 0,
    ) -> None:
        """Resolve a reference and add to entries if not already present.

        Args:
            reference: FHIR reference string (e.g., "Patient/123")
            entries: List of bundle entries to add to
            added_ids: Set of already added resource IDs
            depth: Current recursion depth (to prevent infinite loops)
        """
        if reference in added_ids:
            return

        if depth > 10:  # Prevent infinite recursion
            return

        # Parse reference
        parts = reference.split("/")
        if len(parts) != 2:
            return

        resource_type, resource_id = parts

        # Read the resource
        resource = self.store.read(resource_type, resource_id)
        if resource is None:
            return

        # Add to entries
        entries.append(self._create_entry(resource))
        added_ids.add(reference)

        # Resolve nested references for certain resource types
        self._resolve_nested_references(resource, entries, added_ids, depth + 1)

    def _resolve_nested_references(
        self,
        resource: dict[str, Any],
        entries: list[dict[str, Any]],
        added_ids: set[str],
        depth: int,
    ) -> None:
        """Resolve nested references within a resource.

        Args:
            resource: The FHIR resource
            entries: List of bundle entries
            added_ids: Set of already added IDs
            depth: Current recursion depth
        """
        resource_type = resource.get("resourceType", "")

        # Handle specific resource types with important references
        if resource_type == "Encounter":
            # Resolve service provider
            provider_ref = resource.get("serviceProvider", {}).get("reference")
            if provider_ref:
                self._resolve_and_add(provider_ref, entries, added_ids, depth)

            # Resolve participants
            for participant in resource.get("participant", []):
                individual_ref = participant.get("individual", {}).get("reference")
                if individual_ref:
                    self._resolve_and_add(individual_ref, entries, added_ids, depth)

        elif resource_type == "Practitioner":
            # Practitioners don't typically have nested refs we need
            pass

        elif resource_type == "PractitionerRole":
            # Resolve practitioner and organization
            pract_ref = resource.get("practitioner", {}).get("reference")
            if pract_ref:
                self._resolve_and_add(pract_ref, entries, added_ids, depth)

            org_ref = resource.get("organization", {}).get("reference")
            if org_ref:
                self._resolve_and_add(org_ref, entries, added_ids, depth)

        elif resource_type == "Condition":
            # Resolve asserter
            asserter_ref = resource.get("asserter", {}).get("reference")
            if asserter_ref:
                self._resolve_and_add(asserter_ref, entries, added_ids, depth)

        elif resource_type == "MedicationRequest":
            # Resolve requester
            requester_ref = resource.get("requester", {}).get("reference")
            if requester_ref:
                self._resolve_and_add(requester_ref, entries, added_ids, depth)

            # Resolve medication reference if present
            med_ref = resource.get("medicationReference", {}).get("reference")
            if med_ref:
                self._resolve_and_add(med_ref, entries, added_ids, depth)

        elif resource_type == "Observation":
            # Resolve performer
            for performer in resource.get("performer", []):
                perf_ref = performer.get("reference")
                if perf_ref:
                    self._resolve_and_add(perf_ref, entries, added_ids, depth)

        elif resource_type == "Procedure":
            # Resolve performer actors
            for performer in resource.get("performer", []):
                actor_ref = performer.get("actor", {}).get("reference")
                if actor_ref:
                    self._resolve_and_add(actor_ref, entries, added_ids, depth)

    def _resolve_section_entries(
        self,
        section: dict[str, Any],
        entries: list[dict[str, Any]],
        added_ids: set[str],
    ) -> None:
        """Resolve all entries in a Composition section.

        Args:
            section: The section dictionary
            entries: List of bundle entries
            added_ids: Set of already added IDs
        """
        # Resolve section entries
        for entry in section.get("entry", []):
            entry_ref = entry.get("reference")
            if entry_ref:
                self._resolve_and_add(entry_ref, entries, added_ids)

        # Handle nested sections recursively
        for nested_section in section.get("section", []):
            self._resolve_section_entries(nested_section, entries, added_ids)

    def _create_entry(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Create a bundle entry for a resource.

        Args:
            resource: The FHIR resource

        Returns:
            Bundle entry dictionary
        """
        resource_id = resource.get("id", "")

        return {
            "fullUrl": f"urn:uuid:{resource_id}" if not resource_id.startswith("urn:") else resource_id,
            "resource": resource,
        }

    def _build_bundle(
        self,
        entries: list[dict[str, Any]],
        composition: dict[str, Any],
    ) -> dict[str, Any]:
        """Build the document Bundle.

        Args:
            entries: List of bundle entries
            composition: The original Composition resource

        Returns:
            Document Bundle resource
        """
        bundle_id = str(uuid.uuid4())

        bundle: dict[str, Any] = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
            },
            "identifier": {
                "system": "http://example.org/fhir/document",
                "value": f"DOC-{bundle_id[:8].upper()}",
            },
            "type": "document",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entry": entries,
        }

        return bundle

    def generate_document_from_id(
        self,
        composition_id: str,
        persist: bool = True,
    ) -> dict[str, Any] | None:
        """Generate a Document bundle from a Composition ID.

        Args:
            composition_id: The ID of the Composition resource
            persist: Whether to persist the generated Bundle

        Returns:
            Document Bundle, or None if Composition not found
        """
        composition = self.store.read("Composition", composition_id)

        if composition is None:
            return None

        return self.generate_document(composition, persist=persist)
