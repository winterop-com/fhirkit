# ClaimResponse

## Overview

A ClaimResponse represents the insurer's response to a healthcare claim submitted by a provider. It contains the adjudication results, payment details, and any adjustments or denials for the submitted claim items.

This resource is used to communicate the outcome of claim processing, including approved amounts, denied items, and payment information. It supports the financial reconciliation between providers and payers.

**Common use cases:**
- Claim adjudication results
- Payment determination
- Denial explanations
- Adjustment notifications
- Appeal tracking

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/claimresponse.html](https://hl7.org/fhir/R4/claimresponse.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `type` | CodeableConcept | Category of claim (institutional, oral, pharmacy, professional, vision) |
| `use` | code | claim, preauthorization, predetermination |
| `patient` | Reference(Patient) | The recipient of the claim |
| `created` | dateTime | Response creation date |
| `insurer` | Reference(Organization) | Insurer processing the claim |
| `requestor` | Reference(Practitioner|Organization) | Party that submitted the claim |
| `request` | Reference(Claim) | The original claim |
| `outcome` | code | queued, complete, error, partial |
| `disposition` | string | Disposition message |
| `payment` | BackboneElement | Payment details |
| `item` | BackboneElement[] | Adjudication for each claim item |
| `addItem` | BackboneElement[] | Additional items added by insurer |
| `total` | BackboneElement[] | Adjudication totals |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=response-001` |
| `identifier` | token | Business identifier | `identifier=RESP-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Response status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `request` | reference | Original claim | `request=Claim/claim-001` |
| `insurer` | reference | Insurer reference | `insurer=Organization/payer-001` |
| `outcome` | token | Processing outcome | `outcome=complete` |
| `use` | token | Claim use | `use=claim` |
| `disposition` | string | Disposition message | `disposition=Approved` |
| `requestor` | reference | Claim submitter | `requestor=Practitioner/456` |
| `payment-date` | date | Payment date | `payment-date=2024-01-20` |

## Examples

### Create a ClaimResponse

```bash
curl -X POST http://localhost:8080/baseR4/ClaimResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ClaimResponse",
    "identifier": [{
      "system": "http://payer.example.org/responses",
      "value": "RESP-2024-001"
    }],
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
        "code": "professional",
        "display": "Professional"
      }]
    },
    "use": "claim",
    "patient": {"reference": "Patient/123"},
    "created": "2024-01-15T10:30:00Z",
    "insurer": {"reference": "Organization/payer-001"},
    "request": {"reference": "Claim/claim-001"},
    "outcome": "complete",
    "disposition": "Claim approved and processed",
    "payment": {
      "type": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/ex-paymenttype",
          "code": "complete"
        }]
      },
      "date": "2024-01-20",
      "amount": {"value": 150.00, "currency": "USD"}
    }
  }'
```

### Search ClaimResponses

```bash
# By patient
curl "http://localhost:8080/baseR4/ClaimResponse?patient=Patient/123"

# By outcome
curl "http://localhost:8080/baseR4/ClaimResponse?outcome=complete"

# By original claim
curl "http://localhost:8080/baseR4/ClaimResponse?request=Claim/claim-001"

# By date range
curl "http://localhost:8080/baseR4/ClaimResponse?created=ge2024-01-01&created=le2024-12-31"
```

## Generator Usage

```python
from fhirkit.server.generator import ClaimResponseGenerator

generator = ClaimResponseGenerator(seed=42)

# Generate a random claim response
response = generator.generate()

# Generate with specific outcome
approved = generator.generate(outcome="complete")

# Generate for a specific claim
claim_response = generator.generate(
    request_reference="Claim/claim-001",
    patient_reference="Patient/123",
    outcome="complete"
)

# Generate batch
responses = generator.generate_batch(count=10)
```

## Outcome Codes

| Code | Description |
|------|-------------|
| queued | Claim is queued for processing |
| complete | Processing is complete |
| error | Error in processing |
| partial | Partial processing |

## Related Resources

- [Claim](./claim.md) - The original claim
- [Patient](./patient.md) - The claim recipient
- [Coverage](./coverage.md) - Insurance coverage
- [ExplanationOfBenefit](./explanation-of-benefit.md) - Detailed explanation
