"""Bundle resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class BundleGenerator(FHIRResourceGenerator):
    """Generator for FHIR Bundle resources."""

    # Bundle type codes
    BUNDLE_TYPES = [
        "document",
        "message",
        "transaction",
        "transaction-response",
        "batch",
        "batch-response",
        "history",
        "searchset",
        "collection",
    ]

    # HTTP methods for request entries
    HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        bundle_id: str | None = None,
        bundle_type: str = "collection",
        entries: list[dict[str, Any]] | None = None,
        total: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Bundle resource.

        Args:
            bundle_id: Resource ID (generates UUID if None)
            bundle_type: Type of bundle
            entries: List of entry resources
            total: Total count for searchset bundles

        Returns:
            Bundle FHIR resource
        """
        if bundle_id is None:
            bundle_id = self._generate_id()

        bundle: dict[str, Any] = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": self._generate_meta(),
            "type": bundle_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add total for searchset
        if bundle_type == "searchset":
            bundle["total"] = total if total is not None else len(entries or [])

        # Add entries
        if entries:
            bundle["entry"] = []
            for entry in entries:
                bundle_entry: dict[str, Any] = {}

                if isinstance(entry, dict) and "resourceType" in entry:
                    # It's a resource
                    resource_type = entry.get("resourceType")
                    resource_id = entry.get("id", self._generate_id())
                    bundle_entry["fullUrl"] = f"urn:uuid:{resource_id}"
                    bundle_entry["resource"] = entry

                    # Add request for transaction/batch
                    if bundle_type in ["transaction", "batch"]:
                        bundle_entry["request"] = {
                            "method": "POST",
                            "url": resource_type,
                        }

                    # Add response for transaction-response/batch-response
                    if bundle_type in ["transaction-response", "batch-response"]:
                        bundle_entry["response"] = {
                            "status": "201 Created",
                            "location": f"{resource_type}/{resource_id}/_history/1",
                            "etag": 'W/"1"',
                            "lastModified": datetime.now(timezone.utc).isoformat(),
                        }
                else:
                    # Already a bundle entry structure
                    bundle_entry = entry

                bundle["entry"].append(bundle_entry)

        # Add links for searchset
        if bundle_type == "searchset":
            bundle["link"] = [
                {
                    "relation": "self",
                    "url": f"http://example.org/fhir?_id={bundle_id}",
                }
            ]

        return bundle

    def generate_searchset(
        self,
        resources: list[dict[str, Any]],
        total: int | None = None,
        self_link: str | None = None,
        next_link: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a searchset Bundle.

        Args:
            resources: List of resources to include
            total: Total matching resources
            self_link: Self link URL
            next_link: Next page link URL

        Returns:
            Bundle FHIR resource
        """
        bundle = self.generate(
            bundle_type="searchset",
            entries=resources,
            total=total,
            **kwargs,
        )

        # Update links
        if self_link or next_link:
            bundle["link"] = []
            if self_link:
                bundle["link"].append({"relation": "self", "url": self_link})
            if next_link:
                bundle["link"].append({"relation": "next", "url": next_link})

        return bundle

    def generate_transaction(
        self,
        resources: list[dict[str, Any]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a transaction Bundle.

        Args:
            resources: List of resources to include

        Returns:
            Bundle FHIR resource
        """
        return self.generate(
            bundle_type="transaction",
            entries=resources,
            **kwargs,
        )

    def generate_document(
        self,
        composition: dict[str, Any],
        resources: list[dict[str, Any]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a document Bundle.

        Args:
            composition: The Composition resource (first entry)
            resources: Additional resources

        Returns:
            Bundle FHIR resource
        """
        entries = [composition] + resources
        return self.generate(
            bundle_type="document",
            entries=entries,
            **kwargs,
        )

    def generate_message(
        self,
        message_header: dict[str, Any],
        resources: list[dict[str, Any]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a message Bundle.

        Args:
            message_header: The MessageHeader resource (first entry)
            resources: Additional resources

        Returns:
            Bundle FHIR resource
        """
        entries = [message_header] + resources
        return self.generate(
            bundle_type="message",
            entries=entries,
            **kwargs,
        )
