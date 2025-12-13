# FHIRPath and CQL Deep Dive Tutorial

A comprehensive, example-driven guide to FHIRPath and Clinical Quality Language (CQL).

## Table of Contents

1. [Introduction](#introduction)
2. [FHIRPath Basics](#fhirpath-basics)
3. [CQL Fundamentals](#cql-fundamentals)
4. [Working with Data Types](#working-with-data-types)
5. [Lists and Collections](#lists-and-collections)
6. [Date and Time Operations](#date-and-time-operations)
7. [Intervals](#intervals)
8. [Queries](#queries)
9. [Functions](#functions)
10. [Terminology](#terminology)
11. [Clinical Examples](#clinical-examples)

---

## Introduction

### What is FHIRPath?

FHIRPath is a path-based navigation and extraction language for FHIR (Fast Healthcare Interoperability Resources) data. Think of it like XPath for XML, but designed specifically for healthcare data.

### What is CQL?

CQL (Clinical Quality Language) is a domain-specific language for expressing clinical logic. It builds on FHIRPath concepts and adds:
- Library structure with definitions
- Complex queries
- Temporal operations
- Clinical terminology support
- Quality measure calculations

### When to Use Each

| Use Case | FHIRPath | CQL |
|----------|----------|-----|
| Extract data from FHIR resources | Yes | Yes |
| Simple filtering | Yes | Yes |
| Define reusable logic | | Yes |
| Quality measures | | Yes |
| Clinical decision support | | Yes |
| Complex temporal reasoning | | Yes |

---

## FHIRPath Basics

### Navigating Resources

FHIRPath uses dot notation to navigate through resource properties:

```fhirpath
// Start with a Patient resource
Patient.name                    // Get all names
Patient.name.family             // Get all family names
Patient.name.given              // Get all given names (flattened)
Patient.birthDate               // Get birth date
```

### Real Example - Patient Data

Given this Patient resource:
```json
{
  "resourceType": "Patient",
  "id": "example",
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["John", "Robert"]
    }
  ],
  "birthDate": "1990-05-15",
  "gender": "male",
  "address": [
    {
      "city": "Boston",
      "state": "MA",
      "postalCode": "02101"
    }
  ]
}
```

Extract data:
```fhirpath
Patient.name.family              // Returns: ['Smith']
Patient.name.given               // Returns: ['John', 'Robert']
Patient.name.given.first()       // Returns: 'John'
Patient.address.city             // Returns: ['Boston']
Patient.gender                   // Returns: 'male'
```

### Filtering with where()

The `where()` function filters collections:

```fhirpath
// Get official names only
Patient.name.where(use = 'official')

// Get active conditions
Condition.where(clinicalStatus.coding.code = 'active')

// Get observations with specific code
Observation.where(code.coding.code = '2339-0')
```

### Existence Checks

```fhirpath
// Check if patient has any allergies
Patient.extension.where(url = 'allergy').exists()

// Check if value is present
Observation.value.exists()

// Check if collection is empty
Patient.name.empty()
```

### Type Testing

```fhirpath
// Check type
Observation.value is Quantity
Observation.value is string

// Get value as specific type
Observation.value.ofType(Quantity)
```

### String Functions

```fhirpath
// String operations
Patient.name.family.lower()           // 'smith'
Patient.name.family.upper()           // 'SMITH'
Patient.name.family.substring(0, 2)   // 'Sm'

// Pattern matching
Patient.name.family.startsWith('Sm')  // true
Patient.name.family.contains('mit')   // true
Patient.name.family.matches('^[A-Z]') // true
```

### Combining Paths

```fhirpath
// Union - combine results
Patient.name.given | Patient.name.family

// Concatenation
Patient.name.given.first() + ' ' + Patient.name.family
```

---

## CQL Fundamentals

### Library Structure

Every CQL file is a library:

```cql
library MyLibrary version '1.0.0'

using FHIR version '4.0.1'

// Your definitions here
```

### Definitions

Definitions are named expressions:

```cql
library Basics version '1.0.0'

using FHIR version '4.0.1'

// Simple value
define Greeting: 'Hello, World!'

// Arithmetic
define Sum: 1 + 2 + 3          // Returns: 6
define Product: 4 * 5          // Returns: 20
define Division: 10.0 / 3.0    // Returns: 3.333...

// Boolean logic
define IsTrue: true and not false    // Returns: true
define Logic: 5 > 3 and 10 <= 10     // Returns: true

// String concatenation
define FullName: 'John' + ' ' + 'Smith'  // Returns: 'John Smith'
```

### Context

CQL operates within a context (usually Patient):

```cql
library PatientExample version '1.0.0'

using FHIR version '4.0.1'

context Patient

// Now all retrieves are filtered to current patient
define PatientAge:
    years between Patient.birthDate and Today()

define PatientGender:
    Patient.gender
```

### Conditional Logic

```cql
// If-then-else
define AgeCategory:
    if PatientAge < 18 then 'Pediatric'
    else if PatientAge < 65 then 'Adult'
    else 'Geriatric'

// Case expression
define RiskLevel:
    case
        when PatientAge >= 80 then 'Very High'
        when PatientAge >= 65 then 'High'
        when PatientAge >= 45 then 'Moderate'
        else 'Low'
    end
```

### Null Handling (Three-Valued Logic)

CQL uses three-valued logic: `true`, `false`, and `null`:

```cql
// Null propagates
define NullResult: 5 + null           // Returns: null

// Safe operations with null
define SafeValue: Coalesce(null, null, 'default')  // Returns: 'default'

// Null checks
define IsNull: null is null           // Returns: true
define IsNotNull: 5 is not null       // Returns: true

// Boolean with null
define AndWithNull: true and null     // Returns: null
define OrWithNull: true or null       // Returns: true (short-circuit)
```

---

## Working with Data Types

### Primitive Types

```cql
// String (use SINGLE quotes!)
define MyString: 'Hello, World!'

// Integer
define MyInteger: 42

// Decimal
define MyDecimal: 3.14159

// Boolean
define MyBoolean: true

// Null
define MyNull: null
```

### Date and Time

```cql
// Date literal (starts with @)
define MyDate: @2024-06-15

// DateTime literal
define MyDateTime: @2024-06-15T10:30:00

// Time literal
define MyTime: @T14:30:00

// Partial dates
define YearMonth: @2024-06
define YearOnly: @2024

// Current date/time
define CurrentDate: Today()
define CurrentDateTime: Now()
define CurrentTime: TimeOfDay()
```

### Quantity

Quantities have value and unit:

```cql
// Quantity literals
define Weight: 70 'kg'
define Height: 175 'cm'
define Temperature: 98.6 '[degF]'
define Dose: 500 'mg'

// Quantity arithmetic
define BMI: Weight / (Height / 100) ^ 2

// Compare quantities (same units)
define IsHeavy: Weight > 100 'kg'
```

### Interval

Intervals represent ranges:

```cql
// Integer interval (closed = includes endpoints)
define IntInterval: Interval[1, 10]

// Open interval (excludes endpoints)
define OpenInterval: Interval(1, 10)

// Half-open
define HalfOpen: Interval[1, 10)

// Date interval
define MeasurementPeriod: Interval[@2024-01-01, @2024-12-31]
```

### Tuple

Tuples are named property collections:

```cql
// Create tuple
define PersonInfo: Tuple {
    name: 'John Smith',
    age: 45,
    active: true
}

// Access tuple properties
define PersonName: PersonInfo.name
define PersonAge: PersonInfo.age
```

### Code and Concept

```cql
codesystem "LOINC": 'http://loinc.org'

// Single code
code "Glucose": '2339-0' from "LOINC" display 'Glucose [Mass/volume] in Blood'

// Concept (multiple codes)
concept "Diabetes": {
    "Type2DiabetesSNOMED",
    "Type2DiabetesICD10"
} display 'Diabetes Mellitus'
```

### Type Conversion

```cql
// To String
define IntToString: ToString(42)       // '42'
define BoolToString: ToString(true)    // 'true'

// To Integer
define StringToInt: ToInteger('42')    // 42
define DecimalToInt: ToInteger(3.9)    // 3

// To Decimal
define StringToDec: ToDecimal('3.14')  // 3.14

// To Boolean
define StringToBool: ToBoolean('true') // true
define YesToBool: ToBoolean('yes')     // true

// To Date
define StringToDate: ToDate('2024-06-15')
```

---

## Lists and Collections

### Creating Lists

```cql
// Empty list
define EmptyList: {}

// List of integers
define Numbers: {1, 2, 3, 4, 5}

// List of strings (single quotes!)
define Names: {'Alice', 'Bob', 'Charlie'}

// Mixed types (avoid if possible)
define Mixed: {1, 'two', true}
```

### Accessing Elements

```cql
define Numbers: {1, 2, 3, 4, 5}

// First/Last
define FirstNum: First(Numbers)        // 1
define LastNum: Last(Numbers)          // 5

// By index (0-based)
define ThirdNum: Numbers[2]            // 3

// Tail (all except first)
define TailNums: Tail(Numbers)         // {2, 3, 4, 5}

// Take/Skip
define FirstThree: Take(Numbers, 3)    // {1, 2, 3}
define SkipTwo: Skip(Numbers, 2)       // {3, 4, 5}

// Singleton (assert single element)
define OnlyOne: singleton from {42}    // 42
```

### Membership

```cql
// Contains (list contains value)
define HasThree: {1, 2, 3} contains 3  // true

// In (value in list)
define InList: 3 in {1, 2, 3}          // true

// Includes (list contains list)
define HasSubset: {1, 2, 3, 4, 5} includes {2, 3, 4}  // true
```

### Combining Lists

```cql
// Union (combine, remove duplicates)
define Combined: {1, 2, 3} union {3, 4, 5}      // {1, 2, 3, 4, 5}

// Intersect (common elements)
define Common: {1, 2, 3, 4} intersect {2, 3, 5} // {2, 3}

// Except (remove elements)
define Difference: {1, 2, 3, 4} except {2, 4}   // {1, 3}

// Combine (concatenate lists)
define Concat: Combine({1, 2}, {3, 4})          // {1, 2, 3, 4}
```

### Transforming Lists

```cql
// Distinct (remove duplicates)
define Unique: distinct {1, 2, 2, 3, 3, 3}  // {1, 2, 3}

// Flatten (nested to flat)
define Flat: Flatten({{1, 2}, {3, 4}})      // {1, 2, 3, 4}

// Sort
define Sorted: Sort({5, 2, 8, 1})           // {1, 2, 5, 8}
```

### Aggregate Functions

```cql
define Numbers: {1, 2, 3, 4, 5}

define Total: Sum(Numbers)          // 15
define Average: Avg(Numbers)        // 3.0
define Minimum: Min(Numbers)        // 1
define Maximum: Max(Numbers)        // 5
define Count: Count(Numbers)        // 5

// Boolean aggregates
define AllTrue: AllTrue({true, true, true})    // true
define AnyTrue: AnyTrue({false, true, false})  // true
```

---

## Date and Time Operations

### Component Extraction

```cql
define TestDate: @2024-06-15T10:30:45

// Extract parts
define Year: year from TestDate        // 2024
define Month: month from TestDate      // 6
define Day: day from TestDate          // 15
define Hour: hour from TestDate        // 10
define Minute: minute from TestDate    // 30
define Second: second from TestDate    // 45

// Get date or time portion
define DatePart: date from TestDate    // @2024-06-15
define TimePart: time from TestDate    // @T10:30:45
```

### Date Arithmetic

```cql
define StartDate: @2024-01-15

// Add durations
define PlusYear: StartDate + 1 year      // @2025-01-15
define PlusMonths: StartDate + 3 months  // @2024-04-15
define PlusWeeks: StartDate + 2 weeks    // @2024-01-29
define PlusDays: StartDate + 30 days     // @2024-02-14

// Subtract durations
define MinusYear: StartDate - 1 year     // @2023-01-15
define MinusDays: StartDate - 10 days    // @2024-01-05

// DateTime arithmetic
define AddHours: @2024-01-15T10:00:00 + 5 hours
define AddMinutes: @2024-01-15T10:00:00 + 45 minutes
```

### Duration Calculations

```cql
define BirthDate: @1990-03-15
define Today: @2024-06-15

// Calculate differences
define AgeYears: years between BirthDate and Today    // 34
define AgeMonths: months between BirthDate and Today  // 411
define AgeDays: days between BirthDate and Today      // 12510

// Time durations
define StartTime: @T09:00:00
define EndTime: @T17:30:00

define WorkHours: hours between StartTime and EndTime    // 8
define WorkMinutes: minutes between StartTime and EndTime // 510
```

### Date Comparisons

```cql
define Date1: @2024-01-15
define Date2: @2024-06-15

// Standard comparisons
define Before: Date1 before Date2         // true
define After: Date2 after Date1           // true
define SameOrBefore: Date1 same or before Date2  // true
define SameOrAfter: Date2 same or after Date1    // true

// Precision comparisons
define SameDay: @2024-06-15T10:00 same day as @2024-06-15T22:00   // true
define SameMonth: @2024-06-01 same month as @2024-06-30           // true
define SameYear: @2024-01-01 same year as @2024-12-31             // true
```

### Clinical Age Calculations

```cql
context Patient

// Patient age
define PatientAge: years between Patient.birthDate and Today()

// Age at specific date
define function AgeAt(birthDate Date, asOf Date) returns Integer:
    years between birthDate and asOf

// Age categories
define IsPediatric: PatientAge < 18
define IsAdult: PatientAge >= 18 and PatientAge < 65
define IsGeriatric: PatientAge >= 65
```

---

## Intervals

### Interval Basics

```cql
// Closed interval [includes endpoints]
define Closed: Interval[1, 10]         // includes 1 and 10

// Open interval (excludes endpoints)
define Open: Interval(1, 10)           // excludes 1 and 10

// Half-open
define LeftOpen: Interval(1, 10]       // excludes 1, includes 10
define RightOpen: Interval[1, 10)      // includes 1, excludes 10

// Date intervals
define Q1_2024: Interval[@2024-01-01, @2024-03-31]
```

### Interval Boundaries

```cql
define MyInterval: Interval[1, 10]

define Start: start of MyInterval      // 1
define End: end of MyInterval          // 10
define Width: width of MyInterval      // 9

// Low/High (same as start/end for closed)
define Low: low MyInterval             // 1
define High: high MyInterval           // 10
```

### Point Membership

```cql
// Point in interval
define ContainsPoint: Interval[1, 10] contains 5    // true
define PointIn: 5 in Interval[1, 10]                // true

// Boundary cases
define AtLow: 1 in Interval[1, 10]                  // true
define AtHigh: 10 in Interval[1, 10]                // true
define BelowOpenLow: 1 in Interval(1, 10)           // false
define AboveOpenHigh: 10 in Interval[1, 10)         // false
```

### Interval Relationships

```cql
define A: Interval[1, 5]
define B: Interval[3, 8]
define C: Interval[6, 10]
define D: Interval[1, 10]

// Overlaps
define Overlaps: A overlaps B          // true (share 3-5)
define NoOverlap: A overlaps C         // false

// Includes (one contains another)
define Includes: D includes A          // true
define IncludedIn: A included in D     // true

// Meets (adjacent)
define Meets: Interval[1, 5] meets Interval[6, 10]  // true

// Before/After
define Before: Interval[1, 3] before Interval[5, 10]  // true
define After: Interval[5, 10] after Interval[1, 3]    // true
```

### Interval Operations

```cql
// Union
define Union: Interval[1, 5] union Interval[3, 8]      // Interval[1, 8]

// Intersect
define Intersect: Interval[1, 5] intersect Interval[3, 8]  // Interval[3, 5]

// Collapse (merge adjacent/overlapping)
define Collapsed: collapse {
    Interval[1, 3],
    Interval[2, 5],
    Interval[7, 9]
}   // Returns: {Interval[1, 5], Interval[7, 9]}
```

### Clinical Interval Example

```cql
// Measurement period
parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// Check if event during measurement period
define ObservationsInPeriod:
    [Observation] O
        where O.effective during "Measurement Period"

// Check if encounter overlaps period
define EncountersInPeriod:
    [Encounter] E
        where E.period overlaps "Measurement Period"
```

---

## Queries

### Basic Query Structure

```cql
// Simple query
define FilteredList:
    from item in {1, 2, 3, 4, 5}
    where item > 2
    return item
// Returns: {3, 4, 5}
```

### Query Clauses

#### FROM - Define Sources

```cql
// Single source
from Obs in [Observation]

// Multiple sources
from C in [Condition],
     O in [Observation]
```

#### WHERE - Filter Results

```cql
define ActiveConditions:
    [Condition] C
        where C.clinicalStatus.coding.code contains 'active'

define RecentObs:
    [Observation] O
        where O.effective during "Measurement Period"
            and O.status = 'final'
```

#### LET - Define Variables

```cql
define ObsWithAge:
    [Observation] O
        let patientAge: years between Patient.birthDate and O.effective
        where O.status = 'final'
        return Tuple {
            observation: O,
            ageAtTest: patientAge
        }
```

#### RETURN - Shape Output

```cql
// Return specific property
define ObsDates:
    from O in [Observation]
    return O.effective

// Return tuple
define ObsSummary:
    from O in [Observation]
    return Tuple {
        code: O.code,
        value: O.value,
        date: O.effective
    }

// Return all (preserve duplicates)
define AllValues:
    from O in [Observation]
    return all O.value
```

#### SORT - Order Results

```cql
// Sort ascending
define OldestFirst:
    [Observation] O
        sort by effective

// Sort descending
define NewestFirst:
    [Observation] O
        sort by effective desc

// Multiple sort keys
define SortedObs:
    [Observation] O
        sort by status, effective desc
```

### Relationship Queries

#### WITH - Require Related Data

```cql
// Conditions with related observations
define ConditionsWithObs:
    [Condition] C
        with [Observation] O
            such that O.subject = C.subject
                and O.effective during "Measurement Period"
```

#### WITHOUT - Exclude Related Data

```cql
// Patients without recent labs
define NoRecentLabs:
    [Condition] C
        without [Observation] O
            such that O.effective during "Measurement Period"
```

### First and Last

```cql
// Most recent observation
define MostRecentGlucose:
    Last([Observation: "Glucose"] O
        where O.status = 'final'
        sort by effective)

// First observation in period
define FirstObsInPeriod:
    First([Observation] O
        where O.effective during "Measurement Period"
        sort by effective)
```

---

## Functions

### User-Defined Functions

```cql
// Simple function
define function Add(a Integer, b Integer) returns Integer:
    a + b

// Using the function
define Sum: Add(5, 3)  // Returns: 8
```

### Function Examples

```cql
// Null-safe division
define function SafeDivide(num Decimal, denom Decimal) returns Decimal:
    if denom is null or denom = 0 then null
    else num / denom

// Format name
define function FormatName(given String, family String) returns String:
    Coalesce(given, '') + ' ' + Coalesce(family, '')

// Age calculation
define function CalculateAge(birthDate Date) returns Integer:
    years between birthDate and Today()

// BMI calculation
define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
    if weightKg is null or heightCm is null or heightCm = 0 then null
    else Round(weightKg / Power(heightCm / 100, 2), 1)
```

### Built-in Functions

```cql
// String functions
Concat('Hello', ', ', 'World')     // 'Hello, World'
Combine({'a', 'b', 'c'}, ', ')     // 'a, b, c'
Split('a,b,c', ',')                // {'a', 'b', 'c'}
Upper('hello')                      // 'HELLO'
Lower('HELLO')                      // 'hello'
Substring('Hello', 0, 2)           // 'He'
IndexOf('Hello', 'l')              // 2
StartsWith('Hello', 'He')          // true
EndsWith('Hello', 'lo')            // true
Replace('Hello', 'l', 'L')         // 'HeLLo'
Length('Hello')                     // 5
Trim('  Hello  ')                  // 'Hello'

// Math functions
Abs(-5)                            // 5
Ceiling(3.2)                       // 4
Floor(3.8)                         // 3
Round(3.456, 2)                    // 3.46
Truncate(3.9)                      // 3
Sqrt(16)                           // 4.0
Power(2, 3)                        // 8
Ln(2.71828)                        // ~1.0
Exp(1)                             // ~2.718

// Null handling
Coalesce(null, null, 'default')    // 'default'
IsNull(null)                       // true
IsNotNull(5)                       // true
IsTrue(true)                       // true
IsFalse(false)                     // true
```

---

## Terminology

### Code Systems and Value Sets

```cql
// Define code systems
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "ICD10": 'http://hl7.org/fhir/sid/icd-10-cm'

// Define value sets
valueset "Diabetes": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.103.12.1001'
valueset "HbA1c Tests": 'http://example.org/ValueSet/hba1c-tests'

// Define individual codes
code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'
code "Type2DM": '44054006' from "SNOMED" display 'Type 2 diabetes'
```

### Using Value Sets in Queries

```cql
context Patient

// Retrieve by value set
define DiabetesConditions:
    [Condition: "Diabetes"]

define HbA1cResults:
    [Observation: "HbA1c Tests"]

// Check membership
define HasDiabetes:
    exists([Condition: "Diabetes"])
```

### Code Equivalence

```cql
// Check if codes are equivalent (~)
define MatchesDiabetes:
    [Condition] C
        where C.code ~ "Type2DM"

// Check if code is in value set
define InValueSet:
    [Observation] O
        where O.code in "HbA1c Tests"
```

---

## Clinical Examples

### Example 1: Diabetes Management Measure

```cql
library DiabetesManagement version '1.0.0'

using FHIR version '4.0.1'

codesystem "LOINC": 'http://loinc.org'

valueset "Diabetes": 'http://example.org/ValueSet/diabetes'
valueset "HbA1c Lab Test": 'http://example.org/ValueSet/hba1c'

parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// Population: Diabetic patients
define "Initial Population":
    exists([Condition: "Diabetes"] C
        where C.clinicalStatus.coding.code contains 'active')

// Denominator: Same as initial population
define "Denominator":
    "Initial Population"

// Numerator: HbA1c < 8%
define "Numerator":
    exists("Most Recent HbA1c" H
        where H.value < 8 '%')

// Most recent HbA1c in measurement period
define "Most Recent HbA1c":
    Last([Observation: "HbA1c Lab Test"] O
        where O.effective during "Measurement Period"
            and O.status = 'final'
        sort by effective)

// Stratification by age
define "Age 18-44":
    years between Patient.birthDate and Today() in Interval[18, 44]

define "Age 45-64":
    years between Patient.birthDate and Today() in Interval[45, 64]

define "Age 65+":
    years between Patient.birthDate and Today() >= 65
```

### Example 2: Medication Adherence

```cql
library MedicationAdherence version '1.0.0'

using FHIR version '4.0.1'

valueset "Statin Medications": 'http://example.org/ValueSet/statins'

parameter "Measurement Period" Interval<DateTime>

context Patient

// Active statin prescriptions
define "Active Statin Prescriptions":
    [MedicationRequest: "Statin Medications"] M
        where M.status = 'active'
            and M.authoredOn during "Measurement Period"

// Calculate covered days
define "Statin Covered Days":
    Sum(
        from M in "Active Statin Prescriptions"
        return M.dispenseRequest.expectedSupplyDuration.value
    )

// Total days in period
define "Total Days":
    days between start of "Measurement Period" and end of "Measurement Period"

// Adherence percentage
define "Medication Adherence":
    if "Total Days" > 0 then
        ("Statin Covered Days" / "Total Days") * 100
    else null

// Is adherent (>= 80%)
define "Is Adherent":
    "Medication Adherence" >= 80
```

### Example 3: Blood Pressure Screening

```cql
library BPScreening version '1.0.0'

using FHIR version '4.0.1'

codesystem "LOINC": 'http://loinc.org'

code "Systolic BP": '8480-6' from "LOINC"
code "Diastolic BP": '8462-4' from "LOINC"

valueset "Hypertension": 'http://example.org/ValueSet/hypertension'
valueset "Office Visit": 'http://example.org/ValueSet/office-visit'

parameter "Measurement Period" Interval<DateTime>

context Patient

// Most recent BP
define "Most Recent BP":
    Last([Observation] O
        where (O.code ~ "Systolic BP" or O.code ~ "Diastolic BP")
            and O.effective during "Measurement Period"
            and O.status = 'final'
        sort by effective)

// BP values
define "Systolic":
    Last([Observation: "Systolic BP"] O
        where O.effective during "Measurement Period"
        sort by effective).value.value

define "Diastolic":
    Last([Observation: "Diastolic BP"] O
        where O.effective during "Measurement Period"
        sort by effective).value.value

// BP Categories
define "BP Category":
    case
        when "Systolic" >= 180 or "Diastolic" >= 120 then 'Hypertensive Crisis'
        when "Systolic" >= 140 or "Diastolic" >= 90 then 'Stage 2 Hypertension'
        when "Systolic" >= 130 or "Diastolic" >= 80 then 'Stage 1 Hypertension'
        when "Systolic" >= 120 and "Diastolic" < 80 then 'Elevated'
        when "Systolic" < 120 and "Diastolic" < 80 then 'Normal'
        else 'Unknown'
    end

// Has qualifying encounter
define "Qualifying Encounter":
    exists([Encounter: "Office Visit"] E
        where E.period during "Measurement Period")

// Needs BP check
define "Needs BP Screening":
    "Qualifying Encounter"
        and ("Most Recent BP" is null
            or days between "Most Recent BP".effective and Today() > 365)
```

---

## Running CQL with This Library

### Using the CLI

```bash
# Evaluate a single expression
fhir cql eval "1 + 2 * 3"

# Run a library
fhir cql run examples/cql/01_hello_world.cql

# Run with specific definition
fhir cql run library.cql --definition "Initial Population"

# Run with patient data
fhir cql run library.cql --data patient.json

# Output results to file
fhir cql run library.cql --output results.json
```

### Using the Python API

```python
from fhir_cql.engine.cql import CQLEvaluator

# Create evaluator
evaluator = CQLEvaluator()

# Evaluate expression directly
result = evaluator.evaluate_expression("1 + 2 * 3")
print(result)  # 7

# Compile and run library
lib = evaluator.compile("""
    library Example version '1.0'
    using FHIR version '4.0.1'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, World!'
""")

# Evaluate definitions
sum_result = evaluator.evaluate_definition("Sum")
greeting = evaluator.evaluate_definition("Greeting")

# Evaluate all definitions
all_results = evaluator.evaluate_all_definitions()

# With patient data
patient = {
    "resourceType": "Patient",
    "birthDate": "1990-05-15",
    "gender": "male"
}

result = evaluator.evaluate_definition(
    "PatientAge",
    resource=patient
)
```

---

## Best Practices

### 1. Use Single Quotes for Strings

```cql
// Correct - single quotes for strings
define Name: 'John Smith'
define List: {'apple', 'banana'}

// Wrong - double quotes are for identifiers
define Name: "John Smith"  // This is an identifier reference!
```

### 2. Handle Nulls Explicitly

```cql
// Safe division
define SafeResult:
    if denominator is null or denominator = 0 then null
    else numerator / denominator

// Coalesce for defaults
define SafeValue: Coalesce(value, 0)
```

### 3. Use Meaningful Names

```cql
// Good
define "Initial Population": ...
define "Most Recent HbA1c": ...

// Avoid
define x: ...
define temp: ...
```

### 4. Structure Complex Logic

```cql
// Break into smaller definitions
define "Active Diabetes":
    [Condition: "Diabetes"] C
        where C.clinicalStatus.coding.code contains 'active'

define "Has Active Diabetes":
    exists("Active Diabetes")

define "Qualifying Patient":
    "Has Active Diabetes"
        and PatientAge >= 18
```

### 5. Use Parameters for Flexibility

```cql
parameter "Measurement Period" Interval<DateTime>
parameter "Age Threshold" Integer default 18

// Use parameters in definitions
define "Adults":
    PatientAge >= "Age Threshold"
```

---

## Resources

- [CQL Specification](https://cql.hl7.org/)
- [FHIRPath Specification](https://hl7.org/fhirpath/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [Example CQL Files](../examples/cql/)
