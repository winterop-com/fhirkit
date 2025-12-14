# $evaluate-measure Operation

## Overview

The `$evaluate-measure` operation evaluates a clinical quality measure against patient data using CQL (Clinical Quality Language) and returns a MeasureReport resource with population counts and measure scores.

## FHIR Specification

See: [FHIR R4 Measure/$evaluate-measure](https://hl7.org/fhir/R4/measure-operation-evaluate-measure.html)

## Endpoints

```
GET  /Measure/{id}/$evaluate-measure
POST /Measure/{id}/$evaluate-measure
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `subject` | reference | Patient reference (e.g., `Patient/123`) or Group reference |
| `periodStart` | date | Start of measurement period (YYYY-MM-DD) |
| `periodEnd` | date | End of measurement period (YYYY-MM-DD) |
| `reportType` | code | Type of report: `individual`, `subject-list`, or `summary` |

## How It Works

1. The server retrieves the Measure resource by ID
2. Resolves the associated Library resource containing CQL
3. Extracts and compiles the CQL source code
4. Evaluates the measure against each patient in scope
5. Aggregates results and calculates measure scores
6. Returns a FHIR MeasureReport resource

## Prerequisites

Before using `$evaluate-measure`, you need:

1. **Measure resource** - Defines the quality measure with:
   - Reference to a Library containing CQL
   - Scoring type (proportion, ratio, etc.)
   - Population definitions (initial population, denominator, numerator)

2. **Library resource** - Contains the CQL logic:
   - Base64-encoded CQL in `content[].data`
   - Content type: `text/cql`

3. **Patient data** - The resources the CQL queries against

## Examples

### Population Summary

Evaluate a measure against all patients:

```bash
curl "http://localhost:8000/Measure/measure-001/$evaluate-measure"
```

### Individual Patient

Evaluate for a specific patient:

```bash
curl "http://localhost:8000/Measure/measure-001/$evaluate-measure?subject=Patient/patient-001&reportType=individual"
```

### With Custom Period

Specify a measurement period:

```bash
curl "http://localhost:8000/Measure/measure-001/$evaluate-measure?periodStart=2024-01-01&periodEnd=2024-06-30"
```

## Response

Returns a MeasureReport resource:

```json
{
  "resourceType": "MeasureReport",
  "id": "generated-uuid",
  "status": "complete",
  "type": "summary",
  "measure": "http://example.org/fhir/Measure/DiabetesHbA1c",
  "period": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "group": [{
    "population": [
      {
        "code": {"coding": [{"code": "initial-population"}]},
        "count": 100
      },
      {
        "code": {"coding": [{"code": "denominator"}]},
        "count": 80
      },
      {
        "code": {"coding": [{"code": "numerator"}]},
        "count": 60
      }
    ],
    "measureScore": {"value": 0.75}
  }],
  "improvementNotation": {
    "coding": [{
      "code": "increase",
      "display": "Increased score indicates improvement"
    }]
  }
}
```

## Scoring Types

The server supports these measure scoring types:

| Type | Description | Score Calculation |
|------|-------------|-------------------|
| `proportion` | Percentage-based measure | (numerator - exclusions) / (denominator - exclusions) |
| `ratio` | Ratio of two counts | numerator / denominator |
| `continuous-variable` | Statistical measure | Observation aggregate |
| `cohort` | Simple population count | No score calculated |

## CQL Requirements

The CQL library must define these populations (names can vary):

```cql
library MyMeasure version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "Initial Population":
    exists([Condition] C where C.clinicalStatus ~ 'active')

define "Denominator":
    "Initial Population"

define "Denominator Exclusions":
    false

define "Numerator":
    exists([Observation] O where O.status = 'final')
```

## Error Handling

| Error | Status | Description |
|-------|--------|-------------|
| Measure not found | 404 | Invalid measure ID |
| No library reference | 400 | Measure has no `library` field |
| Library not found | 400 | Referenced Library doesn't exist |
| No CQL content | 400 | Library has no `text/cql` content |
| CQL compilation error | 400 | Invalid CQL syntax |
| No patients found | 400 | No patients to evaluate |
| Evaluation failure | 500 | Runtime error during evaluation |

## Example Setup

### 1. Create Library

```bash
curl -X PUT "http://localhost:8000/Library/library-test" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Library",
    "id": "library-test",
    "url": "http://example.org/fhir/Library/TestMeasure",
    "status": "active",
    "content": [{
      "contentType": "text/cql",
      "data": "<base64-encoded-cql>"
    }]
  }'
```

### 2. Create Measure

```bash
curl -X PUT "http://localhost:8000/Measure/measure-test" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Measure",
    "id": "measure-test",
    "url": "http://example.org/fhir/Measure/TestMeasure",
    "status": "active",
    "library": ["http://example.org/fhir/Library/TestMeasure"],
    "scoring": {
      "coding": [{"code": "proportion"}]
    }
  }'
```

### 3. Evaluate

```bash
curl "http://localhost:8000/Measure/measure-test/$evaluate-measure"
```

## Limitations

- Group-based evaluation is not yet fully implemented
- Stratifiers are detected but may not be fully populated in results
- Only single-library measures are supported
- Library dependencies are not automatically resolved
