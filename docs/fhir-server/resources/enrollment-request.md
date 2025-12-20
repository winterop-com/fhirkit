# EnrollmentRequest

## Overview

An EnrollmentRequest represents a request to enroll a patient in an insurance plan or other benefit program. It is used to initiate the enrollment process with an insurer or benefits administrator.

This resource supports the workflow of adding patients to insurance coverage or benefit programs.

**Common use cases:**
- Insurance enrollment
- Benefits program enrollment
- Open enrollment requests
- Coverage activation requests

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/enrollmentrequest.html](https://hl7.org/fhir/R4/enrollmentrequest.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `created` | dateTime | Creation date |
| `insurer` | Reference(Organization) | Target insurer |
| `provider` | Reference(Practitioner|Organization) | Requesting provider |
| `candidate` | Reference(Patient) | Patient to be enrolled |
| `coverage` | Reference(Coverage) | Coverage to enroll in |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=request-001` |
| `identifier` | token | Business identifier | `identifier=ENR-12345` |
| `status` | token | Request status | `status=active` |
| `subject` | reference | Patient reference | `subject=Patient/123` |
| `patient` | reference | Patient reference (alias) | `patient=Patient/123` |

## Examples

### Create an EnrollmentRequest

```bash
curl -X POST http://localhost:8080/baseR4/EnrollmentRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "EnrollmentRequest",
    "identifier": [{
      "system": "http://provider.example.org/enrollments",
      "value": "ENR-2024-001"
    }],
    "status": "active",
    "created": "2024-01-15T10:00:00Z",
    "insurer": {"reference": "Organization/insurer-001"},
    "provider": {"reference": "Organization/provider-001"},
    "candidate": {"reference": "Patient/123"},
    "coverage": {"reference": "Coverage/cov-001"}
  }'
```

### Search EnrollmentRequests

```bash
# By patient
curl "http://localhost:8080/baseR4/EnrollmentRequest?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/EnrollmentRequest?status=active"
```

## Generator Usage

```python
from fhirkit.server.generator import EnrollmentRequestGenerator

generator = EnrollmentRequestGenerator(seed=42)

# Generate a random enrollment request
request = generator.generate()

# Generate for specific patient
patient_request = generator.generate(
    candidate_reference="Patient/123",
    status="active"
)

# Generate batch
requests = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| active | Request is active |
| cancelled | Request was cancelled |
| draft | Request is a draft |
| entered-in-error | Entered in error |

## Related Resources

- [EnrollmentResponse](./enrollment-response.md) - Response to this request
- [Coverage](./coverage.md) - Coverage being enrolled in
- [Patient](./patient.md) - Patient being enrolled
- [InsurancePlan](./insurance-plan.md) - Plan being enrolled in
