# CareTeam

## Overview

The CareTeam resource represents a team of healthcare providers and related persons caring for a patient. Care teams coordinate care delivery across multiple providers and settings.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/careteam.html](https://hl7.org/fhir/R4/careteam.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | proposed, active, suspended, inactive, entered-in-error |
| `category` | CodeableConcept[] | Type of care team |
| `name` | string | Name of care team |
| `subject` | Reference(Patient) | Patient |
| `encounter` | Reference(Encounter) | Encounter context |
| `period` | Period | Active time period |
| `participant` | BackboneElement[] | Team members |
| `reasonCode` | CodeableConcept[] | Why team exists |
| `reasonReference` | Reference(Condition)[] | Conditions being addressed |
| `managingOrganization` | Reference(Organization)[] | Managing organization |
| `telecom` | ContactPoint[] | Team contact info |
| `note` | Annotation[] | Additional notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=ct-001` |
| `identifier` | token | Business identifier | `identifier=CT-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `status` | token | Team status | `status=active` |
| `category` | token | Team category | `category=LA27976-2` |
| `participant` | reference | Team member | `participant=Practitioner/456` |
| `encounter` | reference | Encounter | `encounter=Encounter/789` |
| `date` | date | Period start | `date=ge2024-01-01` |
| `name` | string | Team name | `name=Diabetes` |

## Examples

### Create a CareTeam

```bash
curl -X POST http://localhost:8080/baseR4/CareTeam \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CareTeam",
    "status": "active",
    "category": [{
      "coding": [{
        "system": "http://loinc.org",
        "code": "LA27976-2",
        "display": "Multidisciplinary care team"
      }]
    }],
    "name": "Diabetes Care Team",
    "subject": {
      "reference": "Patient/patient-001",
      "display": "John Smith"
    },
    "period": {"start": "2024-01-01"},
    "participant": [
      {
        "role": [{
          "coding": [{
            "system": "http://snomed.info/sct",
            "code": "446050000",
            "display": "Primary care physician"
          }]
        }],
        "member": {
          "reference": "Practitioner/practitioner-001",
          "display": "Dr. Jane Smith"
        },
        "period": {"start": "2024-01-01"}
      },
      {
        "role": [{
          "coding": [{
            "system": "http://snomed.info/sct",
            "code": "159033005",
            "display": "Dietitian"
          }]
        }],
        "member": {
          "reference": "Practitioner/dietitian-001",
          "display": "Sarah Johnson, RD"
        }
      }
    ],
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "73211009",
        "display": "Diabetes mellitus"
      }]
    }],
    "managingOrganization": [{
      "reference": "Organization/organization-001",
      "display": "General Hospital"
    }],
    "telecom": [{
      "system": "email",
      "value": "diabetes-care@hospital.org"
    }]
  }'
```

### Search CareTeams

```bash
# By patient
curl "http://localhost:8080/baseR4/CareTeam?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/CareTeam?status=active"

# By participant
curl "http://localhost:8080/baseR4/CareTeam?participant=Practitioner/456"

# By category
curl "http://localhost:8080/baseR4/CareTeam?category=LA27976-2"
```

### Patient Compartment

```bash
# Get all care teams for a patient
curl "http://localhost:8080/baseR4/Patient/123/CareTeam"
```

## Status Codes

| Code | Display |
|------|---------|
| proposed | Proposed |
| active | Active |
| suspended | Suspended |
| inactive | Inactive |
| entered-in-error | Entered in Error |

## Category Codes (LOINC)

| Code | Display |
|------|---------|
| LA27976-2 | Multidisciplinary care team |
| LA27980-4 | Care coordination team |
| LA28865-6 | Longitudinal care team |
| LA28866-4 | Episode-based care team |
| LA27977-0 | Home and community based services team |
| LA27978-8 | Clinical research team |
| LA27979-6 | Public health team |
