# Coverage

## Overview

The Coverage resource represents insurance or payment information for a patient. It describes the financial coverage a patient has and links to the paying organization.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/coverage.html](https://hl7.org/fhir/R4/coverage.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `type` | CodeableConcept | Coverage type |
| `policyHolder` | Reference | Owner of the policy |
| `subscriber` | Reference | Subscriber to the policy |
| `subscriberId` | string | ID assigned to the subscriber |
| `beneficiary` | Reference(Patient) | Plan beneficiary |
| `dependent` | string | Dependent number |
| `relationship` | CodeableConcept | Beneficiary relationship to subscriber |
| `period` | Period | Coverage period |
| `payor` | Reference(Organization)[] | Insurance company |
| `class` | BackboneElement[] | Classification of coverage |
| `order` | positiveInt | Order of application |
| `network` | string | Insurer network |
| `costToBeneficiary` | BackboneElement[] | Cost sharing amounts |
| `subrogation` | boolean | Subrogation applies |
| `contract` | Reference(Contract)[] | Contract details |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=cov-001` |
| `identifier` | token | Business identifier | `identifier=COV-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `beneficiary` | reference | Beneficiary | `beneficiary=Patient/123` |
| `status` | token | Coverage status | `status=active` |
| `type` | token | Coverage type | `type=HIP` |
| `payor` | reference | Payor | `payor=Organization/456` |
| `subscriber` | reference | Subscriber | `subscriber=Patient/123` |
| `policy-holder` | reference | Policy holder | `policy-holder=Patient/123` |
| `class-type` | token | Class type | `class-type=group` |
| `class-value` | string | Class value | `class-value=EMPLOYER-001` |

## Examples

### Create a Coverage

```bash
curl -X POST http://localhost:8080/baseR4/Coverage \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Coverage",
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "HIP",
        "display": "Health insurance plan policy"
      }]
    },
    "subscriber": {
      "reference": "Patient/patient-001"
    },
    "beneficiary": {
      "reference": "Patient/patient-001"
    },
    "relationship": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
        "code": "self",
        "display": "Self"
      }]
    },
    "period": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "payor": [{
      "reference": "Organization/insurance-001",
      "display": "Blue Cross Blue Shield"
    }],
    "class": [
      {
        "type": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "group"
          }]
        },
        "value": "EMPLOYER-001",
        "name": "Employer Group Plan"
      },
      {
        "type": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "plan"
          }]
        },
        "value": "GOLD",
        "name": "Gold Plan"
      }
    ],
    "network": "PPO Network"
  }'
```

### Search Coverage

```bash
# By patient
curl "http://localhost:8080/baseR4/Coverage?patient=Patient/123"

# Active coverage
curl "http://localhost:8080/baseR4/Coverage?status=active"

# By payor
curl "http://localhost:8080/baseR4/Coverage?payor=Organization/456"
```

### Patient Compartment

```bash
# Get all coverage for a patient
curl "http://localhost:8080/baseR4/Patient/123/Coverage"
```

## Status Codes

| Code | Display |
|------|---------|
| active | Active |
| cancelled | Cancelled |
| draft | Draft |
| entered-in-error | Entered in Error |

## Coverage Types

| Code | Display |
|------|---------|
| HIP | Health insurance plan policy |
| EHCPOL | Extended healthcare |
| HSAPOL | Health spending account |
| AUTOPOL | Automobile |
| COL | Collision coverage |
| UNINSMOT | Uninsured motorist |
| PUBLICPOL | Public insurance |
| DENTPRG | Dental program |
| DRUGPOL | Drug policy |
| MCPOL | Managed care policy |
| MENTPOL | Mental health policy |
| VISPOL | Vision care policy |
