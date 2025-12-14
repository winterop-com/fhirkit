# Claim

## Overview

The Claim resource represents a request for payment for healthcare services. Claims are submitted to insurers for reimbursement of services provided to patients.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/claim.html](https://hl7.org/fhir/R4/claim.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `type` | CodeableConcept | Claim type (professional, institutional, etc.) |
| `subType` | CodeableConcept | Claim subtype |
| `use` | code | claim, preauthorization, predetermination |
| `patient` | Reference(Patient) | Patient |
| `billablePeriod` | Period | Service period |
| `created` | dateTime | Creation date |
| `enterer` | Reference | Person entering claim |
| `insurer` | Reference(Organization) | Target insurer |
| `provider` | Reference | Billing provider |
| `priority` | CodeableConcept | Desired processing priority |
| `fundsReserve` | CodeableConcept | Funds reservation |
| `related` | BackboneElement[] | Related claims |
| `prescription` | Reference | Prescription |
| `payee` | BackboneElement | Recipient of payment |
| `referral` | Reference | Treatment referral |
| `facility` | Reference(Location) | Service facility |
| `careTeam` | BackboneElement[] | Care team members |
| `supportingInfo` | BackboneElement[] | Supporting info |
| `diagnosis` | BackboneElement[] | Diagnoses |
| `procedure` | BackboneElement[] | Procedures |
| `insurance` | BackboneElement[] | Insurance coverage |
| `accident` | BackboneElement | Accident info |
| `item` | BackboneElement[] | Service line items |
| `total` | Money | Total claim amount |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=claim-001` |
| `identifier` | token | Business identifier | `identifier=CLM-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Claim status | `status=active` |
| `created` | date | Creation date | `created=2024-01-15` |
| `provider` | reference | Provider | `provider=Practitioner/456` |
| `use` | token | Claim use | `use=claim` |
| `priority` | token | Priority | `priority=normal` |
| `insurer` | reference | Insurer | `insurer=Organization/789` |
| `facility` | reference | Facility | `facility=Location/123` |
| `care-team` | reference | Care team member | `care-team=Practitioner/456` |

## Examples

### Create a Claim

```bash
curl -X POST http://localhost:8080/baseR4/Claim \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Claim",
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
        "code": "professional",
        "display": "Professional"
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
    "created": "2024-01-20",
    "provider": {
      "reference": "Practitioner/practitioner-001"
    },
    "priority": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/processpriority",
        "code": "normal"
      }]
    },
    "insurance": [{
      "sequence": 1,
      "focal": true,
      "coverage": {
        "reference": "Coverage/coverage-001"
      }
    }],
    "diagnosis": [{
      "sequence": 1,
      "diagnosisCodeableConcept": {
        "coding": [{
          "system": "http://hl7.org/fhir/sid/icd-10",
          "code": "E11.9",
          "display": "Type 2 diabetes mellitus without complications"
        }]
      }
    }],
    "item": [{
      "sequence": 1,
      "productOrService": {
        "coding": [{
          "system": "http://www.ama-assn.org/go/cpt",
          "code": "99213",
          "display": "Office visit"
        }]
      },
      "servicedDate": "2024-01-15",
      "unitPrice": {
        "value": 150.00,
        "currency": "USD"
      },
      "net": {
        "value": 150.00,
        "currency": "USD"
      }
    }],
    "total": {
      "value": 150.00,
      "currency": "USD"
    }
  }'
```

### Search Claims

```bash
# By patient
curl "http://localhost:8080/baseR4/Claim?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Claim?status=active"

# By created date
curl "http://localhost:8080/baseR4/Claim?created=2024-01-20"

# By provider
curl "http://localhost:8080/baseR4/Claim?provider=Practitioner/456"
```

### Patient Compartment

```bash
# Get all claims for a patient
curl "http://localhost:8080/baseR4/Patient/123/Claim"
```

## Status Codes

| Code | Display |
|------|---------|
| active | Active |
| cancelled | Cancelled |
| draft | Draft |
| entered-in-error | Entered in Error |

## Use Codes

| Code | Display | Description |
|------|---------|-------------|
| claim | Claim | Actual claim submission |
| preauthorization | Pre-Authorization | Pre-authorization request |
| predetermination | Pre-Determination | Benefits determination |

## Claim Types

| Code | Display |
|------|---------|
| institutional | Institutional |
| oral | Oral |
| pharmacy | Pharmacy |
| professional | Professional |
| vision | Vision |
