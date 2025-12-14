# Measure Evaluation Guide

This guide covers clinical quality measure (CQM) evaluation using the FHIR CQL library. You'll learn how to define CQL-based quality measures, evaluate them against patient populations, and generate FHIR MeasureReport resources.

## Introduction

### What are Clinical Quality Measures?

Clinical Quality Measures (CQMs) are tools that help measure and track the quality of healthcare services. They quantify healthcare processes, outcomes, patient perceptions, and organizational structure using standardized criteria.

**Electronic Clinical Quality Measures (eCQMs)** are CQMs specified in a standardized electronic format:
- Logic is expressed using **CQL (Clinical Quality Language)**
- Data is retrieved from **FHIR** resources
- Results are reported as **FHIR MeasureReport** resources

### Measure Structure

A typical quality measure consists of:

| Component | Description |
|-----------|-------------|
| **Initial Population** | All patients eligible for the measure |
| **Denominator** | Subset of initial population meeting specific criteria |
| **Denominator Exclusions** | Patients removed from denominator (optional) |
| **Denominator Exceptions** | Patients with valid exceptions (optional) |
| **Numerator** | Patients meeting the quality goal |
| **Numerator Exclusions** | Patients removed from numerator (optional) |
| **Stratifiers** | Categories for breaking down results |

### Scoring Types

The library supports four measure scoring types:

| Type | Formula | Use Case |
|------|---------|----------|
| **Proportion** | Numerator / Denominator | Percentage of patients meeting criteria |
| **Ratio** | Numerator / Denominator | Rate comparisons |
| **Continuous Variable** | Aggregate function | Statistical measures |
| **Cohort** | Count only | Headcounts |

---

## Quick Start

### Basic Measure Evaluation

```python
from fhirkit.engine.cql import MeasureEvaluator

# Create the evaluator
evaluator = MeasureEvaluator()

# Load a CQL measure
evaluator.load_measure("""
    library DiabetesMeasure version '1.0'
    using FHIR version '4.0.1'

    context Patient

    define "Initial Population":
        AgeInYears() >= 18

    define "Denominator":
        "Initial Population"

    define "Numerator":
        AgeInYears() >= 40
""")

# Define patient data
patients = [
    {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"},
    {"resourceType": "Patient", "id": "p2", "birthDate": "1970-05-15"},
    {"resourceType": "Patient", "id": "p3", "birthDate": "1985-08-22"},
]

# Evaluate the measure
report = evaluator.evaluate_population(patients)

# View results
for group in report.groups:
    print(f"Initial Population: {group.populations['initial-population'].count}")
    print(f"Denominator: {group.populations['denominator'].count}")
    print(f"Numerator: {group.populations['numerator'].count}")
    if group.measure_score is not None:
        print(f"Score: {group.measure_score:.2%}")
```

### CLI Measure Command

The fastest way to evaluate a measure from the command line:

```bash
# Evaluate measure against a patient file
fhir cql measure measure.cql --data patient.json

# Evaluate against multiple patients in a directory
fhir cql measure measure.cql --patients ./patients/

# Evaluate against a FHIR bundle
fhir cql measure measure.cql --data patient-bundle.json

# Save the report as FHIR MeasureReport JSON
fhir cql measure measure.cql --data bundle.json --output report.json

# Show detailed results with stratifiers
fhir cql measure measure.cql --data bundle.json --verbose
```

---

## CLI Reference

### fhir cql measure

Evaluate a CQL quality measure against patient data.

```bash
fhir cql measure <measure-file> [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `measure-file` | Path to CQL measure file |

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--data` | `-d` | JSON data file (Patient or Bundle) |
| `--patients` | `-p` | Directory with patient JSON files |
| `--output` | `-o` | Output file for FHIR MeasureReport |
| `--verbose` | `-v` | Show detailed results including stratifiers |

**Examples:**

```bash
# Basic evaluation with single patient
fhir cql measure diabetes_measure.cql --data patient.json

# Evaluate population from directory
fhir cql measure diabetes_measure.cql --patients ./patient-data/

# Process a FHIR bundle and export report
fhir cql measure diabetes_measure.cql --data population.json -o report.json

# Verbose output with stratification details
fhir cql measure diabetes_measure.cql -d bundle.json -v
```

