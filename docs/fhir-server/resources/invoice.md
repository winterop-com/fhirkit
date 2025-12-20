# Invoice

## Overview

An Invoice represents a statement of charges for goods or services provided. It aggregates ChargeItems and provides the total amounts due, along with payment terms and billing information.

This resource is used to create and manage bills sent to patients, insurance companies, or other responsible parties for healthcare services.

**Common use cases:**
- Patient billing statements
- Insurance claims
- Service invoicing
- Payment requests
- Account statements

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/invoice.html](https://hl7.org/fhir/R4/invoice.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | draft, issued, balanced, cancelled, entered-in-error |
| `type` | CodeableConcept | Type of invoice |
| `subject` | Reference(Patient) | Recipient of invoice |
| `date` | dateTime | Invoice date |
| `issuer` | Reference(Organization) | Issuing organization |
| `recipient` | Reference(Organization|Patient) | Recipient of the invoice |
| `account` | Reference(Account) | Billing account |
| `lineItem` | BackboneElement[] | Invoice line items |
| `totalPriceComponent` | BackboneElement[] | Total price components |
| `totalNet` | Money | Net total |
| `totalGross` | Money | Gross total |
| `paymentTerms` | markdown | Payment terms |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=invoice-001` |
| `identifier` | token | Business identifier | `identifier=INV-12345` |
| `status` | token | Invoice status | `status=issued` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `date` | date | Invoice date | `date=2024-01-15` |
| `issuer` | reference | Issuer reference | `issuer=Organization/hosp-001` |
| `recipient` | reference | Recipient reference | `recipient=Patient/123` |
| `account` | reference | Account reference | `account=Account/acc-001` |
| `type` | token | Invoice type | `type=patient` |
| `participant` | reference | Participant actor | `participant=Practitioner/456` |
| `participant-role` | token | Participant role | `participant-role=attending` |

## Examples

### Create an Invoice

```bash
curl -X POST http://localhost:8080/baseR4/Invoice \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Invoice",
    "identifier": [{
      "system": "http://hospital.example.org/invoices",
      "value": "INV-2024-001"
    }],
    "status": "issued",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v2-0481",
        "code": "P",
        "display": "Patient Invoice"
      }]
    },
    "subject": {"reference": "Patient/123"},
    "date": "2024-01-15",
    "issuer": {"reference": "Organization/hospital-001"},
    "recipient": {"reference": "Patient/123"},
    "account": {"reference": "Account/acc-001"},
    "lineItem": [{
      "chargeItemReference": {"reference": "ChargeItem/chg-001"},
      "priceComponent": [{
        "type": "base",
        "amount": {"value": 150.00, "currency": "USD"}
      }]
    }],
    "totalNet": {"value": 150.00, "currency": "USD"},
    "totalGross": {"value": 162.00, "currency": "USD"},
    "paymentTerms": "Payment due within 30 days"
  }'
```

### Search Invoices

```bash
# By patient
curl "http://localhost:8080/baseR4/Invoice?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Invoice?status=issued"

# By date range
curl "http://localhost:8080/baseR4/Invoice?date=ge2024-01-01&date=le2024-12-31"

# By issuer
curl "http://localhost:8080/baseR4/Invoice?issuer=Organization/hospital-001"
```

## Generator Usage

```python
from fhirkit.server.generator import InvoiceGenerator

generator = InvoiceGenerator(seed=42)

# Generate a random invoice
invoice = generator.generate()

# Generate for specific patient
patient_invoice = generator.generate(
    subject_reference="Patient/123",
    status="issued"
)

# Generate batch
invoices = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| draft | Invoice is a draft |
| issued | Invoice has been issued |
| balanced | Invoice is balanced (paid) |
| cancelled | Invoice was cancelled |
| entered-in-error | Entered in error |

## Related Resources

- [ChargeItem](./charge-item.md) - Invoice line items
- [Account](./account.md) - Billing account
- [Patient](./patient.md) - Invoice recipient
- [Organization](./organization.md) - Invoice issuer
