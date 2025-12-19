# $document Operation

## Overview

The `$document` operation generates a complete Document Bundle from a Composition resource. It resolves all referenced resources and packages them together into a self-contained clinical document.

**FHIR Specification**: https://hl7.org/fhir/R4/composition-operation-document.html

## Endpoint

```
GET /Composition/{composition_id}/$document
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `persist` | boolean | true | Whether to save the generated Bundle to the store |

## Response

Returns a Document Bundle containing:

1. The Composition resource (always first entry)
2. All referenced resources (Patient, Practitioner, Conditions, etc.)
3. Nested references resolved up to 10 levels deep

```json
{
  "resourceType": "Bundle",
  "id": "doc-abc123",
  "type": "document",
  "timestamp": "2024-01-15T10:30:00Z",
  "identifier": {
    "system": "http://example.org/fhir/document",
    "value": "DOC-ABC12345"
  },
  "entry": [
    {
      "fullUrl": "urn:uuid:composition-001",
      "resource": {
        "resourceType": "Composition",
        "id": "composition-001",
        "status": "final",
        "type": {"coding": [{"code": "11488-4", "display": "Consultation note"}]},
        "subject": {"reference": "Patient/patient-001"},
        "author": [{"reference": "Practitioner/doctor-001"}],
        "section": [...]
      }
    },
    {
      "fullUrl": "urn:uuid:patient-001",
      "resource": {
        "resourceType": "Patient",
        "id": "patient-001",
        "name": [{"family": "Smith", "given": ["John"]}]
      }
    }
  ]
}
```

## Reference Resolution

The operation automatically resolves:

| Composition Field | Resolved Reference |
|-------------------|-------------------|
| `subject` | Patient |
| `encounter` | Encounter |
| `author` | Practitioner, PractitionerRole, Organization |
| `custodian` | Organization |
| `attester.party` | Practitioner, Organization |
| `section.entry` | Any referenced resources |

### Nested References

For resolved resources, additional references are also resolved:

- **Encounter**: serviceProvider, participants
- **PractitionerRole**: practitioner, organization
- **Condition**: asserter
- **MedicationRequest**: requester, medicationReference
- **Observation**: performer
- **Procedure**: performer.actor

## Example

### Create a Composition

```bash
curl -X PUT http://localhost:8080/baseR4/Composition/consultation-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Composition",
    "id": "consultation-001",
    "status": "final",
    "type": {
      "coding": [{"system": "http://loinc.org", "code": "11488-4", "display": "Consultation note"}]
    },
    "subject": {"reference": "Patient/patient-001"},
    "date": "2024-01-15",
    "author": [{"reference": "Practitioner/doctor-001"}],
    "title": "Consultation Note",
    "section": [
      {
        "title": "Chief Complaint",
        "code": {"coding": [{"code": "10154-3", "display": "Chief complaint"}]},
        "entry": [{"reference": "Condition/condition-001"}]
      }
    ]
  }'
```

### Generate Document

```bash
curl http://localhost:8080/baseR4/Composition/consultation-001/\$document
```

## Use Cases

1. **Clinical Documents**: Generate discharge summaries, consultation notes
2. **Document Exchange**: Create portable clinical documents for sharing
3. **Legal Records**: Package complete clinical encounters
4. **Archival**: Create self-contained snapshots of clinical data

## Notes

- Maximum recursion depth is 10 levels (prevents infinite loops)
- Duplicate resources are not added multiple times
- The Composition is always the first entry in the Bundle
- Generated Bundle has type "document"
- A unique identifier is automatically assigned
