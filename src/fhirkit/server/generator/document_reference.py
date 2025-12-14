"""DocumentReference resource generator."""

import base64
from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    DOCUMENT_CATEGORIES,
    DOCUMENT_CONTENT_TYPES,
    DOCUMENT_SECURITY_LABELS,
    DOCUMENT_TYPES,
    LOINC_SYSTEM,
    CodingTemplate,
)


class DocumentReferenceGenerator(FHIRResourceGenerator):
    """Generator for FHIR DocumentReference resources.

    DocumentReference represents a reference to a document of any type,
    including clinical notes, reports, images, and other healthcare documents.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        document_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        custodian_ref: str | None = None,
        status: str | None = None,
        doc_status: str | None = None,
        date: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DocumentReference resource.

        Args:
            document_id: DocumentReference ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            author_ref: Author (Practitioner) reference
            custodian_ref: Custodian (Organization) reference
            status: Status (current, superseded, entered-in-error)
            doc_status: Document status (preliminary, final, amended)
            date: When document was created

        Returns:
            DocumentReference FHIR resource
        """
        if document_id is None:
            document_id = self._generate_id()

        # Status
        if status is None:
            status = self.faker.random_element(
                elements=["current"] * 90 + ["superseded"] * 8 + ["entered-in-error"] * 2
            )

        # Document status
        if doc_status is None:
            doc_status = self.faker.random_element(elements=["final"] * 80 + ["preliminary"] * 15 + ["amended"] * 5)

        # Select document type
        doc_type = self.faker.random_element(DOCUMENT_TYPES)

        # Category
        category = self.faker.random_element(DOCUMENT_CATEGORIES)

        # Content type
        content_type = self.faker.random_element(DOCUMENT_CONTENT_TYPES)

        # Security label
        security = self.faker.random_element(DOCUMENT_SECURITY_LABELS)

        # Date
        if date is None:
            date_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            date = date_dt.isoformat()

        # Generate document content
        content_data = self._generate_document_content(doc_type, content_type)

        document_reference: dict[str, Any] = {
            "resourceType": "DocumentReference",
            "id": document_id,
            "meta": self._generate_meta(),
            "status": status,
            "docStatus": doc_status,
            "type": {
                "coding": [
                    {
                        "system": LOINC_SYSTEM,
                        "code": doc_type["code"],
                        "display": doc_type["display"],
                    }
                ],
                "text": doc_type["display"],
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category",
                            "code": category["code"],
                            "display": category["display"],
                        }
                    ]
                }
            ],
            "date": date,
            "securityLabel": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                            "code": security["code"],
                            "display": security["display"],
                        }
                    ]
                }
            ],
            "content": [
                {
                    "attachment": {
                        "contentType": content_type,
                        "language": "en-US",
                        "data": content_data,
                        "title": f"{doc_type['display']} - {self.faker.date()}",
                        "creation": date,
                    }
                }
            ],
        }

        if patient_ref:
            document_reference["subject"] = {"reference": patient_ref}

        if encounter_ref:
            document_reference["context"] = {
                "encounter": [{"reference": encounter_ref}],
            }

        if author_ref:
            document_reference["author"] = [{"reference": author_ref}]

        if custodian_ref:
            document_reference["custodian"] = {"reference": custodian_ref}

        # Add description (70% chance)
        if self.faker.random.random() < 0.7:
            document_reference["description"] = self._generate_description(doc_type)

        return document_reference

    def _generate_document_content(self, doc_type: CodingTemplate, content_type: str) -> str:
        """Generate base64-encoded document content."""
        doc_display = doc_type.get("display", "Document")

        if content_type == "text/plain":
            content = f"""
{doc_display}
{"=" * len(doc_display)}

Date: {self.faker.date()}
Author: Dr. {self.faker.name()}

{self.faker.paragraph(nb_sentences=5)}

{self.faker.paragraph(nb_sentences=5)}

Assessment and Plan:
{self.faker.paragraph(nb_sentences=3)}

Signed electronically.
"""
        else:
            # For non-text types, generate placeholder
            content = f"[{doc_display} content - {content_type}]"

        return base64.b64encode(content.encode()).decode()

    def _generate_description(self, doc_type: CodingTemplate) -> str:
        """Generate a document description."""
        doc_display = doc_type.get("display", "Document")
        descriptions = [
            f"{doc_display} for patient encounter.",
            f"Clinical {doc_display.lower()} documenting patient care.",
            f"{doc_display} - see content for details.",
            f"Official {doc_display.lower()} signed by provider.",
        ]
        return self.faker.random_element(descriptions)

    def generate_clinical_note(
        self,
        patient_ref: str | None = None,
        author_ref: str | None = None,
    ) -> dict[str, Any]:
        """Generate a clinical note DocumentReference.

        Returns:
            DocumentReference for a clinical note
        """
        # Select a note type
        note_types = [t for t in DOCUMENT_TYPES if "note" in t.get("display", "").lower()]
        if note_types:
            doc_type = self.faker.random_element(note_types)
        else:
            doc_type = DOCUMENT_TYPES[0]

        doc = self.generate(
            patient_ref=patient_ref,
            author_ref=author_ref,
            status="current",
            doc_status="final",
        )
        # Override with specific type
        doc["type"] = {
            "coding": [
                {
                    "system": LOINC_SYSTEM,
                    "code": doc_type["code"],
                    "display": doc_type["display"],
                }
            ],
            "text": doc_type["display"],
        }
        return doc