**Output Example:**

```
Measure: diabetes_measure.cql
Evaluating 100 patient(s)...

                  Group: default
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Population              ┃                 Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ initial-population      │                   100 │
│ denominator             │                    85 │
│ denominator-exclusion   │                     5 │
│ numerator               │                    60 │
│ Score                   │               75.00%  │
└─────────────────────────┴───────────────────────┘
```

---

## Writing CQL Measures

### Measure Structure

A CQL measure library follows a standard pattern with well-known definition names:

```cql
library DiabetesHbA1cMeasure version '1.0.0'

using FHIR version '4.0.1'

// Code systems and value sets
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED": 'http://snomed.info/sct'

valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'
valueset "HbA1c Lab Test": 'http://example.org/fhir/ValueSet/hba1c'

// Measurement period parameter
parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// ============================================================
// POPULATIONS
// ============================================================

// Initial Population: Who is eligible for this measure?
define "Initial Population":
    exists([Condition: "Diabetes"] C
        where C.clinicalStatus ~ 'active')

// Denominator: Same as initial population (or more restrictive)
define "Denominator":
    "Initial Population"

// Denominator Exclusions: Who should be removed from denominator?
define "Denominator Exclusion":
    AgeInYears() > 85

// Numerator: Who meets the quality goal?
define "Numerator":
    exists("Most Recent HbA1c" H
        where H.value < 8 '%')

// ============================================================
// SUPPORTING DEFINITIONS
// ============================================================

define "Most Recent HbA1c":
    Last([Observation: "HbA1c Lab Test"] O
        where O.effective during "Measurement Period"
        sort by effective)

// ============================================================
// STRATIFIERS
// ============================================================

define "Stratifier Age Group":
    if AgeInYears() < 40 then 'Under 40'
    else if AgeInYears() < 65 then '40-64'
    else '65+'
```

### Population Definition Names

The `MeasureEvaluator` automatically detects populations using standard naming conventions:

| Population Type | Recognized Names |
|-----------------|------------------|
| Initial Population | `Initial Population`, `InitialPopulation`, `initial-population` |
| Denominator | `Denominator`, `denominator` |
| Denominator Exclusion | `Denominator Exclusion`, `DenominatorExclusion`, `denominator-exclusion` |
| Denominator Exception | `Denominator Exception`, `DenominatorException`, `denominator-exception` |
| Numerator | `Numerator`, `numerator` |
| Numerator Exclusion | `Numerator Exclusion`, `NumeratorExclusion`, `numerator-exclusion` |
| Measure Population | `Measure Population`, `MeasurePopulation`, `measure-population` |
| Measure Observation | `Measure Observation`, `MeasureObservation`, `measure-observation` |

### Stratifier Detection

Stratifiers are automatically detected by name patterns:
- Definitions starting with `Stratifier` (e.g., `Stratifier Age Group`)
- Definitions containing `Stratification` (e.g., `Stratification by Gender`)

---

## Measure Components

### Initial Population

The initial population defines all patients eligible for the measure:

```cql
// Age-based eligibility
define "Initial Population":
    AgeInYears() >= 18 and AgeInYears() <= 85

// Condition-based eligibility
define "Initial Population":
    exists([Condition: "Diabetes"] C
        where C.clinicalStatus ~ 'active'
            and C.verificationStatus ~ 'confirmed')

// Encounter-based eligibility
define "Initial Population":
    exists([Encounter] E
        where E.period during "Measurement Period"
            and E.status = 'finished')
```

### Denominator

The denominator is typically the initial population or a subset:

```cql
// Same as initial population
define "Denominator":
    "Initial Population"

// More restrictive
define "Denominator":
    "Initial Population"
        and exists("Qualifying Encounter")
```

### Denominator Exclusions

Patients with valid reasons for exclusion from the quality calculation:

```cql
define "Denominator Exclusion":
    // Hospice patients
    exists([Encounter: "Hospice Encounter"] H
        where H.period overlaps "Measurement Period")
    or
    // Terminal illness
    exists([Condition: "Terminal Illness"])
    or
    // Age exclusions
    AgeInYears() > 85
```

### Denominator Exceptions

