# CoverageEligibilityRequest

## Overview

A CoverageEligibilityRequest represents a request to an insurer to verify a patient's insurance coverage and eligibility for specific services. It is used to determine what benefits are available before providing care.

This resource supports pre-service eligibility checks, helping providers understand coverage details, co-pays, deductibles, and authorization requirements before delivering services.

**Common use cases:**
- Pre-service eligibility verification
- Benefit coverage inquiries
- Authorization requirements check
- Cost estimation
- Prior authorization requests

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/coverageeligibilityrequest.html](https://hl7.org/fhir/R4/coverageeligibilityrequest.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `purpose` | code[] | auth-requirements, benefits, discovery, validation |
| `patient` | Reference(Patient) | Patient for the request |
| `created` | dateTime | Request creation date |
| `provider` | Reference(Practitioner|Organization) | Requesting provider |
| `insurer` | Reference(Organization) | Target insurer |
| `facility` | Reference(Location) | Service facility |
| `item` | BackboneElement[] | Items being queried |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=request-001` |
| `identifier` | token | Business identifier | `identifier=ELIG-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Request status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `provider` | reference | Provider reference | `provider=Practitioner/456` |
| `insurer` | reference | Insurer reference | `insurer=Organization/payer-001` |
| `facility` | reference | Facility reference | `facility=Location/loc-001` |

## Examples

### Create a CoverageEligibilityRequest

```bash
curl -X POST http://localhost:8080/baseR4/CoverageEligibilityRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CoverageEligibilityRequest",
    "identifier": [{
      "system": "http://hospital.example.org/eligibility-requests",
      "value": "ELIG-2024-001"
    }],
    "status": "active",
    "purpose": ["benefits"],
    "patient": {"reference": "Patient/123"},
    "created": "2024-01-15T10:00:00Z",
    "provider": {"reference": "Practitioner/456"},
    "insurer": {"reference": "Organization/payer-001"}
  }'
```

### Search CoverageEligibilityRequests

```bash
# By patient
curl "http://localhost:8080/baseR4/CoverageEligibilityRequest?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/CoverageEligibilityRequest?status=active"

# By insurer
curl "http://localhost:8080/baseR4/CoverageEligibilityRequest?insurer=Organization/payer-001"
```

## Generator Usage

```python
from fhirkit.server.generator import CoverageEligibilityRequestGenerator

generator = CoverageEligibilityRequestGenerator(seed=42)

# Generate a random request
request = generator.generate()

# Generate for specific patient
patient_request = generator.generate(
    patient_reference="Patient/123",
    status="active"
)

# Generate batch
requests = generator.generate_batch(count=10)
```

## Purpose Codes

| Code | Description |
|------|-------------|
| auth-requirements | Authorization requirements |
| benefits | Coverage benefits |
| discovery | Coverage discovery |
| validation | Coverage validation |

## Related Resources

- [CoverageEligibilityResponse](./coverage-eligibility-response.md) - Response to this request
- [Coverage](./coverage.md) - Insurance coverage
- [Patient](./patient.md) - The patient
