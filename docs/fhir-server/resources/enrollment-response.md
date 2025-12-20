# EnrollmentResponse

## Overview

An EnrollmentResponse represents an insurer's response to an enrollment request. It indicates whether the enrollment was accepted, the effective dates of coverage, and any relevant disposition information.

This resource completes the enrollment workflow by communicating the outcome of the enrollment request.

**Common use cases:**
- Enrollment confirmations
- Enrollment denials
- Coverage activation notices
- Enrollment status updates

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/enrollmentresponse.html](https://hl7.org/fhir/R4/enrollmentresponse.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `request` | Reference(EnrollmentRequest) | Original request |
| `outcome` | code | queued, complete, error, partial |
| `disposition` | string | Disposition message |
| `created` | dateTime | Creation date |
| `organization` | Reference(Organization) | Responding organization |
| `requestProvider` | Reference(Practitioner|Organization) | Requesting provider |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=response-001` |
| `identifier` | token | Business identifier | `identifier=RESP-12345` |
| `status` | token | Response status | `status=active` |
| `request` | reference | Original request | `request=EnrollmentRequest/req-001` |

## Examples

### Create an EnrollmentResponse

```bash
curl -X POST http://localhost:8080/baseR4/EnrollmentResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "EnrollmentResponse",
    "identifier": [{
      "system": "http://insurer.example.org/responses",
      "value": "RESP-2024-001"
    }],
    "status": "active",
    "request": {"reference": "EnrollmentRequest/req-001"},
    "outcome": "complete",
    "disposition": "Enrollment approved. Coverage effective 2024-02-01.",
    "created": "2024-01-16T14:00:00Z",
    "organization": {"reference": "Organization/insurer-001"}
  }'
```

### Search EnrollmentResponses

```bash
# By status
curl "http://localhost:8080/baseR4/EnrollmentResponse?status=active"

# By request
curl "http://localhost:8080/baseR4/EnrollmentResponse?request=EnrollmentRequest/req-001"
```

## Generator Usage

```python
from fhirkit.server.generator import EnrollmentResponseGenerator

generator = EnrollmentResponseGenerator(seed=42)

# Generate a random enrollment response
response = generator.generate()

# Generate approved response
approved = generator.generate(
    outcome="complete",
    disposition="Enrollment approved"
)

# Generate batch
responses = generator.generate_batch(count=10)
```

## Outcome Codes

| Code | Description |
|------|-------------|
| queued | Response is queued |
| complete | Processing complete |
| error | Error in processing |
| partial | Partial processing |

## Related Resources

- [EnrollmentRequest](./enrollment-request.md) - The original request
- [Coverage](./coverage.md) - Resulting coverage
- [Patient](./patient.md) - Enrolled patient
