# MedicationRequest

## Overview

The MedicationRequest resource represents a prescription or order for medication. This includes both inpatient and outpatient prescriptions, as well as medication recommendations.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/medicationrequest.html](https://hl7.org/fhir/R4/medicationrequest.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, on-hold, cancelled, completed, entered-in-error, stopped, draft, unknown |
| `statusReason` | CodeableConcept | Why current status |
| `intent` | code | proposal, plan, order, original-order, reflex-order, filler-order, instance-order, option |
| `category` | CodeableConcept[] | inpatient, outpatient, community |
| `priority` | code | routine, urgent, asap, stat |
| `doNotPerform` | boolean | Do not dispense |
| `reported[x]` | boolean or Reference | Reported vs primary record |
| `medication[x]` | CodeableConcept or Reference(Medication) | Medication |
| `subject` | Reference(Patient) | Patient |
| `encounter` | Reference(Encounter) | Encounter context |
| `authoredOn` | dateTime | When request was authored |
| `requester` | Reference(Practitioner) | Prescriber |
| `performer` | Reference | Intended performer |
| `reasonCode` | CodeableConcept[] | Reason for prescription |
| `reasonReference` | Reference[] | Condition justification |
| `note` | Annotation[] | Additional notes |
| `dosageInstruction` | Dosage[] | How to take |
| `dispenseRequest` | BackboneElement | Dispensing details |
| `substitution` | BackboneElement | Substitution preferences |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=medrx-001` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Medication code | `code=http://www.nlm.nih.gov/research/umls/rxnorm\|197361` |
| `status` | token | Request status | `status=active` |
| `intent` | token | Request intent | `intent=order` |
| `authoredon` | date | Authored date | `authoredon=2024-01-15` |
| `requester` | reference | Prescriber | `requester=Practitioner/456` |
| `encounter` | reference | Encounter | `encounter=Encounter/789` |

## Examples

### Create a MedicationRequest

```bash
curl -X POST http://localhost:8080/baseR4/MedicationRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MedicationRequest",
    "status": "active",
    "intent": "order",
    "medicationCodeableConcept": {
      "coding": [{
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "197361",
        "display": "Lisinopril 10 MG Oral Tablet"
      }]
    },
    "subject": {
      "reference": "Patient/patient-001"
    },
    "authoredOn": "2024-01-15T10:30:00Z",
    "requester": {
      "reference": "Practitioner/practitioner-001",
      "display": "Dr. Jane Smith"
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "38341003",
        "display": "Hypertensive disorder"
      }]
    }],
    "dosageInstruction": [{
      "sequence": 1,
      "text": "Take one tablet by mouth once daily",
      "timing": {
        "repeat": {
          "frequency": 1,
          "period": 1,
          "periodUnit": "d"
        }
      },
      "route": {
        "coding": [{
          "system": "http://snomed.info/sct",
          "code": "26643006",
          "display": "Oral route"
        }]
      },
      "doseAndRate": [{
        "doseQuantity": {
          "value": 1,
          "unit": "tablet",
          "system": "http://terminology.hl7.org/CodeSystem/v3-orderableDrugForm",
          "code": "TAB"
        }
      }]
    }],
    "dispenseRequest": {
      "validityPeriod": {
        "start": "2024-01-15",
        "end": "2025-01-15"
      },
      "numberOfRepeatsAllowed": 3,
      "quantity": {
        "value": 30,
        "unit": "tablets"
      },
      "expectedSupplyDuration": {
        "value": 30,
        "unit": "days",
        "system": "http://unitsofmeasure.org",
        "code": "d"
      }
    }
  }'
```

### Search MedicationRequests

```bash
# By patient
curl "http://localhost:8080/baseR4/MedicationRequest?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/MedicationRequest?status=active"

# By medication code
curl "http://localhost:8080/baseR4/MedicationRequest?code=http://www.nlm.nih.gov/research/umls/rxnorm|197361"

# Active orders
curl "http://localhost:8080/baseR4/MedicationRequest?status=active&intent=order"

# By prescriber
curl "http://localhost:8080/baseR4/MedicationRequest?requester=Practitioner/456"
```

### Patient Compartment

```bash
# Get all prescriptions for a patient
curl "http://localhost:8080/baseR4/Patient/123/MedicationRequest"

# Active prescriptions only
curl "http://localhost:8080/baseR4/Patient/123/MedicationRequest?status=active"
```

## Status Codes

| Code | Display |
|------|---------|
| active | Active |
| on-hold | On Hold |
| cancelled | Cancelled |
| completed | Completed |
| entered-in-error | Entered in Error |
| stopped | Stopped |
| draft | Draft |
| unknown | Unknown |

## Intent Codes

| Code | Display | Description |
|------|---------|-------------|
| proposal | Proposal | Suggested prescription |
| plan | Plan | Planned prescription |
| order | Order | Authorized prescription |
| original-order | Original Order | First order |
| reflex-order | Reflex Order | Automatic follow-up |
| filler-order | Filler Order | Pharmacy order |
| instance-order | Instance Order | Specific instance |
| option | Option | Treatment option |
