# ChargeItem

## Overview

A ChargeItem represents the charge for a billable service or product provided to a patient. It captures the details of what was provided, who provided it, and the associated costs for billing purposes.

ChargeItems are the building blocks of healthcare billing, representing individual charges that can be aggregated into invoices or claims. They link clinical services to financial transactions.

**Common use cases:**
- Recording service charges
- Tracking billable items
- Linking procedures to costs
- Supporting claim creation
- Revenue cycle management

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/chargeitem.html](https://hl7.org/fhir/R4/chargeitem.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | planned, billable, not-billable, aborted, billed, entered-in-error, unknown |
| `code` | CodeableConcept | Code identifying the charge |
| `subject` | Reference(Patient) | Patient charged |
| `context` | Reference(Encounter) | Encounter context |
| `occurrenceDateTime` | dateTime | When the charge occurred |
| `occurrencePeriod` | Period | Period of service |
| `performer` | BackboneElement[] | Who performed the service |
| `performingOrganization` | Reference(Organization) | Performing organization |
| `requestingOrganization` | Reference(Organization) | Requesting organization |
| `quantity` | Quantity | Quantity of the charge |
| `priceOverride` | Money | Override price |
| `enterer` | Reference(Practitioner) | Who entered the charge |
| `enteredDate` | dateTime | When entered |
| `account` | Reference(Account)[] | Accounts to post to |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=charge-001` |
| `identifier` | token | Business identifier | `identifier=CHG-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `status` | token | Charge status | `status=billable` |
| `code` | token | Charge code | `code=99213` |
| `context` | reference | Encounter context | `context=Encounter/enc-001` |
| `occurrence` | date | When occurred | `occurrence=2024-01-15` |
| `enterer` | reference | Who entered | `enterer=Practitioner/456` |
| `entered-date` | date | Date entered | `entered-date=2024-01-15` |
| `performer-actor` | reference | Performer | `performer-actor=Practitioner/789` |
| `performing-organization` | reference | Organization | `performing-organization=Organization/org-001` |

## Examples

### Create a ChargeItem

```bash
curl -X POST http://localhost:8080/baseR4/ChargeItem \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ChargeItem",
    "identifier": [{
      "system": "http://hospital.example.org/charges",
      "value": "CHG-2024-001"
    }],
    "status": "billable",
    "code": {
      "coding": [{
        "system": "http://www.ama-assn.org/go/cpt",
        "code": "99213",
        "display": "Office visit, established patient, low complexity"
      }]
    },
    "subject": {"reference": "Patient/123"},
    "context": {"reference": "Encounter/enc-001"},
    "occurrenceDateTime": "2024-01-15T14:30:00Z",
    "performer": [{
      "actor": {"reference": "Practitioner/456"}
    }],
    "performingOrganization": {"reference": "Organization/clinic-001"},
    "quantity": {"value": 1},
    "enterer": {"reference": "Practitioner/admin-001"},
    "enteredDate": "2024-01-15T16:00:00Z",
    "account": [{"reference": "Account/acc-001"}]
  }'
```

### Search ChargeItems

```bash
# By patient
curl "http://localhost:8080/baseR4/ChargeItem?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/ChargeItem?status=billable"

# By encounter
curl "http://localhost:8080/baseR4/ChargeItem?context=Encounter/enc-001"

# By date range
curl "http://localhost:8080/baseR4/ChargeItem?occurrence=ge2024-01-01&occurrence=le2024-12-31"
```

## Generator Usage

```python
from fhirkit.server.generator import ChargeItemGenerator

generator = ChargeItemGenerator(seed=42)

# Generate a random charge item
charge = generator.generate()

# Generate billable charge for patient
billable_charge = generator.generate(
    subject_reference="Patient/123",
    status="billable"
)

# Generate batch
charges = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| planned | Charge is planned |
| billable | Charge is ready to bill |
| not-billable | Not billable |
| aborted | Charge was cancelled |
| billed | Already billed |
| entered-in-error | Entered in error |
| unknown | Status unknown |

## Related Resources

- [Account](./account.md) - Account to charge
- [Encounter](./encounter.md) - Service encounter
- [ChargeItemDefinition](./charge-item-definition.md) - Pricing rules
- [Invoice](./invoice.md) - Generated invoice