Patients with valid clinical exceptions (different from exclusions):

```cql
define "Denominator Exception":
    // Medical reason documented
    exists([Observation: "Medical Exception"] O
        where O.effective during "Measurement Period")
    or
    // Patient refused
    exists([Observation: "Patient Refusal"])
```

### Numerator

Patients meeting the quality goal:

```cql
// Lab result-based
define "Numerator":
    exists("Most Recent HbA1c" H
        where H.value < 8.0 '%')

// Procedure-based
define "Numerator":
    exists([Procedure: "Screening Procedure"] P
        where P.performed during "Measurement Period")

// Medication-based
define "Numerator":
    exists([MedicationRequest: "Statin Therapy"] M
        where M.authoredOn during "Measurement Period")
```

### Stratifiers

Break down results by patient characteristics:

```cql
// Age stratification
define "Stratifier Age Group":
    case
        when AgeInYears() in Interval[18, 44] then '18-44'
        when AgeInYears() in Interval[45, 64] then '45-64'
        when AgeInYears() >= 65 then '65+'
        else 'Unknown'
    end

// Gender stratification
define "Stratifier Gender":
    Patient.gender

// Condition-based stratification
define "Stratifier Disease Severity":
    if exists([Condition: "Severe Diabetes"]) then 'Severe'
    else if exists([Condition: "Moderate Diabetes"]) then 'Moderate'
    else 'Mild'
```

---

## Scoring Types

### Proportion Measures

Most common type - calculates a percentage:

```python
from fhirkit.engine.cql import MeasureEvaluator, MeasureScoring

evaluator = MeasureEvaluator()
evaluator.set_scoring(MeasureScoring.PROPORTION)  # Default
evaluator.load_measure(cql_source)

report = evaluator.evaluate_population(patients)
# Score = Numerator / (Denominator - Exclusions - Exceptions)
```

**Formula:**

```
Score = (Numerator - Numerator Exclusions) /
        (Denominator - Denominator Exclusions - Denominator Exceptions)
```

### Ratio Measures

Compares two independent populations:

```python
evaluator.set_scoring(MeasureScoring.RATIO)
```

### Continuous Variable Measures

Statistical aggregation (mean, median, etc.):

```python
evaluator.set_scoring(MeasureScoring.CONTINUOUS_VARIABLE)
```

Requires a `Measure Observation` definition that returns a numeric value.

### Cohort Measures

Simple patient counts:

```python
evaluator.set_scoring(MeasureScoring.COHORT)
```

No score calculated - just population counts.

---

## Python API

### MeasureEvaluator Class

The main class for measure evaluation:

```python
from fhirkit.engine.cql import (
    CQLEvaluator,
    InMemoryDataSource,
    MeasureEvaluator,
    MeasureScoring,
    PopulationType,
)

# Create with defaults
evaluator = MeasureEvaluator()

# Create with existing CQL evaluator
cql = CQLEvaluator()
evaluator = MeasureEvaluator(cql_evaluator=cql)

# Create with data source
data_source = InMemoryDataSource()
evaluator = MeasureEvaluator(data_source=data_source)
```

### Loading Measures

```python
# From CQL string
library = evaluator.load_measure("""
    library MyMeasure version '1.0'

    define "Initial Population":
        true
""")

# From file
library = evaluator.load_measure_file("path/to/measure.cql")

# Access loaded library
print(evaluator.library.name)  # "MyMeasure"
print(evaluator.library.version)  # "1.0"
```

### Manual Population Configuration

Override automatic detection:

```python
# Add population manually
evaluator.add_population(
    pop_type=PopulationType.INITIAL_POPULATION,
    definition="MyInitialPop",  # CQL definition name
    group_id="group1"
)

evaluator.add_population(
    pop_type=PopulationType.NUMERATOR,
    definition="MyNumerator",
    group_id="group1"
)

# Add stratifier
evaluator.add_stratifier(
    definition="AgeGroup",
    group_id="group1"
)
```

### Setting Scoring Type

```python
from fhirkit.engine.cql import MeasureScoring

evaluator.set_scoring(MeasureScoring.PROPORTION)  # Default
evaluator.set_scoring(MeasureScoring.RATIO)
evaluator.set_scoring(MeasureScoring.CONTINUOUS_VARIABLE)
evaluator.set_scoring(MeasureScoring.COHORT)
```

