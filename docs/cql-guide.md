# CQL Complete Guide

A comprehensive guide to CQL (Clinical Quality Language) - from beginner to expert.

## What is CQL?

CQL (Clinical Quality Language) is a domain-specific language for expressing clinical logic. It's designed for:

- **Quality measures** - Calculate quality metrics across patient populations
- **Clinical decision support** - Trigger alerts and recommendations
- **Research protocols** - Define cohorts and eligibility criteria
- **Data extraction** - Query clinical data with complex logic

### CQL vs FHIRPath

| Feature | FHIRPath | CQL |
|---------|----------|-----|
| Expression only | Yes | No (library structure) |
| Reusable definitions | No | Yes |
| User-defined functions | No | Yes |
| Complex queries | Limited | Yes |
| Terminology support | No | Yes |
| Quality measures | No | Yes |
| Temporal reasoning | Limited | Full |

**Use FHIRPath when**: You need to extract or validate data from a single resource.

**Use CQL when**: You need reusable logic, complex queries, quality measures, or clinical decision support.

---

## Getting Started

### Your First CQL Expression

```bash
# Simple expression evaluation
fhir cql eval "1 + 2 * 3"
# Result: 7

fhir cql eval "Upper('hello world')"
# Result: 'HELLO WORLD'

fhir cql eval "Today() + 30 days"
# Result: @2025-01-15 (date 30 days from now)
```

### Your First CQL Library

CQL code is organized into **libraries**:

```cql
library HelloWorld version '1.0'

define Greeting: 'Hello, CQL!'
define Sum: 1 + 2 + 3
define Today: Today()
```

Run it:

```bash
fhir cql run examples/cql/01_hello_world.cql
```

---

## Library Structure

Every CQL library has a standard structure:

```cql
// 1. Library declaration (required)
library MyLibrary version '1.0'

// 2. Data model (optional)
using FHIR version '4.0.1'

// 3. Library includes (optional)
include FHIRHelpers version '4.0.1'

// 4. Parameters (optional)
parameter "Measurement Period" Interval<DateTime>

// 5. Terminology (optional)
codesystem "LOINC": 'http://loinc.org'
valueset "Diabetes": 'http://example.org/vs/diabetes'

// 6. Context (optional)
context Patient

// 7. Definitions (the main logic)
define PatientAge: AgeInYears()
define IsAdult: PatientAge >= 18
```

### Library Declaration

Every library needs a name:

```cql
library MyLibrary version '1.0'
```

The version is optional but recommended for production use.

### Using Data Models

The `using` statement specifies the data model:

```cql
using FHIR version '4.0.1'
```

This enables FHIR-specific features like resource retrieval.

### Including Other Libraries

Reuse logic from other libraries:

```cql
include FHIRHelpers version '4.0.1'
include MyCommonFunctions version '1.0' called Common
```

Use an alias (`called Common`) for shorter references.

### Parameters

Parameters allow runtime configuration:

```cql
parameter "Measurement Period" Interval<DateTime>
parameter "Age Threshold" Integer default 18
```

### Context

The context defines the scope:

```cql
context Patient      // Most common - patient-centric
context Practitioner // Practitioner-centric
context Unfiltered   // No automatic filtering
```

---

## Definitions

Definitions are named expressions - the building blocks of CQL.

### Basic Definitions

```cql
// Literal values
define Greeting: 'Hello, World!'
define Answer: 42
define Pi: 3.14159

// Calculations
define Sum: 1 + 2 + 3
define Product: 4 * 5
define Average: (10 + 20 + 30) / 3
```

### Referencing Other Definitions

Definitions can reference each other:

```cql
define A: 10
define B: 20
define Sum: A + B           // 30
define Product: A * B       // 200
define Ratio: A / B         // 0.5
```

### Clinical Definitions

```cql
context Patient

define PatientAge: AgeInYears()

define IsAdult: PatientAge >= 18

define IsSenior: PatientAge >= 65

define AgeCategory:
    case
        when PatientAge < 18 then 'Pediatric'
        when PatientAge < 65 then 'Adult'
        else 'Senior'
    end
```

---

## Data Types

### Primitive Types

