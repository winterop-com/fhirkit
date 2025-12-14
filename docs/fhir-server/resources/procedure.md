# Procedure

## Overview

The Procedure resource represents an action performed on a patient for diagnostic or therapeutic purposes. This includes surgeries, diagnostic procedures, therapeutic procedures, and counseling sessions.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/procedure.html](https://hl7.org/fhir/R4/procedure.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `instantiatesCanonical` | canonical[] | Protocol/guideline followed |
| `basedOn` | Reference(ServiceRequest)[] | Fulfills order |
| `partOf` | Reference(Procedure)[] | Part of another procedure |
| `status` | code | preparation, in-progress, not-done, on-hold, stopped, completed, entered-in-error, unknown |
| `statusReason` | CodeableConcept | Why status is current value |
| `category` | CodeableConcept | Classification |
| `code` | CodeableConcept | Procedure code (CPT, SNOMED CT) |
| `subject` | Reference(Patient) | Patient |
| `encounter` | Reference(Encounter) | Encounter context |
| `performed[x]` | dateTime, Period, string, Age, Range | When performed |
| `recorder` | Reference | Who recorded |
| `asserter` | Reference | Who asserted |
| `performer` | BackboneElement[] | Who performed |
| `location` | Reference(Location) | Where performed |
| `reasonCode` | CodeableConcept[] | Why performed |
| `reasonReference` | Reference[] | Condition/Observation justification |
| `bodySite` | CodeableConcept[] | Anatomical location |
| `outcome` | CodeableConcept | Result of procedure |
| `report` | Reference(DiagnosticReport)[] | Reports |
| `complication` | CodeableConcept[] | Complications |
| `complicationDetail` | Reference(Condition)[] | Complication details |
| `followUp` | CodeableConcept[] | Follow-up instructions |
| `note` | Annotation[] | Additional notes |
| `focalDevice` | BackboneElement[] | Devices used |
| `usedReference` | Reference[] | Items used |
| `usedCode` | CodeableConcept[] | Coded items used |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=proc-001` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Procedure code | `code=http://snomed.info/sct\|80146002` |
| `status` | token | Procedure status | `status=completed` |
| `date` | date | Procedure date | `date=2024-01-15` |
| `category` | token | Category | `category=387713003` |
| `performer` | reference | Performer reference | `performer=Practitioner/456` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/789` |

## Examples

### Create a Procedure

```bash
curl -X POST http://localhost:8080/baseR4/Procedure \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Procedure",
    "status": "completed",
    "category": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "387713003",
        "display": "Surgical procedure"
      }]
    },
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "80146002",
        "display": "Appendectomy"
      }],
      "text": "Laparoscopic appendectomy"
    },
    "subject": {
      "reference": "Patient/patient-001"
    },
    "encounter": {
      "reference": "Encounter/encounter-001"
    },
    "performedDateTime": "2024-01-15T14:30:00Z",
    "performer": [{
      "function": {
        "coding": [{
          "system": "http://snomed.info/sct",
          "code": "304292004",
          "display": "Surgeon"
        }]
      },
      "actor": {
        "reference": "Practitioner/practitioner-001",
        "display": "Dr. Jane Smith"
      }
    }],
    "location": {
      "reference": "Location/or-001",
      "display": "Operating Room 1"
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "74400008",
        "display": "Acute appendicitis"
      }]
    }],
    "bodySite": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "66754008",
        "display": "Appendix"
      }]
    }],
    "outcome": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "385669000",
        "display": "Successful"
      }]
    },
    "note": [{
      "text": "Uncomplicated laparoscopic appendectomy. Patient tolerated procedure well."
    }]
  }'
```

### Search Procedures

```bash
# By patient
curl "http://localhost:8080/baseR4/Procedure?patient=Patient/123"

# By code
curl "http://localhost:8080/baseR4/Procedure?code=http://snomed.info/sct|80146002"

# By status
curl "http://localhost:8080/baseR4/Procedure?status=completed"

# By date
curl "http://localhost:8080/baseR4/Procedure?date=2024-01-15"

# Combined: patient's completed surgical procedures
curl "http://localhost:8080/baseR4/Procedure?patient=Patient/123&status=completed&category=387713003"
```

### With _include

```bash
# Include patient
curl "http://localhost:8080/baseR4/Procedure?_include=Procedure:patient"

# Include performer
curl "http://localhost:8080/baseR4/Procedure?_include=Procedure:performer"

# Include encounter
curl "http://localhost:8080/baseR4/Procedure?_include=Procedure:encounter"
```

### Patient Compartment

```bash
# Get all procedures for a patient
curl "http://localhost:8080/baseR4/Patient/123/Procedure"

# Completed procedures only
curl "http://localhost:8080/baseR4/Patient/123/Procedure?status=completed"
```

## Generator

The `ProcedureGenerator` creates synthetic Procedure resources with:

- Common medical and surgical procedures
- SNOMED CT procedure codes
- Appropriate performers and locations
- Realistic outcomes

### Usage

```python
from fhir_cql.server.generator import ProcedureGenerator

generator = ProcedureGenerator(seed=42)

# Generate a random procedure
procedure = generator.generate(
    patient_ref="Patient/123",
    practitioner_ref="Practitioner/456"
)

# Generate batch
procedures = generator.generate_batch(
    count=5,
    patient_ref="Patient/123"
)
```

## Procedure Status

| Code | Display | Description |
|------|---------|-------------|
| preparation | Preparation | Being prepared |
| in-progress | In Progress | Currently in progress |
| not-done | Not Done | Was not performed |
| on-hold | On Hold | Temporarily suspended |
| stopped | Stopped | Ended prematurely |
| completed | Completed | Successfully finished |
| entered-in-error | Entered in Error | Data entry error |
| unknown | Unknown | Status unknown |

## Categories (SNOMED CT)

| Code | Display |
|------|---------|
| 387713003 | Surgical procedure |
| 103693007 | Diagnostic procedure |
| 363679005 | Imaging procedure |
| 409063005 | Counseling |
| 409073007 | Education |
| 182832007 | Management procedure |

## Common Procedure Codes (SNOMED CT)

| Code | Display |
|------|---------|
| 80146002 | Appendectomy |
| 234336002 | Laparoscopic cholecystectomy |
| 36969009 | Cesarean section |
| 65200003 | Biopsy |
| 76164006 | Joint replacement |
| 44558001 | Coronary artery bypass |
| 287664005 | Hip replacement |
| 302497006 | Knee replacement |
| 173422009 | Tonsillectomy |
| 90470006 | Mastectomy |

## Performer Function Codes

| Code | Display |
|------|---------|
| 304292004 | Surgeon |
| 158965000 | Anesthesiologist |
| 224535009 | Registered nurse |
| 224571005 | Nurse practitioner |
| 307988006 | Surgical technician |