### Single Patient Evaluation

```python
patient = {
    "resourceType": "Patient",
    "id": "patient-123",
    "birthDate": "1970-05-15",
    "gender": "male"
}

result = evaluator.evaluate_patient(patient)

# Access results
print(f"Patient ID: {result.patient_id}")
print(f"In Initial Population: {result.populations['initial-population']}")
print(f"In Numerator: {result.populations['numerator']}")

# Stratifier values
for strat_name, value in result.stratifier_values.items():
    print(f"{strat_name}: {value}")
```

### Population Evaluation

```python
patients = [
    {"resourceType": "Patient", "id": "p1", "birthDate": "1970-01-01"},
    {"resourceType": "Patient", "id": "p2", "birthDate": "1985-06-15"},
    {"resourceType": "Patient", "id": "p3", "birthDate": "1950-03-22"},
]

report = evaluator.evaluate_population(patients)

# Access report metadata
print(f"Measure: {report.measure_id}")
print(f"Evaluated at: {report.evaluated_at}")
print(f"Period: {report.period_start} to {report.period_end}")

# Access group results
for group in report.groups:
    print(f"\nGroup: {group.id}")

    # Population counts
    for pop_type, pop_count in group.populations.items():
        print(f"  {pop_type}: {pop_count.count}")
        # Optional: list of patient IDs
        # print(f"    Patients: {pop_count.patients}")

    # Measure score
    if group.measure_score is not None:
        print(f"  Score: {group.measure_score:.2%}")

    # Stratified results
    for strat_name, strat_results in group.stratifiers.items():
        print(f"\n  Stratifier: {strat_name}")
        for stratum in strat_results:
            print(f"    {stratum.value}:")
            for pop_type, count in stratum.populations.items():
                print(f"      {pop_type}: {count.count}")
```

### Population Summary

Get a simplified summary dictionary:

```python
report = evaluator.evaluate_population(patients)
summary = evaluator.get_population_summary(report)

print(summary)
# {
#     "measure": "DiabetesMeasure",
#     "total_patients": 100,
#     "groups": [
#         {
#             "id": "default",
#             "populations": {
#                 "initial-population": 100,
#                 "denominator": 85,
#                 "numerator": 60
#             },
#             "measure_score": 0.7059
#         }
#     ]
# }
```

### Converting to FHIR MeasureReport

```python
report = evaluator.evaluate_population(patients)

# Convert to FHIR MeasureReport resource
fhir_report = report.to_fhir()

import json
print(json.dumps(fhir_report, indent=2, default=str))
```

**Output:**

```json
{
  "resourceType": "MeasureReport",
  "status": "complete",
  "type": "summary",
  "measure": "DiabetesMeasure",
  "date": "2024-01-15T10:30:00",
  "period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-12-31T23:59:59"
  },
  "group": [
    {
      "id": "default",
      "population": [
        {
          "code": {"coding": [{"code": "initial-population"}]},
          "count": 100
        },
        {
          "code": {"coding": [{"code": "denominator"}]},
          "count": 85
        },
        {
          "code": {"coding": [{"code": "numerator"}]},
          "count": 60
        }
      ],
      "measureScore": {"value": 0.7059},
      "stratifier": [
        {
          "code": [{"text": "Age Group"}],
          "stratum": [
            {
              "value": {"text": "18-44"},
              "population": [
                {"code": {"coding": [{"code": "initial-population"}]}, "count": 30}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Data Classes Reference

### PopulationType Enum

```python
from fhirkit.engine.cql import PopulationType

PopulationType.INITIAL_POPULATION      # "initial-population"
PopulationType.DENOMINATOR             # "denominator"
PopulationType.DENOMINATOR_EXCLUSION   # "denominator-exclusion"
PopulationType.DENOMINATOR_EXCEPTION   # "denominator-exception"
PopulationType.NUMERATOR               # "numerator"
PopulationType.NUMERATOR_EXCLUSION     # "numerator-exclusion"
PopulationType.MEASURE_POPULATION      # "measure-population"
PopulationType.MEASURE_POPULATION_EXCLUSION  # "measure-population-exclusion"
PopulationType.MEASURE_OBSERVATION     # "measure-observation"
```

### MeasureScoring Enum

```python
from fhirkit.engine.cql import MeasureScoring

