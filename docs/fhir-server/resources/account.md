# Account

## Overview

An Account represents a financial account used to track billing charges and payments for a patient or group of patients. It aggregates financial transactions related to healthcare services and serves as the basis for billing and collections.

Accounts are used to group charges for billing purposes, manage payment allocations, and track the financial status of patient care. They support both individual patient accounts and group accounts for families or organizations.

**Common use cases:**
- Patient billing accounts
- Insurance account tracking
- Service period grouping
- Payment tracking
- Balance management

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/account.html](https://hl7.org/fhir/R4/account.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, inactive, entered-in-error, on-hold, unknown |
| `type` | CodeableConcept | Type of account (patient, insurance, etc.) |
| `name` | string | Human-readable account name |
| `subject` | Reference(Patient)[] | Who the account is for |
| `servicePeriod` | Period | Period of service covered |
| `coverage` | BackboneElement[] | Insurance coverage information |
| `owner` | Reference(Organization) | Organization responsible |
| `description` | string | Account description |
| `guarantor` | BackboneElement[] | Responsible parties |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=account-001` |
| `identifier` | token | Business identifier | `identifier=ACC-12345` |
| `name` | string | Account name | `name=Smith%20Family` |
| `status` | token | Account status | `status=active` |
| `type` | token | Account type | `type=patient` |
| `subject` | reference | Patient reference | `subject=Patient/123` |
| `patient` | reference | Patient reference (alias) | `patient=Patient/123` |
| `owner` | reference | Owner organization | `owner=Organization/hosp-001` |
| `period` | date | Service period | `period=ge2024-01-01` |

## Examples

### Create an Account

```bash
curl -X POST http://localhost:8080/baseR4/Account \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Account",
    "identifier": [{
      "system": "http://hospital.example.org/accounts",
      "value": "ACC-2024-001"
    }],
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "PBILLACCT",
        "display": "Patient Billing Account"
      }]
    },
    "name": "John Smith Patient Account",
    "subject": [{
      "reference": "Patient/123",
      "display": "John Smith"
    }],
    "servicePeriod": {
      "start": "2024-01-01"
    },
    "owner": {
      "reference": "Organization/hospital-001"
    }
  }'
```

### Search Accounts

```bash
# By patient
curl "http://localhost:8080/baseR4/Account?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Account?status=active"

# By owner
curl "http://localhost:8080/baseR4/Account?owner=Organization/hospital-001"

# By service period
curl "http://localhost:8080/baseR4/Account?period=ge2024-01-01"
```

## Generator Usage

```python
from fhirkit.server.generator import AccountGenerator

generator = AccountGenerator(seed=42)

# Generate a random account
account = generator.generate()

# Generate for specific patient
patient_account = generator.generate(
    subject_reference="Patient/123",
    status="active"
)

# Generate batch
accounts = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| active | Account is currently active |
| inactive | Account is not currently active |
| entered-in-error | Account was entered in error |
| on-hold | Account is on hold |
| unknown | Status is unknown |

## Related Resources

- [Patient](./patient.md) - Account subject
- [Coverage](./coverage.md) - Insurance coverage on the account
- [ChargeItem](./charge-item.md) - Charges posted to the account
- [Invoice](./invoice.md) - Invoices generated from the account