| Type | Examples |
|------|----------|
| Boolean | `true`, `false` |
| Integer | `42`, `-7`, `0` |
| Decimal | `3.14`, `0.5` |
| String | `'Hello'`, `"World"` |
| Date | `@2024-01-15` |
| DateTime | `@2024-01-15T10:30:00` |
| Time | `@T10:30:00` |

### Collections (Lists)

```cql
define Numbers: {1, 2, 3, 4, 5}
define Names: {'Alice', 'Bob', 'Charlie'}
define Empty: {}
```

### Intervals

Intervals represent ranges:

```cql
// Closed interval [1, 10] - includes both endpoints
define ClosedInterval: Interval[1, 10]

// Open interval (1, 10) - excludes both endpoints
define OpenInterval: Interval(1, 10)

// Half-open intervals
define LeftOpen: Interval(1, 10]   // excludes 1, includes 10
define RightOpen: Interval[1, 10)  // includes 1, excludes 10

// Date intervals
define Year2024: Interval[@2024-01-01, @2024-12-31]
```

Access interval properties with dot notation:

```cql
define Low: Interval[1, 10].low           // 1
define High: Interval[1, 10].high         // 10
define IsLowClosed: Interval[1, 10].lowClosed   // true
define IsHighClosed: Interval[1, 10].highClosed // true
```

### Tuples

Tuples are structured data:

```cql
define Person: Tuple { name: 'John', age: 30, active: true }

// Access properties
define PersonName: Person.name    // 'John'
define PersonAge: Person.age      // 30
```

### Quantities

Quantities have a value and unit:

```cql
define Weight: 70 'kg'
define Height: 175 'cm'
define Temperature: 98.6 '[degF]'

// Quantity arithmetic
define TotalWeight: 70 'kg' + 5 'kg'  // 75 'kg'
```

---

## Functions

### Built-in Functions

CQL provides many built-in functions:

**String Functions**
```cql
Upper('hello')              // 'HELLO'
Lower('HELLO')              // 'hello'
Length('hello')             // 5
Substring('hello', 0, 2)    // 'he'
StartsWith('hello', 'he')   // true
EndsWith('hello', 'lo')     // true
Matches('hello', '^h.*o$')  // true
```

**Math Functions**
```cql
Abs(-5)                     // 5
Ceiling(4.2)                // 5
Floor(4.8)                  // 4
Round(3.14159, 2)           // 3.14
Power(2, 8)                 // 256
Ln(2.71828)                 // ~1.0
Exp(1)                      // ~2.718
```

**Date/Time Functions**
```cql
Today()                     // Current date
Now()                       // Current datetime
AgeInYears()                // Patient's age
years between @1990-01-01 and Today()
```

**Aggregate Functions**
```cql
Count({1, 2, 3})            // 3
Sum({1, 2, 3, 4, 5})        // 15
Avg({2, 4, 6})              // 4
Min({5, 2, 8})              // 2
Max({5, 2, 8})              // 8
```

**Quantity and Unit Conversion (UCUM)**

Convert between units using the UCUM (Unified Code for Units of Measure) standard:

```cql
// Mass conversions
ConvertQuantity(1 'g', 'mg')           // 1000 'mg'
ConvertQuantity(500 'mg', 'g')         // 0.5 'g'
ConvertQuantity(150 '[lb_av]', 'kg')   // 68.04 'kg'

// Volume conversions
ConvertQuantity(1 'L', 'mL')           // 1000 'mL'
ConvertQuantity(500 'mL', 'L')         // 0.5 'L'

// Temperature conversions
ConvertQuantity(98.6 '[degF]', 'Cel')  // 37.0 'Cel'
ConvertQuantity(37 'Cel', '[degF]')    // 98.6 '[degF]'
ConvertQuantity(0 'Cel', 'K')          // 273.15 'K'

// Length conversions
ConvertQuantity(70 '[in_i]', 'cm')     // 177.8 'cm'
ConvertQuantity(1 '[ft_i]', 'm')       // 0.3048 'm'

// Compound units (concentrations)
ConvertQuantity(180 'mg/dL', 'mg/L')   // 1800 'mg/L'
```