MeasureScoring.PROPORTION          # "proportion"
MeasureScoring.RATIO               # "ratio"
MeasureScoring.CONTINUOUS_VARIABLE # "continuous-variable"
MeasureScoring.COHORT              # "cohort"
```

### PatientResult

Result of evaluating a single patient:

```python
from fhirkit.engine.cql.measure import PatientResult

result = PatientResult(
    patient_id="p1",
    populations={
        "initial-population": True,
        "denominator": True,
        "numerator": False
    },
    observations={},
    stratifier_values={"Age Group": "40-64"}
)
```

### MeasureReport

Aggregated results for a population:

```python
from fhirkit.engine.cql.measure import MeasureReport

report = MeasureReport(
    measure_id="DiabetesMeasure",
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 12, 31),
    groups=[...],
    patient_results=[...],
    evaluated_at=datetime.now()
)
```

### GroupResult

Results for a measure group:

```python
from fhirkit.engine.cql.measure import GroupResult, PopulationCount

group = GroupResult(
    id="default",
    populations={
        "initial-population": PopulationCount(
            type=PopulationType.INITIAL_POPULATION,
            count=100,
            patients=["p1", "p2", ...]
        )
    },
    stratifiers={},
    measure_score=0.75
)
```

---

## Integration with Data Sources

### Using InMemoryDataSource

```python
from fhirkit.engine.cql import InMemoryDataSource, MeasureEvaluator

# Create data source with test data
data_source = InMemoryDataSource()

# Add patients
patients = []
for i in range(10):
    patient = {
        "resourceType": "Patient",
        "id": f"patient-{i}",
        "birthDate": f"{1960 + i * 5}-06-15"
    }
    data_source.add_resource(patient)
    patients.append(patient)

# Add conditions for some patients
data_source.add_resource({
    "resourceType": "Condition",
    "id": "cond-1",
    "subject": {"reference": "Patient/patient-1"},
    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}
})

# Create evaluator with data source
evaluator = MeasureEvaluator(data_source=data_source)
evaluator.load_measure(measure_cql)

# Evaluate
report = evaluator.evaluate_population(patients, data_source=data_source)
```

### Using with FHIR Server

```python
from fhirkit.server.storage import FHIRStore
from fhirkit.engine.cql import MeasureEvaluator

# Get patients from FHIR store
store = FHIRStore()
# ... load data ...

patients = store.search("Patient", {})

# Create evaluator and evaluate
evaluator = MeasureEvaluator()
evaluator.load_measure_file("measure.cql")
report = evaluator.evaluate_population(patients)
```

---

## Example Measures

### Diabetes HbA1c Control

```cql
library DiabetesHbA1c version '1.0.0'
using FHIR version '4.0.1'

codesystem "LOINC": 'http://loinc.org'

valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'
valueset "HbA1c": 'http://example.org/fhir/ValueSet/hba1c'

parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// Patients 18-75 with diabetes
define "Initial Population":
    AgeInYears() >= 18 and AgeInYears() <= 75
    and exists([Condition: "Diabetes"] C
        where C.clinicalStatus ~ 'active')

define "Denominator":
    "Initial Population"

// Exclude hospice patients
define "Denominator Exclusion":
    exists([Encounter: "Hospice"])

// HbA1c less than 8%
define "Numerator":
    "Most Recent HbA1c".value < 8.0 '%'

define "Most Recent HbA1c":
    Last([Observation: "HbA1c"] O
        where O.effective during "Measurement Period"
        sort by effective)

// Age stratification
define "Stratifier Age":
    case
        when AgeInYears() < 40 then '18-39'
        when AgeInYears() < 65 then '40-64'
        else '65-75'
    end
```

### Preventive Care Screening

```cql
library PreventiveScreening version '1.0.0'
using FHIR version '4.0.1'

valueset "Colonoscopy": 'http://example.org/fhir/ValueSet/colonoscopy'

parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// Adults 50-75
define "Initial Population":
    AgeInYears() >= 50 and AgeInYears() <= 75

