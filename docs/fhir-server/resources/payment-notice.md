# PaymentNotice

## Overview

A PaymentNotice indicates that a payment has been, or will be, made. It serves as a notification between parties about payment status and can reference the payment reconciliation details.

This resource supports the financial workflow by communicating payment information between providers, payers, and other parties involved in healthcare billing.

**Common use cases:**
- Payment notifications
- Payment status updates
- Remittance advice references
- Payment confirmation

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/paymentnotice.html](https://hl7.org/fhir/R4/paymentnotice.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `request` | Reference(Any) | Request being paid |
| `response` | Reference(Any) | Response to the request |
| `created` | dateTime | Creation date |
| `provider` | Reference(Practitioner|Organization) | Responsible party |
| `payment` | Reference(PaymentReconciliation) | Payment reference |
| `paymentDate` | date | Payment or clearing date |
| `payee` | Reference(Practitioner|Organization) | Party receiving payment |
| `recipient` | Reference(Organization) | Party being notified |
| `amount` | Money | Payment amount |
| `paymentStatus` | CodeableConcept | Payment status |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=notice-001` |
| `identifier` | token | Business identifier | `identifier=PMT-12345` |
| `status` | token | Notice status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `provider` | reference | Provider reference | `provider=Organization/hosp-001` |
| `request` | reference | Related request | `request=Claim/claim-001` |
| `response` | reference | Related response | `response=ClaimResponse/resp-001` |
| `payment-status` | token | Payment status | `payment-status=paid` |
| `payment-date` | date | Payment date | `payment-date=2024-01-20` |

## Examples

### Create a PaymentNotice

```bash
curl -X POST http://localhost:8080/baseR4/PaymentNotice \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "PaymentNotice",
    "identifier": [{
      "system": "http://payer.example.org/notices",
      "value": "PMT-2024-001"
    }],
    "status": "active",
    "created": "2024-01-15T10:00:00Z",
    "provider": {"reference": "Organization/hospital-001"},
    "payment": {"reference": "PaymentReconciliation/recon-001"},
    "paymentDate": "2024-01-20",
    "recipient": {"reference": "Organization/hospital-001"},
    "amount": {"value": 1500.00, "currency": "USD"},
    "paymentStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/paymentstatus",
        "code": "paid",
        "display": "Paid"
      }]
    }
  }'
```

### Search PaymentNotices

```bash
# By status
curl "http://localhost:8080/baseR4/PaymentNotice?status=active"

# By payment date
curl "http://localhost:8080/baseR4/PaymentNotice?payment-date=2024-01-20"

# By provider
curl "http://localhost:8080/baseR4/PaymentNotice?provider=Organization/hospital-001"
```

## Generator Usage

```python
from fhirkit.server.generator import PaymentNoticeGenerator

generator = PaymentNoticeGenerator(seed=42)

# Generate a random payment notice
notice = generator.generate()

# Generate with specific status
paid_notice = generator.generate(status="active")

# Generate batch
notices = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| active | Notice is active |
| cancelled | Notice was cancelled |
| draft | Notice is a draft |
| entered-in-error | Entered in error |

## Related Resources

- [PaymentReconciliation](./payment-reconciliation.md) - Payment details
- [Claim](./claim.md) - Related claim
- [ClaimResponse](./claim-response.md) - Related claim response
