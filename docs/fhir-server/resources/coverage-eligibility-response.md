# CoverageEligibilityResponse

## Overview

A CoverageEligibilityResponse represents an insurer's response to a coverage eligibility request. It contains information about the patient's coverage status, benefits available, and any limitations or exclusions.

This resource provides detailed benefit information including covered services, co-pays, deductibles, and authorization requirements that help providers understand what will be covered before providing care.

**Common use cases:**
- Eligibility verification results
- Benefit details communication
- Authorization status
- Cost sharing information
- Coverage limitations

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/coverageeligibilityresponse.html](https://hl7.org/fhir/R4/coverageeligibilityresponse.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `purpose` | code[] | auth-requirements, benefits, discovery, validation |
| `patient` | Reference(Patient) | Patient for the response |
| `created` | dateTime | Response creation date |
| `request` | Reference(CoverageEligibilityRequest) | Original request |
| `requestor` | Reference(Practitioner|Organization) | Requesting party |
| `insurer` | Reference(Organization) | Responding insurer |
| `outcome` | code | queued, complete, error, partial |
| `disposition` | string | Disposition message |
| `insurance` | BackboneElement[] | Insurance information |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=response-001` |
| `identifier` | token | Business identifier | `identifier=RESP-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Response status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `request` | reference | Original request | `request=CoverageEligibilityRequest/req-001` |
| `insurer` | reference | Insurer reference | `insurer=Organization/payer-001` |
| `outcome` | token | Processing outcome | `outcome=complete` |
| `requestor` | reference | Requestor | `requestor=Practitioner/456` |
| `disposition` | string | Disposition | `disposition=Eligible` |

## Examples

### Create a CoverageEligibilityResponse

```bash
curl -X POST http://localhost:8080/baseR4/CoverageEligibilityResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CoverageEligibilityResponse",
    "identifier": [{
      "system": "http://payer.example.org/responses",
      "value": "RESP-2024-001"
    }],
    "status": "active",
    "purpose": ["benefits"],
    "patient": {"reference": "Patient/123"},
    "created": "2024-01-15T10:30:00Z",
    "request": {"reference": "CoverageEligibilityRequest/req-001"},
    "insurer": {"reference": "Organization/payer-001"},
    "outcome": "complete",
    "disposition": "Patient is eligible for benefits"
  }'
```

### Search CoverageEligibilityResponses

```bash
# By patient
curl "http://localhost:8080/baseR4/CoverageEligibilityResponse?patient=Patient/123"

# By outcome
curl "http://localhost:8080/baseR4/CoverageEligibilityResponse?outcome=complete"

# By request
curl "http://localhost:8080/baseR4/CoverageEligibilityResponse?request=CoverageEligibilityRequest/req-001"
```

## Generator Usage

```python
from fhirkit.server.generator import CoverageEligibilityResponseGenerator

generator = CoverageEligibilityResponseGenerator(seed=42)

# Generate a random response
response = generator.generate()

# Generate with specific outcome
eligible = generator.generate(
    outcome="complete",
    disposition="Patient is eligible"
)

# Generate batch
responses = generator.generate_batch(count=10)
```

## Outcome Codes

| Code | Description |
|------|-------------|
| queued | Request is queued |
| complete | Processing complete |
| error | Error in processing |
| partial | Partial processing |

## Related Resources

- [CoverageEligibilityRequest](./coverage-eligibility-request.md) - The original request
- [Coverage](./coverage.md) - Insurance coverage details
- [Patient](./patient.md) - The patient
