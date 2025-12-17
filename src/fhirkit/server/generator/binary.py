"""Binary resource generator."""

import base64
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator

# Sample content types for Binary resources
BINARY_CONTENT_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
    "text/xml",
    "application/json",
    "application/xml",
    "text/csv",
    "application/hl7-v2",
    "application/fhir+json",
]


class BinaryGenerator(FHIRResourceGenerator):
    """Generator for FHIR Binary resources.

    Binary is a special resource for raw binary data (PDFs, images, etc.)
    that doesn't fit the standard FHIR resource structure.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        binary_id: str | None = None,
        content_type: str | None = None,
        data: bytes | str | None = None,
        security_context_ref: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Binary resource.

        Args:
            binary_id: Binary ID (generates UUID if None)
            content_type: MIME type of the content
            data: Raw binary data (bytes) or base64 string
            security_context_ref: Reference for security context (e.g., "DocumentReference/123")

        Returns:
            Binary FHIR resource
        """
        if binary_id is None:
            binary_id = self._generate_id()

        if content_type is None:
            content_type = self.faker.random_element(BINARY_CONTENT_TYPES)

        # Generate sample data if not provided
        if data is None:
            # Generate placeholder content based on content type
            if content_type == "text/plain":
                sample_text = self.faker.paragraph(nb_sentences=3)
                data = sample_text.encode("utf-8")
            elif content_type in ("application/json", "application/fhir+json"):
                sample_json = f'{{"generated": true, "timestamp": "{self.faker.iso8601()}"}}'
                data = sample_json.encode("utf-8")
            elif content_type == "text/xml":
                sample_xml = '<?xml version="1.0"?><root><generated>true</generated></root>'
                data = sample_xml.encode("utf-8")
            elif content_type == "text/csv":
                sample_csv = "id,name,value\n1,test,100"
                data = sample_csv.encode("utf-8")
            else:
                # Binary placeholder (small sample)
                data = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"

        # Encode data to base64 if bytes
        if isinstance(data, bytes):
            data_b64 = base64.b64encode(data).decode("utf-8")
        else:
            data_b64 = data

        resource: dict[str, Any] = {
            "resourceType": "Binary",
            "id": binary_id,
            "contentType": content_type,
            "data": data_b64,
        }

        # Add security context if provided
        if security_context_ref:
            resource["securityContext"] = {"reference": security_context_ref}

        # Add metadata
        resource["meta"] = self._generate_meta()

        return resource
