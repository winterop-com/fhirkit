# DocumentReference

## Overview

The DocumentReference resource represents a reference to a document of any kind. It provides metadata about the document and a pointer to its content. This includes clinical notes, reports, images, and other healthcare-related documents.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/documentreference.html](https://hl7.org/fhir/R4/documentreference.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | current, superseded, entered-in-error |
| `docStatus` | code | preliminary, final, amended, entered-in-error |
| `type` | CodeableConcept | Kind of document (LOINC code) |
| `category` | CodeableConcept[] | Categorization of document |
| `subject` | Reference(Patient) | Who the document is about |
| `date` | instant | When the document was created |
| `author` | Reference(Practitioner)[] | Who authored the document |
| `custodian` | Reference(Organization) | Organization maintaining document |
| `content` | BackboneElement[] | Document content with attachment |
| `context` | BackboneElement | Clinical context including encounter |
| `securityLabel` | CodeableConcept[] | Document security labels |
| `description` | string | Human-readable description |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `type` | token | Document type | `type=http://loinc.org\|34117-2` |
| `category` | token | Category | `category=clinical-note` |
| `status` | token | Status | `status=current` |
| `date` | date | Creation date | `date=ge2024-01-01` |
| `author` | reference | Author reference | `author=Practitioner/456` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/789` |
| `custodian` | reference | Custodian reference | `custodian=Organization/org-1` |

## Examples

### Create a DocumentReference

```bash
curl -X POST http://localhost:8080/baseR4/DocumentReference \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "DocumentReference",
    "status": "current",
    "docStatus": "final",
    "type": {
      "coding": [{
        "system": "http://loinc.org",
        "code": "34117-2",
        "display": "History and physical note"
      }],
      "text": "History and physical note"
    },
    "category": [{
      "coding": [{
        "system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category",
        "code": "clinical-note",
        "display": "Clinical Note"
      }]
    }],
    "subject": {"reference": "Patient/patient-001"},
    "date": "2024-06-15T10:30:00Z",
    "author": [{"reference": "Practitioner/practitioner-001"}],
    "content": [{
      "attachment": {
        "contentType": "text/plain",
        "language": "en-US",
        "title": "History and Physical",
        "creation": "2024-06-15T10:30:00Z"
      }
    }]
  }'
```

### Search DocumentReferences

```bash
# By patient
curl "http://localhost:8080/baseR4/DocumentReference?patient=Patient/123"

# By type (H&P notes)
curl "http://localhost:8080/baseR4/DocumentReference?type=http://loinc.org|34117-2"

# Current documents only
curl "http://localhost:8080/baseR4/DocumentReference?status=current"

# By date range
curl "http://localhost:8080/baseR4/DocumentReference?date=ge2024-01-01"

# Combined
curl "http://localhost:8080/baseR4/DocumentReference?patient=Patient/123&category=clinical-note&status=current"
```

## Generator

The `DocumentReferenceGenerator` creates synthetic DocumentReference resources with:

- LOINC document type codes
- US Core category codes
- Base64-encoded sample content
- Confidentiality security labels

### Usage

```python
from fhirkit.server.generator import DocumentReferenceGenerator

generator = DocumentReferenceGenerator(seed=42)

doc = generator.generate(
    patient_ref="Patient/123",
    author_ref="Practitioner/456",
    custodian_ref="Organization/org-1"
)

# Generate clinical note specifically
note = generator.generate_clinical_note(
    patient_ref="Patient/123",
    author_ref="Practitioner/456"
)
```

## Clinical Codes

### Document Types (LOINC)

| Code | Display |
|------|---------|
| 34117-2 | History and physical note |
| 11488-4 | Consultation note |
| 18842-5 | Discharge summary |
| 11506-3 | Progress note |
| 28570-0 | Procedure note |
| 11502-2 | Laboratory report |
| 18748-4 | Diagnostic imaging report |
| 34111-5 | Emergency department note |

### Security Labels

| Code | Display |
|------|---------|
| N | Normal |
| R | Restricted |
| V | Very Restricted |
