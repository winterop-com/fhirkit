# ImmunizationEvaluation

## Overview

An ImmunizationEvaluation represents the evaluation of a patient's immunization status against a specific set of recommendations. It determines whether administered doses are valid according to clinical guidelines and vaccination schedules.

This resource is used to assess whether a patient has received valid immunizations and what additional doses may be needed to complete a series.

**Common use cases:**
- Vaccination series validation
- Dose validity assessment
- Immunization compliance checking
- School/work immunization verification
- Travel immunization assessment

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/immunizationevaluation.html](https://hl7.org/fhir/R4/immunizationevaluation.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | completed, entered-in-error |
| `patient` | Reference(Patient) | Patient being evaluated |
| `date` | dateTime | Evaluation date |
| `authority` | Reference(Organization) | Evaluating authority |
| `targetDisease` | CodeableConcept | Disease being evaluated for |
| `immunizationEvent` | Reference(Immunization) | Immunization being evaluated |
| `doseStatus` | CodeableConcept | Valid or not valid |
| `doseStatusReason` | CodeableConcept[] | Reason for status |
| `doseNumberPositiveInt` | positiveInt | Dose number |
| `seriesDosesPositiveInt` | positiveInt | Total doses in series |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=eval-001` |
| `identifier` | token | Business identifier | `identifier=EVAL-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Evaluation status | `status=completed` |
| `date` | date | Evaluation date | `date=2024-01-15` |
| `immunization-event` | reference | Immunization reference | `immunization-event=Immunization/imm-001` |
| `target-disease` | token | Target disease | `target-disease=14189004` |
| `dose-status` | token | Dose validity status | `dose-status=valid` |

## Examples

### Create an ImmunizationEvaluation

```bash
curl -X POST http://localhost:8080/baseR4/ImmunizationEvaluation \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ImmunizationEvaluation",
    "identifier": [{
      "system": "http://hospital.example.org/evaluations",
      "value": "EVAL-2024-001"
    }],
    "status": "completed",
    "patient": {"reference": "Patient/123"},
    "date": "2024-01-15T10:00:00Z",
    "authority": {"reference": "Organization/cdc"},
    "targetDisease": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "14189004",
        "display": "Measles"
      }]
    },
    "immunizationEvent": {"reference": "Immunization/imm-001"},
    "doseStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/immunization-evaluation-dose-status",
        "code": "valid",
        "display": "Valid"
      }]
    },
    "doseNumberPositiveInt": 1,
    "seriesDosesPositiveInt": 2
  }'
```

### Search ImmunizationEvaluations

```bash
# By patient
curl "http://localhost:8080/baseR4/ImmunizationEvaluation?patient=Patient/123"

# By immunization event
curl "http://localhost:8080/baseR4/ImmunizationEvaluation?immunization-event=Immunization/imm-001"

# By dose status
curl "http://localhost:8080/baseR4/ImmunizationEvaluation?dose-status=valid"
```

## Generator Usage

```python
from fhirkit.server.generator import ImmunizationEvaluationGenerator

generator = ImmunizationEvaluationGenerator(seed=42)

# Generate a random evaluation
evaluation = generator.generate()

# Generate for specific patient
patient_eval = generator.generate(
    patient_reference="Patient/123",
    immunization_reference="Immunization/imm-001"
)

# Generate batch
evaluations = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| completed | Evaluation is complete |
| entered-in-error | Entered in error |

## Dose Status Codes

| Code | Description |
|------|-------------|
| valid | Dose is valid |
| notvalid | Dose is not valid |

## Related Resources

- [Immunization](./immunization.md) - The administered immunization
- [ImmunizationRecommendation](./immunization-recommendation.md) - Related recommendations
- [Patient](./patient.md) - Patient being evaluated
