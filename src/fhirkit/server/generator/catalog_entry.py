"""CatalogEntry resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CatalogEntryGenerator(FHIRResourceGenerator):
    """Generator for FHIR CatalogEntry resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    ENTRY_TYPES = [
        "ActivityDefinition",
        "PlanDefinition",
        "SpecimenDefinition",
        "ObservationDefinition",
        "DeviceDefinition",
        "Organization",
        "Practitioner",
        "PractitionerRole",
        "HealthcareService",
        "MedicationKnowledge",
        "Medication",
        "Substance",
        "Location",
    ]

    RELATION_TYPES = [
        {
            "system": "http://hl7.org/fhir/relation-type",
            "code": "triggers",
            "display": "Triggers",
        },
        {
            "system": "http://hl7.org/fhir/relation-type",
            "code": "is-replaced-by",
            "display": "Is Replaced By",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        entry_id: str | None = None,
        orderable: bool = True,
        referenced_item_reference: str | None = None,
        additional_identifier: list[dict[str, Any]] | None = None,
        classification: list[dict[str, Any]] | None = None,
        status: str = "active",
        validity_period_start: str | None = None,
        validity_period_end: str | None = None,
        valid_to: str | None = None,
        last_updated: str | None = None,
        related_entry: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CatalogEntry resource.

        Args:
            entry_id: Resource ID (generates UUID if None)
            orderable: Whether the item is orderable
            referenced_item_reference: Reference to the cataloged item
            additional_identifier: Additional identifiers
            classification: Classification of the entry
            status: Entry status
            validity_period_start: Start of validity period
            validity_period_end: End of validity period
            valid_to: Validity end date
            last_updated: Last update time
            related_entry: Related entries

        Returns:
            CatalogEntry FHIR resource
        """
        if entry_id is None:
            entry_id = self._generate_id()

        catalog_entry: dict[str, Any] = {
            "resourceType": "CatalogEntry",
            "id": entry_id,
            "meta": self._generate_meta(),
            "orderable": orderable,
            "status": status,
        }

        # Add identifier
        catalog_entry["identifier"] = [
            {
                "system": "http://example.org/catalog-entries",
                "value": f"CAT-{self.faker.random_number(digits=8, fix_len=True)}",
            }
        ]

        # Add additional identifiers
        if additional_identifier:
            catalog_entry["additionalIdentifier"] = additional_identifier

        # Add referenced item
        if referenced_item_reference:
            catalog_entry["referencedItem"] = {"reference": referenced_item_reference}
        else:
            item_type = self.faker.random_element(self.ENTRY_TYPES)
            catalog_entry["referencedItem"] = {"reference": f"{item_type}/{self._generate_id()}"}

        # Add classification
        if classification:
            catalog_entry["classification"] = classification
        elif self.faker.boolean(chance_of_getting_true=60):
            catalog_entry["classification"] = [
                {
                    "coding": [
                        {
                            "system": "http://example.org/catalog-classification",
                            "code": self.faker.random_element(["diagnostic", "therapeutic", "preventive"]),
                        }
                    ]
                }
            ]

        # Add validity period
        if validity_period_start or validity_period_end:
            catalog_entry["validityPeriod"] = {}
            if validity_period_start:
                catalog_entry["validityPeriod"]["start"] = validity_period_start
            if validity_period_end:
                catalog_entry["validityPeriod"]["end"] = validity_period_end
        else:
            start = datetime.now(timezone.utc)
            end = start + timedelta(days=365)
            catalog_entry["validityPeriod"] = {
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            }

        # Add valid to
        if valid_to:
            catalog_entry["validTo"] = valid_to

        # Add last updated
        if last_updated:
            catalog_entry["lastUpdated"] = last_updated
        else:
            catalog_entry["lastUpdated"] = datetime.now(timezone.utc).isoformat()

        # Add related entries
        if related_entry:
            catalog_entry["relatedEntry"] = related_entry

        return catalog_entry

    def generate_for_medication(
        self,
        medication_id: str,
        orderable: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CatalogEntry for a medication.

        Args:
            medication_id: Medication ID
            orderable: Whether it can be ordered

        Returns:
            CatalogEntry FHIR resource
        """
        return self.generate(
            referenced_item_reference=f"Medication/{medication_id}",
            orderable=orderable,
            classification=[
                {
                    "coding": [
                        {
                            "system": "http://example.org/catalog-classification",
                            "code": "therapeutic",
                            "display": "Therapeutic",
                        }
                    ]
                }
            ],
            **kwargs,
        )