Supported unit categories:
- **Mass**: g, mg, kg, ug, ng, [lb_av], [oz_av]
- **Volume**: L, mL, dL, uL, [gal_us], [foz_us]
- **Length**: m, cm, mm, km, [in_i], [ft_i], [mi_i]
- **Temperature**: Cel (Celsius), [degF] (Fahrenheit), K (Kelvin)
- **Time**: s, min, h, d, wk, mo, a (year)
- **Concentration**: mg/dL, mmol/L, g/L, etc.

### User-Defined Functions

Create reusable functions:

```cql
// Simple function
define function Double(x Integer) returns Integer:
    x * 2

// Function with multiple parameters
define function Add(a Integer, b Integer) returns Integer:
    a + b

// Function with null handling
define function SafeDivide(num Decimal, denom Decimal) returns Decimal:
    if denom is null or denom = 0 then null
    else num / denom

// Clinical function
define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
    if weightKg is null or heightCm is null or heightCm = 0 then null
    else Round(weightKg / Power(heightCm / 100, 2), 1)

// Using functions
define BMI: CalculateBMI(70.0, 175.0)  // ~22.9
```

---

## Queries

Queries filter and transform collections.

### Basic Query Syntax

```cql
// Query syntax: (source) alias where condition return expression
define Adults:
    (Patients) P
    where P.age >= 18
    return P
```

### Query on Lists

List literals require parentheses:

```cql
// Filter a list
define LargeNumbers:
    ({1, 2, 3, 4, 5, 6, 7, 8, 9, 10}) N
    where N > 5
    return N
// Result: {6, 7, 8, 9, 10}

// Transform a list
define Doubled:
    ({1, 2, 3}) N
    return N * 2
// Result: {2, 4, 6}

// Filter and transform
define LargeDoubled:
    ({1, 2, 3, 4, 5}) N
    where N > 2
    return N * 2
// Result: {6, 8, 10}
```

### FHIR Resource Queries

Query FHIR resources:

```cql
context Patient

// Get all conditions
define AllConditions: [Condition]

// Filter by status
define ActiveConditions:
    [Condition] C
    where C.clinicalStatus.coding.code = 'active'

// Get observations with specific code
define BloodPressures:
    [Observation: code in "Blood Pressure Codes"]

// Complex filtering
define RecentActiveConditions:
    [Condition] C
    where C.clinicalStatus.coding.code = 'active'
        and C.recordedDate during "Measurement Period"
```

### Query Clauses

**let** - Define intermediate values:
```cql
define ConditionsWithAge:
    [Condition] C
    let onset: C.onset as FHIR.dateTime
    where onset is not null
    return Tuple { condition: C, onsetDate: onset }
```

**sort** - Order results:
```cql
define SortedObservations:
    [Observation] O
    return O
    sort by effective desc
```

**aggregate** - Aggregate results:
```cql
define TotalValue:
    ({1, 2, 3, 4, 5}) N
    aggregate sum starting 0: sum + N
// Result: 15
```

---

## Terminology

CQL has built-in support for clinical terminology.

### Code Systems and Codes

```cql
// Define code systems
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "ICD10": 'http://hl7.org/fhir/sid/icd-10-cm'

// Define individual codes
code "Glucose": '2339-0' from "LOINC" display 'Glucose [Mass/volume] in Blood'
code "Diabetes": '44054006' from "SNOMED" display 'Type 2 diabetes mellitus'
```

### Value Sets

```cql
// Reference external value sets
valueset "Diabetes Codes": 'http://example.org/fhir/ValueSet/diabetes'
valueset "HbA1c": 'http://example.org/fhir/ValueSet/hba1c'

// Use in queries
define DiabetesConditions:
    [Condition: code in "Diabetes Codes"]

define HbA1cTests:
    [Observation: code in "HbA1c"]
```

### Code Comparisons

```cql
define HasDiabetes:
    exists([Condition] C where C.code ~ "Diabetes")

define IsGlucoseTest:
    Observation.code ~ "Glucose"
```

---

## Temporal Operations

CQL excels at date/time logic.

### Date Arithmetic

```cql
define Today: Today()
define Tomorrow: Today() + 1 day
define NextWeek: Today() + 7 days
define LastMonth: Today() - 1 month
define NextYear: Today() + 1 year
```

