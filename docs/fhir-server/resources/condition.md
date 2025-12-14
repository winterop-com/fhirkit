# Condition

## Overview

The Condition resource represents a clinical condition, problem, diagnosis, or other event, situation, issue, or clinical concept that has risen to a level of concern. Conditions can be current, historical, or anticipated.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/condition.html](https://hl7.org/fhir/R4/condition.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `clinicalStatus` | CodeableConcept | active, recurrence, relapse, inactive, remission, resolved |
| `verificationStatus` | CodeableConcept | unconfirmed, provisional, differential, confirmed, refuted, entered-in-error |
| `category` | CodeableConcept[] | problem-list-item, encounter-diagnosis, etc. |
| `severity` | CodeableConcept | Subjective severity |
| `code` | CodeableConcept | Diagnosis code (ICD-10, SNOMED CT) |
| `bodySite` | CodeableConcept[] | Anatomical location |
| `subject` | Reference(Patient) | Patient who has the condition |
| `encounter` | Reference(Encounter) | Encounter when recorded |
| `onset[x]` | dateTime, Age, Period, Range, string | When condition began |
| `abatement[x]` | dateTime, Age, Period, Range, string | When condition resolved |
| `recordedDate` | dateTime | Date recorded |
| `recorder` | Reference(Practitioner) | Who recorded the condition |
| `asserter` | Reference | Who asserted the condition |
| `stage` | BackboneElement[] | Stage/grade |
| `evidence` | BackboneElement[] | Supporting evidence |
| `note` | Annotation[] | Additional notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=cond-001` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Diagnosis code | `code=http://snomed.info/sct\|73211009` |
| `clinical-status` | token | Clinical status | `clinical-status=active` |
| `verification-status` | token | Verification status | `verification-status=confirmed` |
| `category` | token | Category | `category=problem-list-item` |
| `onset-date` | date | Onset date | `onset-date=ge2024-01-01` |
| `severity` | token | Severity | `severity=24484000` |

## Examples

### Create a Condition

```bash
curl -X POST http://localhost:8080/baseR4/Condition \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Condition",
    "clinicalStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active",
        "display": "Active"
      }]
    },
    "verificationStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "confirmed",
        "display": "Confirmed"
      }]
    },
    "category": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
        "code": "problem-list-item",
        "display": "Problem List Item"
      }]
    }],
    "severity": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "6736007",
        "display": "Moderate"
      }]
    },
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "73211009",
        "display": "Diabetes mellitus"
      }],
      "text": "Type 2 Diabetes Mellitus"
    },
    "subject": {
      "reference": "Patient/patient-001"
    },
    "onsetDateTime": "2020-03-15",
    "recordedDate": "2024-01-15T10:30:00Z"
  }'
```

### Search Conditions

```bash
# By patient
curl "http://localhost:8080/baseR4/Condition?patient=Patient/123"

# By diagnosis code
curl "http://localhost:8080/baseR4/Condition?code=http://snomed.info/sct|73211009"

# By clinical status
curl "http://localhost:8080/baseR4/Condition?clinical-status=active"

# Active confirmed conditions
curl "http://localhost:8080/baseR4/Condition?clinical-status=active&verification-status=confirmed"

# Problem list items
curl "http://localhost:8080/baseR4/Condition?category=problem-list-item"
```

### With _include

```bash
# Include patient
curl "http://localhost:8080/baseR4/Condition?_include=Condition:patient"

# Include encounter
curl "http://localhost:8080/baseR4/Condition?_include=Condition:encounter"
```

### Patient Compartment

```bash
# Get all conditions for a patient
curl "http://localhost:8080/baseR4/Patient/123/Condition"

# Active conditions only
curl "http://localhost:8080/baseR4/Patient/123/Condition?clinical-status=active"
```

## Generator

The `ConditionGenerator` creates synthetic Condition resources with:

- Common chronic and acute conditions
- Appropriate SNOMED CT codes
- Realistic onset dates and clinical statuses
- Abatement dates for resolved conditions

### Usage

```python
from fhirkit.server.generator import ConditionGenerator

generator = ConditionGenerator(seed=42)

# Generate a random condition
condition = generator.generate(
    patient_ref="Patient/123"
)

# Generate batch
conditions = generator.generate_batch(
    count=5,
    patient_ref="Patient/123"
)
```

## Clinical Status

| Code | Display | Description |
|------|---------|-------------|
| active | Active | Currently active |
| recurrence | Recurrence | Condition has recurred |
| relapse | Relapse | Condition has relapsed |
| inactive | Inactive | Not currently active |
| remission | Remission | In remission |
| resolved | Resolved | Condition has resolved |

## Verification Status

| Code | Display | Description |
|------|---------|-------------|
| unconfirmed | Unconfirmed | Not yet confirmed |
| provisional | Provisional | Provisional diagnosis |
| differential | Differential | Differential diagnosis |
| confirmed | Confirmed | Confirmed diagnosis |
| refuted | Refuted | Refuted diagnosis |
| entered-in-error | Entered in Error | Data entry error |

## Common Condition Codes (SNOMED CT)

| Code | Display |
|------|---------|
| 73211009 | Diabetes mellitus |
| 38341003 | Hypertensive disorder |
| 195967001 | Asthma |
| 84114007 | Heart failure |
| 13645005 | Chronic obstructive lung disease |
| 40930008 | Hypothyroidism |
| 35489007 | Depressive disorder |
| 271737000 | Anemia |
| 396275006 | Osteoarthritis |
| 56265001 | Heart disease |

## Severity Codes (SNOMED CT)

| Code | Display |
|------|---------|
| 255604002 | Mild |
| 6736007 | Moderate |
| 24484000 | Severe |
