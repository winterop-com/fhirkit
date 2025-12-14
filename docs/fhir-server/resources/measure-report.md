# MeasureReport

## Overview

The MeasureReport resource contains the results of evaluating a Measure against a specific subject (patient) or population. It captures population counts, measure scores, and references to the resources used in the calculation.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/measurereport.html](https://hl7.org/fhir/R4/measurereport.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | complete, pending, error |
| `type` | code | individual, subject-list, summary, data-collection |
| `measure` | canonical | Reference to the Measure being reported |
| `subject` | Reference(Patient) | Who the report is for (individual reports) |
| `date` | dateTime | When the report was generated |
| `reporter` | Reference(Organization\|Practitioner) | Who is reporting the data |
| `period` | Period | Measurement period |
| `improvementNotation` | CodeableConcept | Increase or decrease indicates improvement |
| `group` | BackboneElement[] | Population results and measure scores |
| `evaluatedResource` | Reference[] | Resources used in the calculation |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `identifier` | token | Business identifier | `identifier=report-123` |
| `status` | token | Report status | `status=complete` |
| `measure` | uri | Measure reference | `measure=http://example.org/Measure/CMS123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `date` | date | Report date | `date=ge2024-01-01` |
| `reporter` | reference | Reporter reference | `reporter=Organization/org-1` |
| `period` | date | Measurement period | `period=ge2024-01-01` |
| `evaluated-resource` | reference | Evaluated resource | `evaluated-resource=Observation/456` |

## Examples

### Create an Individual MeasureReport

```bash
curl -X POST http://localhost:8080/baseR4/MeasureReport \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MeasureReport",
    "status": "complete",
    "type": "individual",
    "measure": "http://example.org/fhir/Measure/DiabetesHbA1c",
    "subject": {"reference": "Patient/patient-001"},
    "date": "2024-06-15T10:30:00Z",
    "reporter": {"reference": "Organization/org-001"},
    "period": {
      "start": "2024-01-01",
      "end": "2024-06-30"
    },
    "improvementNotation": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation",
        "code": "decrease",
        "display": "Decreased score indicates improvement"
      }]
    },
    "group": [{
      "population": [
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "initial-population"
            }]
          },
          "count": 1
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "denominator"
            }]
          },
          "count": 1
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "numerator"
            }]
          },
          "count": 0
        }
      ],
      "measureScore": {
        "value": 0.0
      }
    }]
  }'
```

### Create a Summary MeasureReport

```bash
curl -X POST http://localhost:8080/baseR4/MeasureReport \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MeasureReport",
    "status": "complete",
    "type": "summary",
    "measure": "http://example.org/fhir/Measure/DiabetesHbA1c",
    "date": "2024-06-15T10:30:00Z",
    "reporter": {"reference": "Organization/org-001"},
    "period": {
      "start": "2024-01-01",
      "end": "2024-06-30"
    },
    "group": [{
      "population": [
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "initial-population"
            }]
          },
          "count": 500
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "denominator"
            }]
          },
          "count": 450
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "numerator"
            }]
          },
          "count": 380
        }
      ],
      "measureScore": {
        "value": 0.8444
      }
    }]
  }'
```

### Search MeasureReports

```bash
# By patient
curl "http://localhost:8080/baseR4/MeasureReport?patient=Patient/123"

# By measure
curl "http://localhost:8080/baseR4/MeasureReport?measure=http://example.org/Measure/DiabetesHbA1c"

# Complete reports
curl "http://localhost:8080/baseR4/MeasureReport?status=complete"

# By date range
curl "http://localhost:8080/baseR4/MeasureReport?date=ge2024-01-01"

# Combined
curl "http://localhost:8080/baseR4/MeasureReport?patient=Patient/123&status=complete"
```

## Generator

The `MeasureReportGenerator` creates synthetic MeasureReport resources with:

- Individual and summary report types
- Realistic population counts
- Calculated measure scores
- Measurement periods

### Usage

```python
from fhir_cql.server.generator import MeasureReportGenerator

generator = MeasureReportGenerator(seed=42)

# Generate any report
report = generator.generate(
    measure_ref="http://example.org/fhir/Measure/DiabetesHbA1c",
    patient_ref="Patient/123",
    reporter_ref="Organization/org-1"
)

# Generate individual patient report
individual = generator.generate_individual_report(
    measure_ref="http://example.org/fhir/Measure/DiabetesHbA1c",
    patient_ref="Patient/123",
    period_start="2024-01-01",
    period_end="2024-06-30"
)

# Generate population summary report
summary = generator.generate_summary_report(
    measure_ref="http://example.org/fhir/Measure/DiabetesHbA1c",
    reporter_ref="Organization/org-1"
)

# Generate batch for multiple patients
reports = generator.generate_batch(
    count=10,
    measure_ref="http://example.org/fhir/Measure/DiabetesHbA1c",
    patient_refs=["Patient/1", "Patient/2", "Patient/3"]
)
```

## Report Types

| Code | Display | Description |
|------|---------|-------------|
| individual | Individual | Report for a single patient |
| subject-list | Subject List | Report with list of subjects meeting criteria |
| summary | Summary | Aggregate report for a population |
| data-collection | Data Collection | Report for data collection purposes |

## Status Codes

| Code | Description |
|------|-------------|
| complete | Report is complete and ready for use |
| pending | Report is being generated |
| error | An error occurred during generation |

## Understanding Measure Scores

### Proportion Measures

For proportion measures, the score is calculated as:

```
measureScore = numerator / denominator
```

Example: If 380 out of 450 patients met the quality criteria:
- Denominator: 450
- Numerator: 380
- Measure Score: 0.8444 (84.44%)

### Individual vs Summary Reports

**Individual Reports** (type=individual):
- Report for a single patient
- Counts are typically 0 or 1
- Score is 0 (not in numerator) or 1 (in numerator)
- Includes `subject` reference to the patient

**Summary Reports** (type=summary):
- Aggregate report for a population
- Counts represent number of patients
- Score is the percentage/ratio
- No `subject` reference (population-level)

## Patient Compartment

MeasureReport is part of the Patient compartment when it has a `subject` reference. This means:

```bash
# Get all measure reports for a patient
curl "http://localhost:8080/baseR4/Patient/123/MeasureReport"

# Included in $everything
curl "http://localhost:8080/baseR4/Patient/123/$everything"
```
