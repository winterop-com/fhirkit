# Measure

## Overview

The Measure resource represents a computable definition of a health-related measure, such as an electronic Clinical Quality Measure (eCQM). It defines what data should be collected and how to calculate the measure score.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/measure.html](https://hl7.org/fhir/R4/measure.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `url` | uri | Canonical identifier for this measure |
| `identifier` | Identifier[] | Business identifiers |
| `version` | string | Business version |
| `name` | string | Computer-friendly name |
| `title` | string | Human-friendly title |
| `status` | code | draft, active, retired, unknown |
| `experimental` | boolean | For testing purposes only |
| `date` | dateTime | Date last changed |
| `publisher` | string | Publishing organization |
| `description` | markdown | Natural language description |
| `purpose` | markdown | Why this measure is defined |
| `effectivePeriod` | Period | When the measure is valid |
| `library` | canonical[] | CQL Library references |
| `scoring` | CodeableConcept | proportion, ratio, continuous-variable, cohort |
| `type` | CodeableConcept[] | process, outcome, structure, etc. |
| `improvementNotation` | CodeableConcept | increase or decrease indicates improvement |
| `group` | BackboneElement[] | Population groups and stratifiers |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `url` | uri | Canonical URL | `url=http://example.org/Measure/cms123` |
| `name` | string | Computer-friendly name | `name=CMS123` |
| `title` | string | Human-friendly title | `title=Diabetes` |
| `status` | token | Status | `status=active` |
| `version` | token | Version | `version=1.0.0` |
| `identifier` | token | Business identifier | `identifier=CMS123` |
| `description` | string | Text search in description | `description=blood%20pressure` |
| `publisher` | string | Publisher name | `publisher=CMS` |
| `date` | date | Publication date | `date=ge2024-01-01` |
| `effective` | date | Effective period | `effective=ge2024-01-01` |
| `topic` | token | Topic code | `topic=treatment` |

## Examples

### Create a Measure

```bash
curl -X POST http://localhost:8080/baseR4/Measure \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Measure",
    "url": "http://example.org/fhir/Measure/DiabetesHbA1c",
    "name": "DiabetesHbA1cControl",
    "title": "Diabetes: Hemoglobin A1c Poor Control",
    "status": "active",
    "date": "2024-01-01",
    "publisher": "Example Healthcare",
    "description": "Percentage of patients with diabetes who had HbA1c > 9%",
    "library": ["http://example.org/fhir/Library/DiabetesHbA1c"],
    "scoring": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/measure-scoring",
        "code": "proportion",
        "display": "Proportion"
      }]
    },
    "type": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/measure-type",
        "code": "outcome",
        "display": "Outcome"
      }]
    }],
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
          "criteria": {
            "language": "text/cql-identifier",
            "expression": "InitialPopulation"
          }
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "denominator"
            }]
          },
          "criteria": {
            "language": "text/cql-identifier",
            "expression": "Denominator"
          }
        },
        {
          "code": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/measure-population",
              "code": "numerator"
            }]
          },
          "criteria": {
            "language": "text/cql-identifier",
            "expression": "Numerator"
          }
        }
      ]
    }]
  }'
```

### Search Measures

```bash
# By status
curl "http://localhost:8080/baseR4/Measure?status=active"

# By name
curl "http://localhost:8080/baseR4/Measure?name=Diabetes"

# By URL
curl "http://localhost:8080/baseR4/Measure?url=http://example.org/fhir/Measure/DiabetesHbA1c"

# By type (outcome measures)
curl "http://localhost:8080/baseR4/Measure?topic=outcome"

# Active measures by publisher
curl "http://localhost:8080/baseR4/Measure?status=active&publisher=CMS"
```

## Generator

The `MeasureGenerator` creates synthetic Measure resources with:

- Realistic eCQM-style definitions
- Proportion, ratio, and cohort scoring types
- Population definitions (initial-population, numerator, denominator)
- CQL library references

### Usage

```python
from fhir_cql.server.generator import MeasureGenerator

generator = MeasureGenerator(seed=42)

# Generate any measure
measure = generator.generate(
    library_ref="http://example.org/fhir/Library/DiabetesLib"
)

# Generate proportion measure
proportion = generator.generate_proportion_measure(
    name="DiabetesControl",
    title="Diabetes HbA1c Control"
)

# Generate outcome measure
outcome = generator.generate_outcome_measure(
    name="BloodPressureControl",
    title="Controlling High Blood Pressure"
)

# Generate batch
measures = generator.generate_batch(count=10)
```

## Scoring Types

| Code | Display | Description |
|------|---------|-------------|
| proportion | Proportion | Numerator / Denominator |
| ratio | Ratio | Numerator / Denominator (different populations) |
| continuous-variable | Continuous Variable | Statistical measure of observations |
| cohort | Cohort | Count of population meeting criteria |

## Measure Types

| Code | Display | Description |
|------|---------|-------------|
| process | Process | Measures healthcare processes |
| outcome | Outcome | Measures health outcomes |
| structure | Structure | Measures structural capabilities |
| patient-reported-outcome | Patient Reported Outcome | Patient-reported measures |
| composite | Composite | Combines multiple measures |

## Population Codes

| Code | Display |
|------|---------|
| initial-population | Initial Population |
| numerator | Numerator |
| numerator-exclusion | Numerator Exclusion |
| denominator | Denominator |
| denominator-exclusion | Denominator Exclusion |
| denominator-exception | Denominator Exception |
| measure-population | Measure Population |
| measure-observation | Measure Observation |

## Integration with CQL

Measures typically reference CQL libraries for their population criteria:

```json
{
  "library": ["http://example.org/fhir/Library/DiabetesLib"],
  "group": [{
    "population": [{
      "criteria": {
        "language": "text/cql-identifier",
        "expression": "InitialPopulation"
      }
    }]
  }]
}
```

The referenced CQL library would define:

```cql
define "InitialPopulation":
  [Patient] P
    where P.age >= 18
      and exists [Condition: "Diabetes"]
```