define "Denominator":
    "Initial Population"

// Had colonoscopy in past 10 years
define "Numerator":
    exists([Procedure: "Colonoscopy"] P
        where P.performed ends during
            Interval[start of "Measurement Period" - 10 years,
                     end of "Measurement Period"])

define "Stratifier Risk Level":
    if exists([Condition: "High Risk Condition"]) then 'High Risk'
    else 'Average Risk'
```

### Medication Adherence

```cql
library MedicationAdherence version '1.0.0'
using FHIR version '4.0.1'

valueset "Statin Medications": 'http://example.org/fhir/ValueSet/statins'
valueset "Cardiovascular Disease": 'http://example.org/fhir/ValueSet/cvd'

parameter "Measurement Period" Interval<DateTime>

context Patient

// Adults with cardiovascular disease
define "Initial Population":
    AgeInYears() >= 21
    and exists([Condition: "Cardiovascular Disease"])

define "Denominator":
    "Initial Population"

// Exception: documented allergy or intolerance
define "Denominator Exception":
    exists([AllergyIntolerance: "Statin Medications"])

// Currently on statin therapy
define "Numerator":
    exists([MedicationRequest: "Statin Medications"] M
        where M.status = 'active'
            and M.authoredOn during "Measurement Period")
```

---

## Troubleshooting

### Common Issues

**No populations detected:**
```python
evaluator.load_measure(cql_source)
print(evaluator._groups)  # Empty?
```

Ensure your CQL uses recognized population names (e.g., `"Initial Population"`, not `"IP"`).

**Score is None:**
- Check that denominator count > 0 after exclusions
- Verify scoring type is set correctly
- Ensure numerator definition returns boolean

**Patient not in population:**
```python
# Debug single patient
result = evaluator.evaluate_patient(patient)
print(result.populations)  # Check which populations are True/False
```

**Stratifier values are None:**
- Verify stratifier definition returns a value for all patients
- Check for edge cases that might return null

### Performance Tips

1. **Batch processing**: Evaluate populations rather than individual patients
2. **Data source optimization**: Use `InMemoryDataSource` for repeated evaluations
3. **Limit stratifiers**: Only add stratifiers you need in the report
4. **Measurement period**: Ensure your period parameter is properly constrained

---

## Best Practices

### Measure Design

1. **Clear population definitions**: Make Initial Population inclusive, then narrow with Denominator
2. **Document exclusions**: Use Denominator Exclusion for valid clinical reasons
3. **Use exceptions sparingly**: Denominator Exception is for individual patient circumstances
4. **Test edge cases**: Include patients at age boundaries, with missing data, etc.

### CQL Style

```cql
// Good: Named definitions for reuse
define "Active Diabetes":
    exists([Condition: "Diabetes"] C
        where C.clinicalStatus ~ 'active')

define "Initial Population":
    AgeInYears() >= 18 and "Active Diabetes"

// Good: Measurement period filtering
define "Qualifying Encounters":
    [Encounter] E
        where E.period during "Measurement Period"

// Good: Explicit null handling
define "Has Recent HbA1c":
    "Most Recent HbA1c" is not null
        and "Most Recent HbA1c".value is not null
```

### Testing

```python
def test_measure_populations():
    """Test all population combinations."""
    evaluator = MeasureEvaluator()
    evaluator.load_measure(MEASURE_CQL)

    # Test: In all populations
    result1 = evaluator.evaluate_patient(in_numerator_patient)
    assert result1.populations["numerator"] is True

    # Test: In denominator but not numerator
    result2 = evaluator.evaluate_patient(not_in_numerator_patient)
    assert result2.populations["denominator"] is True
    assert result2.populations["numerator"] is False

    # Test: Excluded
    result3 = evaluator.evaluate_patient(excluded_patient)
    assert result3.populations["denominator-exclusion"] is True
```

---

## See Also

- [CQL Tutorial](cql-tutorial.md) - CQL language basics
- [CQL Python API](cql-api.md) - CQL evaluator reference
- [Data Sources Guide](datasources-guide.md) - Working with FHIR data
- [FHIR Server Guide](fhir-server-guide.md) - Using the built-in FHIR server
