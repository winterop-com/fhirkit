# ExplanationOfBenefit

## Overview

The ExplanationOfBenefit (EOB) resource represents the results of a claim adjudication. It provides detailed information about what was paid, what the patient owes, and how the claim was processed.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/explanationofbenefit.html](https://hl7.org/fhir/R4/explanationofbenefit.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `type` | CodeableConcept | Claim type |
| `subType` | CodeableConcept | Claim subtype |
| `use` | code | claim, preauthorization, predetermination |
| `patient` | Reference(Patient) | Patient |
| `billablePeriod` | Period | Service period |
| `created` | dateTime | Creation date |
| `enterer` | Reference | Person entering EOB |
| `insurer` | Reference(Organization) | Insurer |
| `provider` | Reference | Provider |
| `outcome` | code | queued, complete, error, partial |
| `disposition` | string | Disposition message |
| `claim` | Reference(Claim) | Original claim |
| `claimResponse` | Reference | Claim response |
| `insurance` | BackboneElement[] | Insurance coverage |
| `item` | BackboneElement[] | Service line items |
| `adjudication` | BackboneElement[] | Header adjudication |
| `total` | BackboneElement[] | Total amounts |
| `payment` | BackboneElement | Payment details |
| `processNote` | BackboneElement[] | Processing notes |
| `benefitPeriod` | Period | Benefit period |
| `benefitBalance` | BackboneElement[] | Balance by category |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=eob-001` |
| `identifier` | token | Business identifier | `identifier=EOB-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | EOB status | `status=active` |
| `created` | date | Creation date | `created=2024-01-25` |
| `claim` | reference | Claim reference | `claim=Claim/456` |
| `provider` | reference | Provider | `provider=Practitioner/789` |
| `insurer` | reference | Insurer | `insurer=Organization/123` |
| `outcome` | token | Processing outcome | `outcome=complete` |
| `use` | token | EOB use | `use=claim` |
| `disposition` | string | Disposition | `disposition=paid` |
| `facility` | reference | Facility | `facility=Location/456` |
| `coverage` | reference | Coverage | `coverage=Coverage/789` |
| `care-team` | reference | Care team member | `care-team=Practitioner/123` |

## Examples

### Create an ExplanationOfBenefit

```bash
curl -X POST http://localhost:8080/baseR4/ExplanationOfBenefit \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ExplanationOfBenefit",
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
        "code": "professional"
      }]
    },
    "use": "claim",
    "patient": {
      "reference": "Patient/patient-001"
    },
    "billablePeriod": {
      "start": "2024-01-15",
      "end": "2024-01-15"
    },
    "created": "2024-01-25",
    "insurer": {
      "reference": "Organization/insurance-001"
    },
    "provider": {
      "reference": "Practitioner/practitioner-001"
    },
    "outcome": "complete",
    "disposition": "Claim processed successfully",
    "insurance": [{
      "focal": true,
      "coverage": {
        "reference": "Coverage/coverage-001"
      }
    }],
    "item": [{
      "sequence": 1,
      "productOrService": {
        "coding": [{
          "system": "http://www.ama-assn.org/go/cpt",
          "code": "99213"
        }]
      },
      "adjudication": [
        {
          "category": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/adjudication",
              "code": "submitted"
            }]
          },
          "amount": {"value": 150.00, "currency": "USD"}
        },
        {
          "category": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/adjudication",
              "code": "benefit"
            }]
          },
          "amount": {"value": 100.00, "currency": "USD"}
        }
      ]
    }],
    "total": [
      {
        "category": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "submitted"
          }]
        },
        "amount": {"value": 150.00, "currency": "USD"}
      },
      {
        "category": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/adjudication",
            "code": "benefit"
          }]
        },
        "amount": {"value": 100.00, "currency": "USD"}
      }
    ],
    "payment": {
      "type": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/ex-paymenttype",
          "code": "complete"
        }]
      },
      "date": "2024-01-28",
      "amount": {"value": 100.00, "currency": "USD"}
    }
  }'
```

### Search ExplanationOfBenefits

```bash
# By patient
curl "http://localhost:8080/baseR4/ExplanationOfBenefit?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/ExplanationOfBenefit?status=active"

# By outcome
curl "http://localhost:8080/baseR4/ExplanationOfBenefit?outcome=complete"

# By created date
curl "http://localhost:8080/baseR4/ExplanationOfBenefit?created=2024-01-25"
```

### Patient Compartment

```bash
# Get all EOBs for a patient
curl "http://localhost:8080/baseR4/Patient/123/ExplanationOfBenefit"
```

## Status Codes

| Code | Display |
|------|---------|
| active | Active |
| cancelled | Cancelled |
| draft | Draft |
| entered-in-error | Entered in Error |

## Outcome Codes

| Code | Display | Description |
|------|---------|-------------|
| queued | Queued | Still being processed |
| complete | Complete | Processing complete |
| error | Error | Processing error |
| partial | Partial | Partially processed |

## Adjudication Categories

| Code | Display |
|------|---------|
| submitted | Submitted Amount |
| copay | CoPay |
| eligible | Eligible Amount |
| deductible | Deductible |
| benefit | Benefit Amount |
