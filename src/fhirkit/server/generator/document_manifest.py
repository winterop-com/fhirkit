"""DocumentManifest resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class DocumentManifestGenerator(FHIRResourceGenerator):
    """Generator for FHIR DocumentManifest resources."""

    MANIFEST_TYPES = [
        {
            "system": "http://snomed.info/sct",
            "code": "419891008",
            "display": "Record artifact",
        },
        {
            "system": "http://loinc.org",
            "code": "11503-0",
            "display": "Medical records",
        },
        {
            "system": "http://loinc.org",
            "code": "34117-2",
            "display": "History and physical note",
        },
        {
            "system": "http://loinc.org",
            "code": "18842-5",
            "display": "Discharge summary",
        },
    ]

    STATUS_CODES = ["current", "superseded", "entered-in-error"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        manifest_id: str | None = None,
        status: str | None = None,
        manifest_type: dict[str, Any] | None = None,
        subject_reference: str | None = None,
        created: str | None = None,
        author_references: list[str] | None = None,
        recipient_references: list[str] | None = None,
        source: str | None = None,
        description: str | None = None,
        content_references: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DocumentManifest resource.

        Args:
            manifest_id: Resource ID (generates UUID if None)
            status: Manifest status
            manifest_type: Type of manifest
            subject_reference: Reference to Patient or other subject
            created: Creation date
            author_references: References to authors
            recipient_references: References to recipients
            source: Source of the manifest
            description: Human readable description
            content_references: References to content documents

        Returns:
            DocumentManifest FHIR resource
        """
        if manifest_id is None:
            manifest_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:1])

        if manifest_type is None:
            manifest_type = self.faker.random_element(self.MANIFEST_TYPES)

        if created is None:
            created = datetime.now().isoformat()

        manifest: dict[str, Any] = {
            "resourceType": "DocumentManifest",
            "id": manifest_id,
            "status": status,
            "type": {
                "coding": [manifest_type],
                "text": manifest_type["display"],
            },
            "created": created,
        }

        # Add master identifier
        manifest["masterIdentifier"] = {
            "system": "http://example.org/document-manifest-ids",
            "value": f"DM-{self.faker.random_number(digits=10, fix_len=True)}",
        }

        # Add subject reference
        if subject_reference:
            manifest["subject"] = {"reference": subject_reference}
        else:
            manifest["subject"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add author references
        if author_references:
            manifest["author"] = [{"reference": ref} for ref in author_references]
        elif self.faker.boolean(chance_of_getting_true=70):
            manifest["author"] = [{"reference": f"Practitioner/{self._generate_id()}"}]

        # Add recipient references
        if recipient_references:
            manifest["recipient"] = [{"reference": ref} for ref in recipient_references]

        # Add source
        if source:
            manifest["source"] = source
        else:
            manifest["source"] = f"urn:oid:1.3.6.1.4.1.21367.2009.1.2.{self.faker.random_int(1, 999)}"

        # Add description
        if description:
            manifest["description"] = description
        else:
            manifest["description"] = f"Document manifest: {manifest_type['display']}"

        # Add content references
        if content_references:
            manifest["content"] = [{"reference": ref} for ref in content_references]
        else:
            # Generate some placeholder document references
            num_docs = self.faker.random_int(1, 3)
            manifest["content"] = [{"reference": f"DocumentReference/{self._generate_id()}"} for _ in range(num_docs)]

        return manifest

    def generate_for_patient(
        self,
        patient_id: str,
        document_references: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DocumentManifest for a specific patient.

        Args:
            patient_id: Patient ID
            document_references: List of DocumentReference IDs

        Returns:
            DocumentManifest FHIR resource
        """
        content_refs = None
        if document_references:
            content_refs = [f"DocumentReference/{doc_id}" for doc_id in document_references]

        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            content_references=content_refs,
            **kwargs,
        )
