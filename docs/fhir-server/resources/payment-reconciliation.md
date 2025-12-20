# PaymentReconciliation

## Overview

A PaymentReconciliation provides the bulk payment details associated with a payment by a payer for services rendered. It links payments to specific claims and provides reconciliation information.

This resource supports financial reconciliation by detailing how payments are allocated across multiple claims or services, including adjustments and payment notes.

**Common use cases:**
- Remittance advice
- Payment allocation details
- Financial reconciliation
- Payment tracking
- Adjustment documentation

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/paymentreconciliation.html](https://hl7.org/fhir/R4/paymentreconciliation.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `period` | Period | Period covered |
| `created` | dateTime | Creation date |
| `paymentIssuer` | Reference(Organization) | Party making payment |
| `request` | Reference(Task) | Original request |
| `requestor` | Reference(Practitioner|Organization) | Party requesting payment |
| `outcome` | code | queued, complete, error, partial |
| `disposition` | string | Disposition message |
| `paymentDate` | date | When payment issued |
| `paymentAmount` | Money | Total payment amount |
| `detail` | BackboneElement[] | Payment allocation details |
| `processNote` | BackboneElement[] | Processing notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=recon-001` |
| `identifier` | token | Business identifier | `identifier=RECON-12345` |
| `status` | token | Reconciliation status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `outcome` | token | Processing outcome | `outcome=complete` |
| `payment-issuer` | reference | Payment issuer | `payment-issuer=Organization/payer-001` |
| `request` | reference | Original request | `request=Task/task-001` |
| `requestor` | reference | Requestor | `requestor=Organization/hosp-001` |
| `disposition` | string | Disposition | `disposition=Processed` |
| `payment-date` | date | Payment date | `payment-date=2024-01-20` |

## Examples

### Create a PaymentReconciliation

```bash
curl -X POST http://localhost:8080/baseR4/PaymentReconciliation \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "PaymentReconciliation",
    "identifier": [{
      "system": "http://payer.example.org/reconciliations",
      "value": "RECON-2024-001"
    }],
    "status": "active",
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "created": "2024-02-01T10:00:00Z",
    "paymentIssuer": {"reference": "Organization/payer-001"},
    "outcome": "complete",
    "disposition": "Payment processed successfully",
    "paymentDate": "2024-02-01",
    "paymentAmount": {"value": 5000.00, "currency": "USD"},
    "detail": [{
      "type": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/payment-type",
          "code": "payment"
        }]
      },
      "request": {"reference": "Claim/claim-001"},
      "amount": {"value": 1500.00, "currency": "USD"}
    }]
  }'
```

### Search PaymentReconciliations

```bash
# By status
curl "http://localhost:8080/baseR4/PaymentReconciliation?status=active"

# By payment date
curl "http://localhost:8080/baseR4/PaymentReconciliation?payment-date=2024-02-01"

# By payment issuer
curl "http://localhost:8080/baseR4/PaymentReconciliation?payment-issuer=Organization/payer-001"

# By outcome
curl "http://localhost:8080/baseR4/PaymentReconciliation?outcome=complete"
```

## Generator Usage

```python
from fhirkit.server.generator import PaymentReconciliationGenerator

generator = PaymentReconciliationGenerator(seed=42)

# Generate a random payment reconciliation
recon = generator.generate()

# Generate with specific outcome
complete_recon = generator.generate(
    outcome="complete",
    status="active"
)

# Generate batch
recons = generator.generate_batch(count=10)
```

## Outcome Codes

| Code | Description |
|------|-------------|
| queued | Reconciliation is queued |
| complete | Processing complete |
| error | Error in processing |
| partial | Partial processing |

## Related Resources

- [PaymentNotice](./payment-notice.md) - Payment notification
- [Claim](./claim.md) - Related claims
- [ClaimResponse](./claim-response.md) - Claim responses
