# Observation

## Overview

The Observation resource represents measurements, simple assertions, and other observations about a patient. This includes vital signs, laboratory results, imaging reports, clinical findings, and social history observations.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/observation.html](https://hl7.org/fhir/R4/observation.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `basedOn` | Reference(ServiceRequest)[] | Fulfills plan or order |
| `partOf` | Reference[] | Part of another observation/procedure |
| `status` | code | registered, preliminary, final, amended, etc. |
| `category` | CodeableConcept[] | vital-signs, laboratory, etc. |
| `code` | CodeableConcept | What was observed (LOINC) |
| `subject` | Reference(Patient) | Patient observed |
| `focus` | Reference[] | Focus of observation |
| `encounter` | Reference(Encounter) | Healthcare event |
| `effective[x]` | dateTime, Period, Timing, instant | When observed |
| `issued` | instant | When result was available |
| `performer` | Reference[] | Who performed observation |
| `value[x]` | Quantity, CodeableConcept, string, boolean, integer, Range, Ratio, SampledData, time, dateTime, Period | Result value |
| `dataAbsentReason` | CodeableConcept | Why result is missing |
| `interpretation` | CodeableConcept[] | High, low, normal, etc. |
| `note` | Annotation[] | Comments |
| `bodySite` | CodeableConcept | Body site |
| `method` | CodeableConcept | Method used |
| `specimen` | Reference(Specimen) | Specimen analyzed |
| `device` | Reference(Device) | Device used |
| `referenceRange` | BackboneElement[] | Reference ranges |
| `hasMember` | Reference(Observation)[] | Component observations |
| `derivedFrom` | Reference[] | Source data |
| `component` | BackboneElement[] | Component results |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=obs-001` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Observation code | `code=http://loinc.org\|85354-9` |
| `category` | token | Category | `category=vital-signs` |
| `status` | token | Status | `status=final` |
| `date` | date | Effective date | `date=2024-01-15` |
| `value-quantity` | quantity | Numeric value | `value-quantity=120` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/456` |

## Examples

### Create a Blood Pressure Observation

```bash
curl -X POST http://localhost:8080/baseR4/Observation \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Observation",
    "status": "final",
    "category": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "vital-signs",
        "display": "Vital Signs"
      }]
    }],
    "code": {
      "coding": [{
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure panel"
      }]
    },
    "subject": {
      "reference": "Patient/patient-001"
    },
    "effectiveDateTime": "2024-01-15T10:30:00Z",
    "component": [
      {
        "code": {
          "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
          }]
        },
        "valueQuantity": {
          "value": 120,
          "unit": "mmHg",
          "system": "http://unitsofmeasure.org",
          "code": "mm[Hg]"
        }
      },
      {
        "code": {
          "coding": [{
            "system": "http://loinc.org",
            "code": "8462-4",
            "display": "Diastolic blood pressure"
          }]
        },
        "valueQuantity": {
          "value": 80,
          "unit": "mmHg",
          "system": "http://unitsofmeasure.org",
          "code": "mm[Hg]"
        }
      }
    ]
  }'
```

### Create a Lab Result

```bash
curl -X POST http://localhost:8080/baseR4/Observation \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Observation",
    "status": "final",
    "category": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "laboratory",
        "display": "Laboratory"
      }]
    }],
    "code": {
      "coding": [{
        "system": "http://loinc.org",
        "code": "4548-4",
        "display": "Hemoglobin A1c"
      }]
    },
    "subject": {
      "reference": "Patient/patient-001"
    },
    "effectiveDateTime": "2024-01-15T08:00:00Z",
    "valueQuantity": {
      "value": 7.2,
      "unit": "%",
      "system": "http://unitsofmeasure.org",
      "code": "%"
    },
    "interpretation": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "H",
        "display": "High"
      }]
    }],
    "referenceRange": [{
      "low": {"value": 4.0, "unit": "%"},
      "high": {"value": 5.6, "unit": "%"},
      "text": "Normal: 4.0-5.6%"
    }]
  }'
```

### Search Observations

```bash
# By patient
curl "http://localhost:8080/baseR4/Observation?patient=Patient/123"

# By code (LOINC)
curl "http://localhost:8080/baseR4/Observation?code=http://loinc.org|4548-4"

# By category
curl "http://localhost:8080/baseR4/Observation?category=vital-signs"

# Lab results
curl "http://localhost:8080/baseR4/Observation?category=laboratory"

# By date range
curl "http://localhost:8080/baseR4/Observation?date=ge2024-01-01&date=le2024-01-31"

# Combined: patient's recent vital signs
curl "http://localhost:8080/baseR4/Observation?patient=Patient/123&category=vital-signs&date=ge2024-01-01"
```

### Patient Compartment

```bash
# Get all observations for a patient
curl "http://localhost:8080/baseR4/Patient/123/Observation"

# Vital signs only
curl "http://localhost:8080/baseR4/Patient/123/Observation?category=vital-signs"

# Lab results only
curl "http://localhost:8080/baseR4/Patient/123/Observation?category=laboratory"
```

## Generator

The `ObservationGenerator` creates synthetic Observation resources with:

- Vital signs (blood pressure, heart rate, temperature, etc.)
- Lab results with realistic values
- Appropriate LOINC codes
- Reference ranges and interpretations

### Usage

```python
from fhirkit.server.generator import ObservationGenerator

generator = ObservationGenerator(seed=42)

# Generate a random observation
observation = generator.generate(
    patient_ref="Patient/123"
)

# Generate batch
observations = generator.generate_batch(
    count=10,
    patient_ref="Patient/123"
)
```

## Observation Status

| Code | Display | Description |
|------|---------|-------------|
| registered | Registered | Existence known, no result |
| preliminary | Preliminary | Preliminary result |
| final | Final | Final result |
| amended | Amended | Result amended |
| corrected | Corrected | Result corrected |
| cancelled | Cancelled | Observation cancelled |
| entered-in-error | Entered in Error | Data entry error |
| unknown | Unknown | Status unknown |

## Categories

| Code | Display |
|------|---------|
| vital-signs | Vital Signs |
| laboratory | Laboratory |
| imaging | Imaging |
| procedure | Procedure |
| survey | Survey |
| exam | Exam |
| therapy | Therapy |
| activity | Activity |
| social-history | Social History |

## Common LOINC Codes

### Vital Signs

| Code | Display |
|------|---------|
| 85354-9 | Blood pressure panel |
| 8480-6 | Systolic blood pressure |
| 8462-4 | Diastolic blood pressure |
| 8867-4 | Heart rate |
| 8310-5 | Body temperature |
| 9279-1 | Respiratory rate |
| 59408-5 | Oxygen saturation |
| 29463-7 | Body weight |
| 8302-2 | Body height |
| 39156-5 | Body mass index |

### Laboratory

| Code | Display |
|------|---------|
| 4548-4 | Hemoglobin A1c |
| 2339-0 | Glucose |
| 2085-9 | HDL Cholesterol |
| 2089-1 | LDL Cholesterol |
| 2093-3 | Total Cholesterol |
| 2571-8 | Triglycerides |
| 718-7 | Hemoglobin |
| 789-8 | Red blood cell count |
| 6690-2 | White blood cell count |
| 777-3 | Platelet count |

## Interpretation Codes

| Code | Display | Description |
|------|---------|-------------|
| H | High | Above normal range |
| L | Low | Below normal range |
| N | Normal | Within normal range |
| HH | Critical High | Critically high |
| LL | Critical Low | Critically low |
| A | Abnormal | Abnormal |