### Duration Calculations

```cql
define PatientAge: years between Patient.birthDate and Today()

define DaysSinceOnset:
    days between Condition.onset and Today()

define MonthsOnMedication:
    months between MedicationRequest.authoredOn and Today()
```

### Interval Operations

```cql
define MeasurementPeriod: Interval[@2024-01-01, @2024-12-31]

// Check if date is in interval
define InPeriod: Today() in MeasurementPeriod

// Check if intervals overlap
define PeriodsOverlap:
    Interval[@2024-01-01, @2024-06-30] overlaps Interval[@2024-04-01, @2024-09-30]

// Get interval boundaries
define PeriodStart: start of MeasurementPeriod
define PeriodEnd: end of MeasurementPeriod
```

### Temporal Comparisons

```cql
// Same day comparison
define SameDay: date1 same day as date2

// Before/after
define Before: date1 before date2
define After: date1 after date2

// During
define DuringPeriod: Observation.effective during MeasurementPeriod
```

---

## Quality Measures

CQL is designed for clinical quality measures.

### Measure Populations

```cql
library DiabetesMeasure version '1.0'
using FHIR version '4.0.1'

parameter "Measurement Period" Interval<DateTime>

context Patient

// Initial Population - who is eligible?
define "Initial Population":
    AgeInYears() >= 18

// Denominator - who is in the measure?
define "Denominator":
    "Initial Population"
        and exists([Condition: code in "Diabetes Codes"])

// Denominator Exclusions - who should be excluded?
define "Denominator Exclusions":
    exists([Condition: code in "Hospice Codes"])

// Numerator - who met the measure?
define "Numerator":
    exists(
        [Observation: code in "HbA1c Codes"] O
        where O.effective during "Measurement Period"
            and O.value < 9 '%'
    )
```

### Running Measures

```bash
# Evaluate a measure
fhir cql measure examples/cql/08_quality_measure.cql --data patient.json

# Evaluate for population
fhir cql measure measure.cql --data patients/
```

---

## Python API

### Basic Usage

```python
from fhirkit.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()

# Evaluate expression
result = evaluator.evaluate_expression("1 + 2 * 3")  # 7

# Compile and run library
lib = evaluator.compile("""
    library Example version '1.0'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, CQL!'
""")

sum_result = evaluator.evaluate_definition("Sum")  # 6
greeting = evaluator.evaluate_definition("Greeting")  # 'Hello, CQL!'
```

### With Patient Data

```python
evaluator = CQLEvaluator()

lib = evaluator.compile("""
    library PatientLib version '1.0'
    using FHIR version '4.0.1'
    context Patient
    define PatientAge: years between Patient.birthDate and Today()
    define IsAdult: PatientAge >= 18
""")

patient = {
    "resourceType": "Patient",
    "birthDate": "1990-05-15",
    "gender": "male"
}

age = evaluator.evaluate_definition("PatientAge", resource=patient)
is_adult = evaluator.evaluate_definition("IsAdult", resource=patient)
```

See the [CQL API](cql-api.md) for complete API documentation.

---

## CLI Reference

### Expression Evaluation

```bash
# Evaluate expression
fhir cql eval "1 + 2 * 3"
fhir cql eval "Today() + 30 days"
fhir cql eval "Upper('hello')"
```

### Library Operations

```bash
# Run a library
fhir cql run library.cql

# Run specific definition
fhir cql run library.cql --definition Sum

# Run with patient data
fhir cql run library.cql --data patient.json
```

### Validation

```bash
# Check library syntax
fhir cql check library.cql

# Validate multiple files
fhir cql validate *.cql

# Show AST
fhir cql ast library.cql
```

### Interactive REPL

```bash
# Start interactive mode
fhir cql repl
```

See the [CLI Reference](cli.md) for complete CLI documentation.

---

## Next Steps

- [CQL Tutorial](cql-tutorial.md) - Step-by-step hands-on learning
- [CQL API](cql-api.md) - Complete Python API reference
- [CQL Reference](fhirpath-cql-tutorial.md) - Expression deep dive
- [Measure Guide](measure-guide.md) - Quality measure evaluation
- [Data Sources](datasources-guide.md) - FHIR data integration
