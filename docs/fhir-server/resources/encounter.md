# Encounter

## Overview

The Encounter resource represents an interaction between a patient and healthcare provider(s) for the purpose of providing healthcare services. This includes ambulatory visits, emergency room visits, inpatient stays, and home health visits.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/encounter.html](https://hl7.org/fhir/R4/encounter.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | planned, arrived, triaged, in-progress, onleave, finished, cancelled, entered-in-error, unknown |
| `statusHistory` | BackboneElement[] | Status change history |
| `class` | Coding | Classification (ambulatory, emergency, inpatient, etc.) |
| `classHistory` | BackboneElement[] | Class change history |
| `type` | CodeableConcept[] | Specific type of encounter |
| `serviceType` | CodeableConcept | Type of service |
| `priority` | CodeableConcept | Indicates urgency |
| `subject` | Reference(Patient) | The patient |
| `episodeOfCare` | Reference(EpisodeOfCare)[] | Episodes this is part of |
| `basedOn` | Reference(ServiceRequest)[] | Referrals that initiated this |
| `participant` | BackboneElement[] | Participants in the encounter |
| `appointment` | Reference(Appointment)[] | Appointments that led to this |
| `period` | Period | Start and end times |
| `length` | Duration | Duration of encounter |
| `reasonCode` | CodeableConcept[] | Reason for encounter |
| `diagnosis` | BackboneElement[] | Diagnoses relevant to encounter |
| `hospitalization` | BackboneElement | Details about hospitalization |
| `location` | BackboneElement[] | Locations during encounter |
| `serviceProvider` | Reference(Organization) | Organization responsible |
| `partOf` | Reference(Encounter) | Parent encounter |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=enc-001` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `status` | token | Encounter status | `status=finished` |
| `class` | token | Encounter class | `class=AMB` |
| `type` | token | Encounter type | `type=99213` |
| `date` | date | Encounter date | `date=2024-01-15` |
| `participant` | reference | Participant reference | `participant=Practitioner/456` |
| `service-provider` | reference | Service provider | `service-provider=Organization/789` |

## Examples

### Create an Encounter

```bash
curl -X POST http://localhost:8080/baseR4/Encounter \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Encounter",
    "status": "finished",
    "class": {
      "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
      "code": "AMB",
      "display": "ambulatory"
    },
    "type": [{
      "coding": [{
        "system": "http://www.ama-assn.org/go/cpt",
        "code": "99213",
        "display": "Office visit, established patient"
      }]
    }],
    "subject": {
      "reference": "Patient/patient-001"
    },
    "participant": [{
      "type": [{
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
          "code": "ATND",
          "display": "attender"
        }]
      }],
      "individual": {
        "reference": "Practitioner/practitioner-001",
        "display": "Dr. Jane Smith"
      }
    }],
    "period": {
      "start": "2024-01-15T09:00:00Z",
      "end": "2024-01-15T09:30:00Z"
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "185389009",
        "display": "Follow-up visit"
      }]
    }],
    "serviceProvider": {
      "reference": "Organization/organization-001"
    }
  }'
```

### Search Encounters

```bash
# By patient
curl "http://localhost:8080/baseR4/Encounter?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Encounter?status=finished"

# By class
curl "http://localhost:8080/baseR4/Encounter?class=AMB"

# By date
curl "http://localhost:8080/baseR4/Encounter?date=2024-01-15"

# Combined: patient's ambulatory encounters
curl "http://localhost:8080/baseR4/Encounter?patient=Patient/123&class=AMB"
```

### With _include

```bash
# Include patient
curl "http://localhost:8080/baseR4/Encounter?_include=Encounter:patient"

# Include participant
curl "http://localhost:8080/baseR4/Encounter?_include=Encounter:participant"

# Include service provider
curl "http://localhost:8080/baseR4/Encounter?_include=Encounter:service-provider"
```

### Patient Compartment

```bash
# Get all encounters for a patient
curl "http://localhost:8080/baseR4/Patient/123/Encounter"

# Filter by status
curl "http://localhost:8080/baseR4/Patient/123/Encounter?status=finished"
```

## Generator

The `EncounterGenerator` creates synthetic Encounter resources with:

- Realistic encounter classes and types
- Appropriate durations based on encounter type
- Linked participants and organizations

### Usage

```python
from fhir_cql.server.generator import EncounterGenerator

generator = EncounterGenerator(seed=42)

# Generate a random encounter
encounter = generator.generate(
    patient_ref="Patient/123",
    practitioner_ref="Practitioner/456"
)

# Generate batch
encounters = generator.generate_batch(
    count=10,
    patient_ref="Patient/123"
)
```

## Encounter Status

| Code | Display | Description |
|------|---------|-------------|
| planned | Planned | Not yet started |
| arrived | Arrived | Patient has arrived |
| triaged | Triaged | Patient has been triaged |
| in-progress | In Progress | Currently ongoing |
| onleave | On Leave | Patient temporarily left |
| finished | Finished | Completed |
| cancelled | Cancelled | Was cancelled |
| entered-in-error | Entered in Error | Data entry error |
| unknown | Unknown | Status unknown |

## Encounter Class (v3-ActCode)

| Code | Display | Description |
|------|---------|-------------|
| AMB | Ambulatory | Outpatient visit |
| EMER | Emergency | Emergency room visit |
| FLD | Field | Field encounter |
| HH | Home Health | Home health visit |
| IMP | Inpatient | Inpatient admission |
| ACUTE | Inpatient Acute | Acute inpatient stay |
| NONAC | Inpatient Non-Acute | Non-acute inpatient |
| OBSENC | Observation | Observation encounter |
| PRENC | Pre-Admission | Pre-admission |
| SS | Short Stay | Short stay |
| VR | Virtual | Virtual/telehealth |
