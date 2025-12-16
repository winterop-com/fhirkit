# CQL Step-by-Step Tutorial

A hands-on guide to learning Clinical Quality Language (CQL) from scratch.

## Prerequisites

- Python 3.13+ installed
- This library installed (`make install`)
- Completed the [FHIRPath Tutorial](fhirpath-tutorial.md) (recommended)

## Tutorial Overview

1. [Step 1: Your First CQL Expression](#step-1-your-first-cql-expression)
2. [Step 2: Basic Data Types](#step-2-basic-data-types)
3. [Step 3: Creating a Library](#step-3-creating-a-library)
4. [Step 4: Working with Lists](#step-4-working-with-lists)
5. [Step 5: Date and Time](#step-5-date-and-time)
6. [Step 6: Conditional Logic](#step-6-conditional-logic)
7. [Step 7: Functions](#step-7-functions)
8. [Step 8: Working with FHIR Data](#step-8-working-with-fhir-data)
9. [Step 9: Queries](#step-9-queries)
10. [Step 10: Clinical Example](#step-10-clinical-example)

---

## Step 1: Your First CQL Expression

### Goal

Learn to evaluate simple CQL expressions.

### Run Your First Expression

```bash
fhir cql eval "1 + 2"
```

Output:
```
3
```

### Try More Arithmetic

```bash
fhir cql eval "10 - 3"
fhir cql eval "4 * 5"
fhir cql eval "15 / 3"
fhir cql eval "2 + 3 * 4"
```

The last one outputs `14` (multiplication before addition).

### Integer vs Decimal Division

```bash
# Integer division (truncates)
fhir cql eval "7 div 2"
```

Output:
```
3
```

```bash
# Decimal division
fhir cql eval "7.0 / 2.0"
```

Output:
```
3.5
```

### Modulo (Remainder)

```bash
fhir cql eval "7 mod 3"
```

Output:
```
1
```

### Try It Yourself

Calculate these:

```bash
fhir cql eval "(10 + 5) * 2"
fhir cql eval "100 div 7"
fhir cql eval "100 mod 7"
fhir cql eval "2.5 + 3.5"
```

### What You Learned

- CQL evaluates arithmetic expressions
- `div` for integer division, `/` for decimal
- `mod` for remainder
- Standard operator precedence applies

---

## Step 2: Basic Data Types

### Goal

Learn CQL's core data types.

### Strings (Use Single Quotes!)

```bash
fhir cql eval "'Hello, World!'"
fhir cql eval "'CQL' + ' is ' + 'powerful'"
```

Important: CQL uses **single quotes** for strings. Double quotes are for identifiers.

### String Functions

```bash
fhir cql eval "Upper('hello')"
fhir cql eval "Lower('HELLO')"
fhir cql eval "Length('Hello')"
fhir cql eval "Substring('Hello World', 0, 5)"
```

### Booleans

```bash
fhir cql eval "true"
fhir cql eval "false"
fhir cql eval "true and false"
fhir cql eval "true or false"
fhir cql eval "not true"
```

### Boolean Logic

```bash
fhir cql eval "5 > 3"
fhir cql eval "5 = 5"
fhir cql eval "5 != 3"
fhir cql eval "5 >= 5"
fhir cql eval "3 < 5 and 5 < 10"
```

### Null

```bash
fhir cql eval "null"
fhir cql eval "5 + null"
fhir cql eval "null = null"
```

Note: In CQL, `null = null` returns `null`, not `true`. Use `is null` to check:

```bash
fhir cql eval "null is null"
fhir cql eval "5 is not null"
```

### Try It Yourself

```bash
fhir cql eval "'Hello' + ' ' + 'World'"
fhir cql eval "Upper('hello') = 'HELLO'"
fhir cql eval "10 > 5 and 10 < 20"
fhir cql eval "StartsWith('Hello', 'He')"
```

### What You Learned

- Strings use single quotes
- Boolean operators: `and`, `or`, `not`
- Comparison operators: `=`, `!=`, `>`, `<`, `>=`, `<=`
- `null` propagates through operations
- Use `is null` and `is not null` for null checks

---

## Step 3: Creating a Library

### Goal

Learn to write CQL libraries with definitions.

### Create Your First Library

Save this as `hello.cql`:

```cql
library HelloWorld version '1.0.0'

// Simple definitions
define Greeting: 'Hello, CQL!'
define Sum: 1 + 2 + 3
define IsTrue: true and not false
```

### Run the Library

```bash
fhir cql run hello.cql
```

Output:
```
Library: HelloWorld v1.0.0

+------------+---------------+
| Definition | Value         |
+------------+---------------+
| Greeting   | 'Hello, CQL!' |
| Sum        | 6             |
| IsTrue     | true          |
+------------+---------------+
```

### Run a Specific Definition

```bash
fhir cql run hello.cql --definition Sum
```

### List Definitions

```bash
fhir cql definitions hello.cql
```

### Definitions Can Reference Each Other

Update `hello.cql`:

```cql
library HelloWorld version '1.0.0'

define A: 10
define B: 20
define Sum: A + B
define Product: A * B
define Average: (A + B) / 2.0
```

Run it:

```bash
fhir cql run hello.cql
```

### Try It Yourself

Create `math.cql`:

```cql
library MathExamples version '1.0.0'

define Pi: 3.14159
define Radius: 5
define CircleArea: Pi * Radius * Radius
define Circumference: 2 * Pi * Radius
```

```bash
fhir cql run math.cql
```

### What You Learned

- Libraries start with `library Name version '...'`
- `define Name: expression` creates definitions
- Definitions can reference other definitions
- `fhir cql run` evaluates all definitions
- `--definition` evaluates a specific one

---

## Step 4: Working with Lists

### Goal

Learn to create and manipulate lists.

### Creating Lists

```bash
fhir cql eval "{1, 2, 3, 4, 5}"
fhir cql eval "{'apple', 'banana', 'cherry'}"
fhir cql eval "{}"
```

### Accessing Elements

```bash
fhir cql eval "First({1, 2, 3})"
fhir cql eval "Last({1, 2, 3})"
fhir cql eval "{1, 2, 3, 4, 5}[2]"
```

### List Operations

```bash
# Count
fhir cql eval "Count({1, 2, 3, 4, 5})"

# Take first N
fhir cql eval "Take({1, 2, 3, 4, 5}, 3)"

# Skip first N
fhir cql eval "Skip({1, 2, 3, 4, 5}, 2)"

# Tail (all except first)
fhir cql eval "Tail({1, 2, 3, 4, 5})"
```

### Aggregate Functions

```bash
fhir cql eval "Sum({1, 2, 3, 4, 5})"
fhir cql eval "Avg({10, 20, 30})"
fhir cql eval "Min({5, 2, 8, 1, 9})"
fhir cql eval "Max({5, 2, 8, 1, 9})"
```

### Membership

```bash
# Check if list contains value
fhir cql eval "{1, 2, 3} contains 2"

# Check if value is in list
fhir cql eval "2 in {1, 2, 3}"

# Check if exists
fhir cql eval "exists({1, 2, 3})"
fhir cql eval "exists({})"
```

### Combining Lists

```bash
# Union (removes duplicates)
fhir cql eval "{1, 2, 3} union {3, 4, 5}"

# Intersect (common elements)
fhir cql eval "{1, 2, 3, 4} intersect {2, 3, 5}"

# Except (remove elements)
fhir cql eval "{1, 2, 3, 4} except {2, 4}"
```

### Create a Library

Save as `lists.cql`:

```cql
library ListExamples version '1.0.0'

define Numbers: {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

define Total: Sum(Numbers)
define Average: Avg(Numbers)
define Minimum: Min(Numbers)
define Maximum: Max(Numbers)

define FirstThree: Take(Numbers, 3)
define LastThree: Skip(Numbers, 7)

define HasFive: Numbers contains 5
define EvenNumbers: {2, 4, 6, 8, 10}
define OddNumbers: Numbers except EvenNumbers
```

```bash
fhir cql run lists.cql
```

### Try It Yourself

```bash
fhir cql eval "Flatten({{1, 2}, {3, 4}, {5}})"
fhir cql eval "distinct {1, 1, 2, 2, 3, 3}"
fhir cql eval "Sort({5, 2, 8, 1, 9})"
```

### What You Learned

- Lists use curly braces: `{1, 2, 3}`
- `First()`, `Last()`, `Take()`, `Skip()` for access
- `Sum()`, `Avg()`, `Min()`, `Max()` for aggregation
- `contains`, `in`, `exists()` for membership
- `union`, `intersect`, `except` for combining

---

## Step 5: Date and Time

### Goal

Learn to work with dates and times.

### Date Literals

```bash
# Date literal (starts with @)
fhir cql eval "@2024-06-15"

# DateTime literal
fhir cql eval "@2024-06-15T10:30:00"

# Partial dates
fhir cql eval "@2024-06"
fhir cql eval "@2024"
```

### Current Date/Time

```bash
fhir cql eval "Today()"
fhir cql eval "Now()"
```

### Date Arithmetic

```bash
# Add duration
fhir cql eval "@2024-01-15 + 30 days"
fhir cql eval "@2024-01-15 + 2 months"
fhir cql eval "@2024-01-15 + 1 year"

# Subtract duration
fhir cql eval "@2024-06-15 - 10 days"
fhir cql eval "Today() - 1 week"
```

### Duration Between Dates

```bash
fhir cql eval "years between @1990-03-15 and @2024-06-15"
fhir cql eval "months between @2024-01-01 and @2024-06-15"
fhir cql eval "days between @2024-06-01 and @2024-06-15"
```

### Extract Date Parts

```bash
fhir cql eval "year from @2024-06-15"
fhir cql eval "month from @2024-06-15"
fhir cql eval "day from @2024-06-15"
```

### Date Comparisons

```bash
fhir cql eval "@2024-01-01 before @2024-06-15"
fhir cql eval "@2024-06-15 after @2024-01-01"
fhir cql eval "@2024-06-15 same day as @2024-06-15"
fhir cql eval "@2024-06-15 same month as @2024-06-01"
```

### Create a Library

Save as `dates.cql`:

```cql
library DateExamples version '1.0.0'

define CurrentDate: Today()
define CurrentDateTime: Now()

define BirthDate: @1990-05-15
define Age: years between BirthDate and Today()

define NextBirthday: @2024-05-15
define DaysUntilBirthday: days between Today() and NextBirthday

define StartOfYear: @2024-01-01
define EndOfYear: @2024-12-31
define DaysInYear: days between StartOfYear and EndOfYear

define NextWeek: Today() + 7 days
define LastMonth: Today() - 1 month
```

```bash
fhir cql run dates.cql
```

### Try It Yourself

```bash
fhir cql eval "Today() + 100 days"
fhir cql eval "years between @2000-01-01 and Today()"
fhir cql eval "@2024-02-28 + 1 day"
```

### What You Learned

- Date literals start with `@`
- `Today()` and `Now()` for current date/time
- Add/subtract with `+ N days/months/years`
- `years/months/days between` for durations
- `year/month/day from` for extraction
- `before`, `after`, `same day as` for comparison

---

## Step 6: Conditional Logic

### Goal

Learn to write conditional expressions.

### If-Then-Else

```bash
fhir cql eval "if 5 > 3 then 'yes' else 'no'"
fhir cql eval "if true then 100 else 0"
```

### Nested Conditions

```bash
fhir cql eval "if 10 > 20 then 'big' else if 10 > 5 then 'medium' else 'small'"
```

### Case Expressions

```bash
fhir cql eval "case when 5 > 10 then 'big' when 5 > 3 then 'medium' else 'small' end"
```

### Case with Value

```bash
fhir cql eval "case 'red' when 'red' then 'stop' when 'green' then 'go' else 'caution' end"
```

### Create a Library

Save as `conditions.cql`:

```cql
library ConditionExamples version '1.0.0'

define Age: 35

define AgeCategory:
    if Age < 18 then 'Pediatric'
    else if Age < 65 then 'Adult'
    else 'Geriatric'

define Score: 75

define Grade:
    case
        when Score >= 90 then 'A'
        when Score >= 80 then 'B'
        when Score >= 70 then 'C'
        when Score >= 60 then 'D'
        else 'F'
    end

define Temperature: 98.6

define TemperatureStatus:
    case
        when Temperature >= 103 then 'High Fever'
        when Temperature >= 100.4 then 'Fever'
        when Temperature >= 97 then 'Normal'
        else 'Low'
    end
```

```bash
fhir cql run conditions.cql
```

### Null Handling

```bash
# Coalesce returns first non-null
fhir cql eval "Coalesce(null, null, 'default')"
fhir cql eval "Coalesce(5, 10, 15)"

# If null then default
fhir cql eval "if null is null then 'was null' else 'not null'"
```

### Try It Yourself

Create `bmi.cql`:

```cql
library BMICalculator version '1.0.0'

define WeightKg: 70
define HeightCm: 175

define BMI: Round(WeightKg / Power(HeightCm / 100, 2), 1)

define BMICategory:
    case
        when BMI < 18.5 then 'Underweight'
        when BMI < 25 then 'Normal'
        when BMI < 30 then 'Overweight'
        else 'Obese'
    end
```

```bash
fhir cql run bmi.cql
```

### What You Learned

- `if condition then value else value` for conditionals
- `case when ... then ... else ... end` for multiple conditions
- `Coalesce()` returns first non-null value
- Conditions can be nested

---

## Step 7: Functions

### Goal

Learn to define and use functions.

### Built-in Functions

```bash
# Math
fhir cql eval "Abs(-5)"
fhir cql eval "Round(3.456, 2)"
fhir cql eval "Sqrt(16)"
fhir cql eval "Power(2, 10)"

# String
fhir cql eval "Concat('Hello', ' ', 'World')"
fhir cql eval "Combine({'a', 'b', 'c'}, ', ')"
fhir cql eval "Split('a,b,c', ',')"
fhir cql eval "Replace('Hello', 'l', 'L')"
```

### User-Defined Functions

Save as `functions.cql`:

```cql
library FunctionExamples version '1.0.0'

// Simple function
define function Add(a Integer, b Integer) returns Integer:
    a + b

// Using the function
define SumResult: Add(10, 20)

// Function with null handling
define function SafeDivide(num Decimal, denom Decimal) returns Decimal:
    if denom is null or denom = 0 then null
    else num / denom

define Division1: SafeDivide(10.0, 2.0)
define Division2: SafeDivide(10.0, 0.0)

// BMI calculation function
define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
    if weightKg is null or heightCm is null or heightCm = 0 then null
    else Round(weightKg / Power(heightCm / 100, 2), 1)

define MyBMI: CalculateBMI(70.0, 175.0)

// Temperature conversion
define function CelsiusToFahrenheit(celsius Decimal) returns Decimal:
    Round((celsius * 9 / 5) + 32, 1)

define function FahrenheitToCelsius(fahrenheit Decimal) returns Decimal:
    Round((fahrenheit - 32) * 5 / 9, 1)

define BodyTempF: CelsiusToFahrenheit(37.0)
define BodyTempC: FahrenheitToCelsius(98.6)
```

```bash
fhir cql run functions.cql
```

### Recursive Functions

Save as `factorial.cql`:

```cql
library Factorial version '1.0.0'

define function Factorial(n Integer) returns Integer:
    if n <= 1 then 1
    else n * Factorial(n - 1)

define Fact5: Factorial(5)
define Fact10: Factorial(10)
```

```bash
fhir cql run factorial.cql
```

### Try It Yourself

Create a library with these functions:

```cql
library MyFunctions version '1.0.0'

// Calculate age from birth date
define function AgeInYears(birthDate Date) returns Integer:
    years between birthDate and Today()

// Format a name
define function FormatName(given String, family String) returns String:
    given + ' ' + family

// Check if adult
define function IsAdult(age Integer) returns Boolean:
    age >= 18

define TestAge: AgeInYears(@1990-05-15)
define TestName: FormatName('John', 'Smith')
define TestAdult: IsAdult(TestAge)
```

### What You Learned

- Define functions with `define function Name(params) returns Type:`
- Functions can call other functions
- Functions can be recursive
- Use null checks for safety

---

## Step 8: Working with FHIR Data

### Goal

Learn to evaluate CQL with FHIR patient data.

### Create Patient Data

Save as `patient.json`:

```json
{
  "resourceType": "Patient",
  "id": "patient-1",
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["John", "Robert"]
    }
  ],
  "gender": "male",
  "birthDate": "1985-03-15"
}
```

### Access Patient Data

```bash
# Direct expression with patient context
fhir cql eval "Patient.gender" --data patient.json
fhir cql eval "Patient.birthDate" --data patient.json
fhir cql eval "Patient.name.first().family" --data patient.json
```

### Create a Patient Library

Save as `patient-info.cql`:

```cql
library PatientInfo version '1.0.0'

using FHIR version '4.0.1'

context Patient

define PatientName:
    Patient.name.first().given.first() + ' ' + Patient.name.first().family

define PatientGender:
    Patient.gender

define PatientBirthDate:
    Patient.birthDate

define PatientAge:
    years between Patient.birthDate and Today()

define IsAdult:
    PatientAge >= 18

define AgeCategory:
    case
        when PatientAge < 18 then 'Pediatric'
        when PatientAge < 65 then 'Adult'
        else 'Geriatric'
    end
```

```bash
fhir cql run patient-info.cql --data patient.json
```

### Working with Bundles

Save as `patient-bundle.json`:

```json
{
  "resourceType": "Bundle",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Smith", "given": ["John"]}],
        "gender": "male",
        "birthDate": "1985-03-15"
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "condition-1",
        "subject": {"reference": "Patient/patient-1"},
        "clinicalStatus": {
          "coding": [{"code": "active"}]
        },
        "code": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "44054006",
              "display": "Type 2 diabetes mellitus"
            }
          ]
        }
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-1",
        "subject": {"reference": "Patient/patient-1"},
        "status": "final",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "4548-4",
              "display": "Hemoglobin A1c"
            }
          ]
        },
        "valueQuantity": {
          "value": 7.2,
          "unit": "%"
        }
      }
    }
  ]
}
```

### Retrieve Resources

Save as `retrieve-example.cql`:

```cql
library RetrieveExample version '1.0.0'

using FHIR version '4.0.1'

context Patient

// Retrieve all conditions for this patient
define Conditions: [Condition]

// Retrieve all observations
define Observations: [Observation]

// Count resources
define ConditionCount: Count(Conditions)
define ObservationCount: Count(Observations)
```

```bash
fhir cql run retrieve-example.cql --data patient-bundle.json
```

### Try It Yourself

Add more data to the bundle and query it:

```cql
library MyQueries version '1.0.0'

using FHIR version '4.0.1'

context Patient

define AllConditions: [Condition]
define ActiveConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'

define HasDiabetes:
    exists(ActiveConditions)
```

### Using FHIRHelpers

FHIRKit includes a built-in **FHIRHelpers** library that provides standard conversion functions for working with FHIR data. It's automatically available.

Save as `fhirhelpers-example.cql`:

```cql
library FHIRHelpersExample version '1.0.0'

using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'

context Patient

// Get all observations
define Observations: [Observation]

// Get the latest HbA1c observation
define LatestHbA1c:
    Last([Observation] O
        where O.code.coding.code = '4548-4'
        sort by effective)

// Use FHIRHelpers to convert FHIR Quantity to CQL Quantity
define LatestHbA1cValue:
    FHIRHelpers.ToQuantity(LatestHbA1c.value as FHIR.Quantity)

// Check if HbA1c is controlled (< 7%)
define HbA1cControlled:
    LatestHbA1cValue < 7.0 '%'
```

```bash
fhir cql run fhirhelpers-example.cql --data patient-bundle.json
```

#### Common FHIRHelpers Functions

| Function | Purpose |
|----------|---------|
| `ToQuantity()` | Convert FHIR Quantity to CQL Quantity |
| `ToCode()` | Convert FHIR Coding to CQL Code |
| `ToConcept()` | Convert CodeableConcept to Concept |
| `ToInterval()` | Convert FHIR Period to Interval |
| `ToString()` | Extract string value |
| `ToDateTime()` | Convert to DateTime |
| `ToDate()` | Convert to Date |

#### Using an Alias

```cql
library AliasExample version '1.0.0'

using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FH

context Patient

// Shorter reference with alias
define Weight:
    FH.ToQuantity(
        (Last([Observation] O where O.code.coding.code = '29463-7')).value as FHIR.Quantity
    )
```

### What You Learned

- `using FHIR version '4.0.1'` declares FHIR model
- `context Patient` scopes to patient
- Access patient properties with `Patient.property`
- `[ResourceType]` retrieves resources
- `--data` loads JSON data
- `include FHIRHelpers` provides type conversion functions
- FHIRHelpers is built-in and automatically available

---

## Step 9: Queries

### Goal

Learn CQL query syntax for filtering and transforming data.

### Basic Query

```bash
# Filter a list
fhir cql eval "from n in {1, 2, 3, 4, 5} where n > 2 return n"
```

Output:
```
[3, 4, 5]
```

### Transform Results

```bash
# Double each value
fhir cql eval "from n in {1, 2, 3, 4, 5} return n * 2"
```

Output:
```
[2, 4, 6, 8, 10]
```

### Query with Let

```bash
# Define intermediate values
fhir cql eval "from n in {1, 2, 3, 4, 5} let squared: n * n where squared > 10 return squared"
```

### Sorting

```bash
fhir cql eval "Sort({5, 2, 8, 1, 9})"
fhir cql eval "from n in {5, 2, 8, 1, 9} return n sort asc"
fhir cql eval "from n in {5, 2, 8, 1, 9} return n sort desc"
```

### Query Library

Save as `queries.cql`:

```cql
library QueryExamples version '1.0.0'

define Numbers: {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

// Filter: greater than 5
define GreaterThanFive:
    from n in Numbers
    where n > 5
    return n

// Transform: square each
define Squared:
    from n in Numbers
    return n * n

// Combined: squares greater than 25
define LargeSquares:
    from n in Numbers
    let sq: n * n
    where sq > 25
    return sq

// Sorted descending
define SortedDesc:
    from n in Numbers
    return n
    sort desc

// First 3 even numbers
define FirstThreeEven:
    Take(
        from n in Numbers
        where n mod 2 = 0
        return n,
        3
    )
```

```bash
fhir cql run queries.cql
```

### FHIR Queries

Save as `fhir-queries.cql`:

```cql
library FHIRQueries version '1.0.0'

using FHIR version '4.0.1'

context Patient

// Get all observations
define AllObservations: [Observation]

// Filter to final observations
define FinalObservations:
    [Observation] O
        where O.status = 'final'

// Get observation values
define ObservationValues:
    from O in FinalObservations
    return O.value

// Most recent observation
define MostRecent:
    Last(
        [Observation] O
            where O.status = 'final'
            sort by effective
    )

// Active conditions
define ActiveConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'

// Condition codes
define ConditionCodes:
    from C in ActiveConditions
    return C.code.coding.first().display
```

```bash
fhir cql run fhir-queries.cql --data patient-bundle.json
```

### Try It Yourself

```bash
# Query strings
fhir cql eval "from name in {'Alice', 'Bob', 'Charlie'} where StartsWith(name, 'A') return name"

# Query with transformation
fhir cql eval "from name in {'alice', 'bob', 'charlie'} return Upper(name)"
```

### What You Learned

- `from x in list where condition return expression`
- `let` defines intermediate values
- `sort asc` or `sort desc` for ordering
- Can query FHIR resources directly
- `First()` and `Last()` with queries

---

## Step 10: Clinical Example

### Goal

Build a complete clinical quality measure.

### Scenario: Diabetes HbA1c Monitoring

We'll create a measure that checks if diabetic patients have an HbA1c test result under control.

### Create Test Data

Save as `diabetic-patient.json`:

```json
{
  "resourceType": "Bundle",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Johnson", "given": ["Mary"]}],
        "gender": "female",
        "birthDate": "1965-08-20"
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "diabetes",
        "subject": {"reference": "Patient/patient-1"},
        "clinicalStatus": {
          "coding": [{"code": "active"}]
        },
        "code": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "44054006",
              "display": "Type 2 diabetes mellitus"
            }
          ]
        }
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "hba1c-1",
        "subject": {"reference": "Patient/patient-1"},
        "status": "final",
        "effectiveDateTime": "2024-03-15",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "4548-4",
              "display": "Hemoglobin A1c"
            }
          ]
        },
        "valueQuantity": {
          "value": 7.2,
          "unit": "%"
        }
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "hba1c-2",
        "subject": {"reference": "Patient/patient-1"},
        "status": "final",
        "effectiveDateTime": "2024-06-15",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "4548-4",
              "display": "Hemoglobin A1c"
            }
          ]
        },
        "valueQuantity": {
          "value": 6.8,
          "unit": "%"
        }
      }
    }
  ]
}
```

### Create the Measure

Save as `diabetes-measure.cql`:

```cql
library DiabetesHbA1cMeasure version '1.0.0'

using FHIR version '4.0.1'

// Code systems
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "LOINC": 'http://loinc.org'

// Codes
code "Type2DM": '44054006' from "SNOMED"
code "HbA1c": '4548-4' from "LOINC"

// Parameters
parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// =====================
// Patient Demographics
// =====================

define PatientName:
    Patient.name.first().given.first() + ' ' + Patient.name.first().family

define PatientAge:
    years between Patient.birthDate and Today()

// =====================
// Clinical Data
// =====================

// All diabetes conditions
define DiabetesConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'

// Check if patient has diabetes
define HasDiabetes:
    exists(DiabetesConditions)

// All HbA1c observations
define HbA1cTests:
    [Observation] O
        where O.status = 'final'

// Most recent HbA1c
define MostRecentHbA1c:
    Last(
        HbA1cTests O
            sort by effective
    )

// Most recent HbA1c value
define MostRecentHbA1cValue:
    MostRecentHbA1c.value.value

// Most recent HbA1c date
define MostRecentHbA1cDate:
    MostRecentHbA1c.effective

// =====================
// Measure Logic
// =====================

// Initial Population: Diabetic patients 18+
define "Initial Population":
    HasDiabetes and PatientAge >= 18

// Denominator: Same as initial population
define "Denominator":
    "Initial Population"

// Numerator: HbA1c < 8%
define "Numerator":
    "Initial Population"
        and MostRecentHbA1cValue < 8

// Control status
define HbA1cControlStatus:
    case
        when MostRecentHbA1cValue is null then 'No Test'
        when MostRecentHbA1cValue < 7 then 'Well Controlled'
        when MostRecentHbA1cValue < 8 then 'Controlled'
        when MostRecentHbA1cValue < 9 then 'Poorly Controlled'
        else 'Uncontrolled'
    end

// =====================
// Summary
// =====================

define MeasureSummary:
    'Patient: ' + PatientName +
    ', Age: ' + ToString(PatientAge) +
    ', Has Diabetes: ' + ToString(HasDiabetes) +
    ', Last HbA1c: ' + ToString(MostRecentHbA1cValue) + '%' +
    ', Status: ' + HbA1cControlStatus
```

### Run the Measure

```bash
fhir cql run diabetes-measure.cql --data diabetic-patient.json
```

### Expected Output

```
Library: DiabetesHbA1cMeasure v1.0.0

+------------------------+------------------------------------------+
| Definition             | Value                                    |
+------------------------+------------------------------------------+
| PatientName            | 'Mary Johnson'                           |
| PatientAge             | 59                                       |
| DiabetesConditions     | [<Condition>]                            |
| HasDiabetes            | true                                     |
| HbA1cTests             | [<Observation>, <Observation>]           |
| MostRecentHbA1c        | <Observation>                            |
| MostRecentHbA1cValue   | 6.8                                      |
| MostRecentHbA1cDate    | @2024-06-15                              |
| Initial Population     | true                                     |
| Denominator            | true                                     |
| Numerator              | true                                     |
| HbA1cControlStatus     | 'Well Controlled'                        |
| MeasureSummary         | 'Patient: Mary Johnson, Age: 59...'      |
+------------------------+------------------------------------------+
```

### Test Different Scenarios

Edit `diabetic-patient.json` to change the HbA1c value:

1. Change to `8.5` - should show "Poorly Controlled"
2. Change to `10.0` - should show "Uncontrolled"
3. Remove the observation - should show "No Test"

### What You Learned

- Complete library structure with codesystems and codes
- Parameters for measurement periods
- Querying and filtering FHIR resources
- Building measure populations
- Creating summary output

---

## Additional Examples

This section provides extensive additional examples covering advanced CQL features.

### Interval Examples

Intervals are ranges of values - essential for date ranges, age ranges, and more.

#### Creating Intervals

```bash
# Closed interval (includes endpoints)
fhir cql eval "Interval[1, 10]"

# Open interval (excludes endpoints)
fhir cql eval "Interval(1, 10)"

# Half-open intervals
fhir cql eval "Interval[1, 10)"
fhir cql eval "Interval(1, 10]"

# Date intervals
fhir cql eval "Interval[@2024-01-01, @2024-12-31]"

# DateTime intervals
fhir cql eval "Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]"
```

#### Interval Properties

```bash
# Get start and end
fhir cql eval "start of Interval[1, 10]"
fhir cql eval "end of Interval[1, 10]"

# Get width
fhir cql eval "width of Interval[1, 10]"

# Get low and high bounds
fhir cql eval "low Interval[1, 10]"
fhir cql eval "high Interval[1, 10]"

# Point from single-value interval
fhir cql eval "point from Interval[5, 5]"
```

#### Interval Membership

```bash
# Check if value is in interval
fhir cql eval "5 in Interval[1, 10]"
fhir cql eval "15 in Interval[1, 10]"

# Check if interval contains value
fhir cql eval "Interval[1, 10] contains 5"

# Boundary cases
fhir cql eval "1 in Interval[1, 10]"
fhir cql eval "1 in Interval(1, 10)"
fhir cql eval "10 in Interval[1, 10)"
```

#### Interval Relationships

```bash
# Overlaps
fhir cql eval "Interval[1, 5] overlaps Interval[3, 8]"
fhir cql eval "Interval[1, 3] overlaps Interval[5, 8]"

# Includes
fhir cql eval "Interval[1, 10] includes Interval[3, 7]"

# Before/After
fhir cql eval "Interval[1, 3] before Interval[5, 10]"
fhir cql eval "Interval[5, 10] after Interval[1, 3]"

# Meets (adjacent)
fhir cql eval "Interval[1, 5] meets Interval[6, 10]"

# Starts/Ends
fhir cql eval "Interval[1, 5] starts Interval[1, 10]"
fhir cql eval "Interval[5, 10] ends Interval[1, 10]"
```

#### Interval Operations

```bash
# Union
fhir cql eval "Interval[1, 5] union Interval[3, 8]"

# Intersect
fhir cql eval "Interval[1, 5] intersect Interval[3, 8]"

# Except
fhir cql eval "Interval[1, 10] except Interval[4, 6]"

# Collapse overlapping intervals
fhir cql eval "collapse {Interval[1, 3], Interval[2, 5], Interval[7, 10]}"

# Expand to list
fhir cql eval "expand Interval[@2024-01-01, @2024-01-05] per day"
```

#### Interval Library Example

Save as `intervals.cql`:

```cql
library IntervalExamples version '1.0'

// Measurement period
define MeasurementPeriod:
    Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

// Quarters
define Q1: Interval[@2024-01-01, @2024-03-31]
define Q2: Interval[@2024-04-01, @2024-06-30]
define Q3: Interval[@2024-07-01, @2024-09-30]
define Q4: Interval[@2024-10-01, @2024-12-31]

// Check if date is in Q2
define InQ2: @2024-05-15 during Q2

// Age ranges
define PediatricAge: Interval[0, 17]
define AdultAge: Interval[18, 64]
define GeriatricAge: Interval[65, 120]

// Check age category
define Age: 45
define IsPediatric: Age in PediatricAge
define IsAdult: Age in AdultAge
define IsGeriatric: Age in GeriatricAge

// Combine overlapping intervals
define CoverageIntervals: {
    Interval[@2024-01-01, @2024-03-15],
    Interval[@2024-03-01, @2024-06-30],
    Interval[@2024-08-01, @2024-12-31]
}
define CollapsedCoverage: collapse CoverageIntervals

// Days in each month
define JanuaryDays: expand Interval[@2024-01-01, @2024-01-31] per day
define JanuaryDayCount: Count(JanuaryDays)
```

```bash
fhir cql run intervals.cql
```

---

### Aggregate Operations

Powerful operations for summarizing collections.

#### Basic Aggregates

```bash
# Sum
fhir cql eval "Sum({1, 2, 3, 4, 5})"

# Average
fhir cql eval "Avg({10, 20, 30, 40, 50})"

# Min and Max
fhir cql eval "Min({5, 2, 8, 1, 9})"
fhir cql eval "Max({5, 2, 8, 1, 9})"

# Count
fhir cql eval "Count({1, 2, 3, 4, 5})"

# All elements true?
fhir cql eval "AllTrue({true, true, true})"
fhir cql eval "AllTrue({true, false, true})"

# Any element true?
fhir cql eval "AnyTrue({false, true, false})"
fhir cql eval "AnyTrue({false, false, false})"
```

#### Population Statistics

```bash
# Population variance
fhir cql eval "PopulationVariance({2, 4, 4, 4, 5, 5, 7, 9})"

# Population standard deviation
fhir cql eval "PopulationStdDev({2, 4, 4, 4, 5, 5, 7, 9})"

# Sample variance
fhir cql eval "Variance({2, 4, 4, 4, 5, 5, 7, 9})"

# Sample standard deviation
fhir cql eval "StdDev({2, 4, 4, 4, 5, 5, 7, 9})"

# Median
fhir cql eval "Median({1, 2, 3, 4, 5})"
fhir cql eval "Median({1, 2, 3, 4, 5, 6})"

# Mode
fhir cql eval "Mode({1, 2, 2, 3, 3, 3, 4})"
```

#### Query Aggregates

```bash
# Sum with query
fhir cql eval "Sum(from n in {1, 2, 3, 4, 5} return n * 2)"

# Count with filter
fhir cql eval "Count(from n in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10} where n mod 2 = 0 return n)"

# Average of squares
fhir cql eval "Avg(from n in {1, 2, 3, 4, 5} return n * n)"
```

#### Aggregate Library Example

Save as `aggregates.cql`:

```cql
library AggregateExamples version '1.0'

define Scores: {85, 92, 78, 95, 88, 76, 90, 82, 94, 87}

// Basic statistics
define TotalScore: Sum(Scores)
define AverageScore: Avg(Scores)
define MinScore: Min(Scores)
define MaxScore: Max(Scores)
define MedianScore: Median(Scores)
define ScoreCount: Count(Scores)

// Calculated statistics
define ScoreRange: MaxScore - MinScore
define StdDeviation: StdDev(Scores)

// Passing scores (>= 80)
define PassingScores: from s in Scores where s >= 80 return s
define PassingCount: Count(PassingScores)
define PassingRate: Round(PassingCount / ScoreCount * 100, 1)

// Grade distribution
define ACount: Count(from s in Scores where s >= 90 return s)
define BCount: Count(from s in Scores where s >= 80 and s < 90 return s)
define CCount: Count(from s in Scores where s >= 70 and s < 80 return s)
define FCount: Count(from s in Scores where s < 70 return s)

// Normalized scores (0-100 scale to 0-1)
define NormalizedScores: from s in Scores return s / 100.0

// Top 3 scores
define TopThree: Take(from s in Scores return s sort desc, 3)

// Bottom 3 scores
define BottomThree: Take(from s in Scores return s sort asc, 3)
```

```bash
fhir cql run aggregates.cql
```

---

### String Functions

Extensive string manipulation capabilities.

#### Basic String Operations

```bash
# Concatenation
fhir cql eval "'Hello' + ' ' + 'World'"
fhir cql eval "Concat('Hello', ' ', 'World')"

# Length
fhir cql eval "Length('Hello World')"

# Case conversion
fhir cql eval "Upper('hello')"
fhir cql eval "Lower('HELLO')"
```

#### Substring and Position

```bash
# Substring (0-indexed)
fhir cql eval "Substring('Hello World', 0, 5)"
fhir cql eval "Substring('Hello World', 6)"

# Position of character
fhir cql eval "PositionOf('o', 'Hello World')"
fhir cql eval "LastPositionOf('o', 'Hello World')"
```

#### String Matching

```bash
# StartsWith / EndsWith
fhir cql eval "StartsWith('Hello World', 'Hello')"
fhir cql eval "EndsWith('Hello World', 'World')"

# Contains
fhir cql eval "'Hello World' contains 'llo'"

# Matches (regex)
fhir cql eval "Matches('Hello123', '[A-Za-z]+[0-9]+')"
fhir cql eval "Matches('test@email.com', '.*@.*\\..*')"
```

#### String Transformation

```bash
# Replace
fhir cql eval "Replace('Hello World', 'World', 'CQL')"
fhir cql eval "ReplaceMatches('Hello123', '[0-9]', 'X')"

# Split
fhir cql eval "Split('a,b,c,d', ',')"

# Combine (join)
fhir cql eval "Combine({'a', 'b', 'c'}, '-')"
fhir cql eval "Combine({'apple', 'banana', 'cherry'}, ', ')"
```

#### String Library Example

Save as `strings.cql`:

```cql
library StringExamples version '1.0'

define FullName: 'John Robert Smith'
define Email: 'john.smith@example.com'
define Phone: '(555) 123-4567'

// Name parsing
define FirstName: Substring(FullName, 0, PositionOf(' ', FullName))
define NameParts: Split(FullName, ' ')
define LastName: Last(NameParts)
define MiddleName: NameParts[1]

// Email parsing
define EmailUser: Substring(Email, 0, PositionOf('@', Email))
define EmailDomain: Substring(Email, PositionOf('@', Email) + 1)
define IsValidEmail: Matches(Email, '.*@.*\\..*')

// Phone formatting
define PhoneDigits: ReplaceMatches(Phone, '[^0-9]', '')
define FormattedPhone:
    '(' + Substring(PhoneDigits, 0, 3) + ') ' +
    Substring(PhoneDigits, 3, 3) + '-' +
    Substring(PhoneDigits, 6, 4)

// Name formatting
define FormalName: LastName + ', ' + FirstName
define Initials:
    Substring(FirstName, 0, 1) + '.' +
    Substring(MiddleName, 0, 1) + '.' +
    Substring(LastName, 0, 1) + '.'

// String checks
define IsLongName: Length(FullName) > 20
define HasMiddleName: Count(NameParts) > 2

// Case transformations
define UpperName: Upper(FullName)
define LowerEmail: Lower(Email)
```

```bash
fhir cql run strings.cql
```

---

### Math Functions

Mathematical operations beyond basic arithmetic.

#### Basic Math

```bash
# Absolute value
fhir cql eval "Abs(-42)"

# Ceiling and Floor
fhir cql eval "Ceiling(4.2)"
fhir cql eval "Floor(4.8)"

# Round
fhir cql eval "Round(3.14159, 2)"
fhir cql eval "Round(3.5)"

# Truncate
fhir cql eval "Truncate(3.9)"
fhir cql eval "Truncate(-3.9)"
```

#### Powers and Roots

```bash
# Power
fhir cql eval "Power(2, 10)"
fhir cql eval "Power(10, 3)"

# Square root (using Power)
fhir cql eval "Power(16, 0.5)"

# Logarithm
fhir cql eval "Ln(2.718281828)"
fhir cql eval "Log(100, 10)"
```

#### Trigonometry

```bash
# Basic trig
fhir cql eval "Sin(0)"
fhir cql eval "Cos(0)"
fhir cql eval "Tan(0)"

# Inverse trig
fhir cql eval "Asin(0)"
fhir cql eval "Acos(1)"
fhir cql eval "Atan(0)"
```

#### Math Library Example

Save as `math.cql`:

```cql
library MathExamples version '1.0'

// Constants
define Pi: 3.14159265359
define E: 2.71828182846

// Circle calculations
define Radius: 5.0
define CircleArea: Pi * Power(Radius, 2)
define Circumference: 2 * Pi * Radius
define Diameter: 2 * Radius

// Sphere calculations
define SphereVolume: (4.0 / 3.0) * Pi * Power(Radius, 3)
define SphereSurfaceArea: 4 * Pi * Power(Radius, 2)

// Quadratic formula: ax^2 + bx + c = 0
define a: 1.0
define b: -5.0
define c: 6.0
define Discriminant: Power(b, 2) - 4 * a * c
define HasRealRoots: Discriminant >= 0

// Financial: Compound interest
// A = P(1 + r/n)^(nt)
define Principal: 1000.0
define Rate: 0.05
define CompoundsPerYear: 12
define Years: 10
define FutureValue: Round(
    Principal * Power(1 + Rate / CompoundsPerYear, CompoundsPerYear * Years),
    2
)

// Statistics helper functions
define Numbers: {12, 15, 18, 22, 25, 30, 35}
define Mean: Avg(Numbers)
define SumOfSquaredDiffs: Sum(
    from n in Numbers
    return Power(n - Mean, 2)
)
define Variance: SumOfSquaredDiffs / Count(Numbers)
define StandardDeviation: Round(Power(Variance, 0.5), 2)

// Distance formula: sqrt((x2-x1)^2 + (y2-y1)^2)
define function Distance(x1 Decimal, y1 Decimal, x2 Decimal, y2 Decimal) returns Decimal:
    Round(Power(Power(x2 - x1, 2) + Power(y2 - y1, 2), 0.5), 2)

define TestDistance: Distance(0.0, 0.0, 3.0, 4.0)
```

```bash
fhir cql run math.cql
```

---

### Clinical Calculations

Real-world medical formulas.

#### BMI Calculation

Save as `bmi-calc.cql`:

```cql
library BMICalculation version '1.0'

using FHIR version '4.0.1'

context Patient

// BMI = weight(kg) / height(m)^2
define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
    if weightKg is null or heightCm is null or heightCm = 0 then null
    else Round(weightKg / Power(heightCm / 100, 2), 1)

define function BMICategory(bmi Decimal) returns String:
    if bmi is null then 'Unknown'
    else if bmi < 18.5 then 'Underweight'
    else if bmi < 25.0 then 'Normal'
    else if bmi < 30.0 then 'Overweight'
    else if bmi < 35.0 then 'Obese Class I'
    else if bmi < 40.0 then 'Obese Class II'
    else 'Obese Class III'

// Test values
define TestWeight: 70.0
define TestHeight: 175.0
define TestBMI: CalculateBMI(TestWeight, TestHeight)
define TestCategory: BMICategory(TestBMI)

// Ideal body weight (Devine formula)
define function IdealBodyWeight(heightCm Decimal, isFemale Boolean) returns Decimal:
    if heightCm is null then null
    else if isFemale then
        Round(45.5 + (2.3 * ((heightCm / 2.54) - 60)), 1)
    else
        Round(50.0 + (2.3 * ((heightCm / 2.54) - 60)), 1)

define TestIdealWeight: IdealBodyWeight(TestHeight, false)
define WeightDifference: TestWeight - TestIdealWeight
```

#### eGFR Calculation

Save as `egfr-calc.cql`:

```cql
library EGFRCalculation version '1.0'

using FHIR version '4.0.1'

context Patient

// Simplified CKD-EPI formula
define function CalculateEGFR(
    creatinine Decimal,
    age Integer,
    isFemale Boolean,
    isBlack Boolean
) returns Integer:
    if creatinine is null or age is null or creatinine = 0 then null
    else
        let baseEGFR: 175 * Power(creatinine, -1.154) * Power(age, -0.203)
        let genderAdjusted: if isFemale then baseEGFR * 0.742 else baseEGFR
        let raceAdjusted: if isBlack then genderAdjusted * 1.212 else genderAdjusted
        return Truncate(raceAdjusted)

define function CKDStage(egfr Integer) returns String:
    if egfr is null then 'Unknown'
    else if egfr >= 90 then 'Stage 1 (Normal)'
    else if egfr >= 60 then 'Stage 2 (Mild)'
    else if egfr >= 45 then 'Stage 3a (Mild-Moderate)'
    else if egfr >= 30 then 'Stage 3b (Moderate-Severe)'
    else if egfr >= 15 then 'Stage 4 (Severe)'
    else 'Stage 5 (Kidney Failure)'

define function NeedsDoseAdjustment(egfr Integer) returns Boolean:
    egfr is not null and egfr < 60

// Test values
define TestCreatinine: 1.2
define TestAge: 65
define TestEGFR: CalculateEGFR(TestCreatinine, TestAge, false, false)
define TestCKDStage: CKDStage(TestEGFR)
define TestNeedsDoseAdj: NeedsDoseAdjustment(TestEGFR)
```

#### Temperature Conversion

Save as `temperature.cql`:

```cql
library TemperatureConversion version '1.0'

// Conversion functions
define function CelsiusToFahrenheit(c Decimal) returns Decimal:
    if c is null then null
    else Round(c * 9.0 / 5.0 + 32, 1)

define function FahrenheitToCelsius(f Decimal) returns Decimal:
    if f is null then null
    else Round((f - 32) * 5.0 / 9.0, 1)

define function CelsiusToKelvin(c Decimal) returns Decimal:
    if c is null then null
    else Round(c + 273.15, 2)

// Clinical interpretation
define function FeverStatus(tempCelsius Decimal) returns String:
    if tempCelsius is null then 'Unknown'
    else if tempCelsius < 35.0 then 'Hypothermia'
    else if tempCelsius < 36.1 then 'Low'
    else if tempCelsius < 37.2 then 'Normal'
    else if tempCelsius < 38.0 then 'Low-grade fever'
    else if tempCelsius < 39.0 then 'Moderate fever'
    else if tempCelsius < 40.0 then 'High fever'
    else 'Hyperpyrexia'

// Test values
define BodyTempC: 37.5
define BodyTempF: CelsiusToFahrenheit(BodyTempC)
define FeverCheck: FeverStatus(BodyTempC)

// Common reference temperatures
define FreezingC: 0.0
define FreezingF: CelsiusToFahrenheit(FreezingC)
define BoilingC: 100.0
define BoilingF: CelsiusToFahrenheit(BoilingC)
define NormalBodyC: 37.0
define NormalBodyF: CelsiusToFahrenheit(NormalBodyC)
```

---

### Risk Score Calculations

Clinical risk assessment algorithms.

#### CHA2DS2-VASc Score

Save as `chadsvasc.cql`:

```cql
library CHA2DS2VASc version '1.0'

/*
 * CHA2DS2-VASc Score for stroke risk in atrial fibrillation
 *
 * C - Congestive heart failure: 1 point
 * H - Hypertension: 1 point
 * A2 - Age >= 75: 2 points
 * D - Diabetes: 1 point
 * S2 - Stroke/TIA history: 2 points
 * V - Vascular disease: 1 point
 * A - Age 65-74: 1 point
 * Sc - Sex category (female): 1 point
 */

define function CalculateCHA2DS2VASc(
    hasHeartFailure Boolean,
    hasHypertension Boolean,
    age Integer,
    hasDiabetes Boolean,
    hasStrokeOrTIA Boolean,
    hasVascularDisease Boolean,
    isFemale Boolean
) returns Integer:
    (if hasHeartFailure then 1 else 0)
    + (if hasHypertension then 1 else 0)
    + (if age >= 75 then 2 else if age >= 65 then 1 else 0)
    + (if hasDiabetes then 1 else 0)
    + (if hasStrokeOrTIA then 2 else 0)
    + (if hasVascularDisease then 1 else 0)
    + (if isFemale then 1 else 0)

define function StrokeRiskCategory(score Integer) returns String:
    if score is null then 'Unknown'
    else if score = 0 then 'Low (0.2% annual stroke risk)'
    else if score = 1 then 'Low-Moderate (0.6% annual stroke risk)'
    else if score = 2 then 'Moderate (2.2% annual stroke risk)'
    else if score = 3 then 'Moderate-High (3.2% annual stroke risk)'
    else if score = 4 then 'High (4.8% annual stroke risk)'
    else 'Very High (>6% annual stroke risk)'

define function AnticoagulationRecommended(score Integer, isFemale Boolean) returns String:
    // For females, score of 1 (sex alone) doesn't warrant anticoag
    let adjustedScore: if isFemale and score = 1 then 0 else score
    return case
        when adjustedScore = 0 then 'No anticoagulation recommended'
        when adjustedScore = 1 then 'Consider anticoagulation'
        else 'Anticoagulation recommended'
    end

// Test case: 70-year-old female with hypertension and diabetes
define TestScore: CalculateCHA2DS2VASc(
    false,  // heart failure
    true,   // hypertension
    70,     // age
    true,   // diabetes
    false,  // stroke/TIA
    false,  // vascular disease
    true    // female
)

define TestRiskCategory: StrokeRiskCategory(TestScore)
define TestRecommendation: AnticoagulationRecommended(TestScore, true)
```

#### Framingham Risk Score (Simplified)

Save as `framingham.cql`:

```cql
library FraminghamRisk version '1.0'

/*
 * Simplified Framingham Risk Score
 * Estimates 10-year cardiovascular disease risk
 */

define function FraminghamAgePoints(age Integer, isFemale Boolean) returns Integer:
    if isFemale then
        case
            when age < 35 then -9
            when age < 40 then -4
            when age < 45 then 0
            when age < 50 then 3
            when age < 55 then 6
            when age < 60 then 7
            when age < 65 then 8
            when age < 70 then 8
            when age < 75 then 8
            else 8
        end
    else
        case
            when age < 35 then -1
            when age < 40 then 0
            when age < 45 then 1
            when age < 50 then 2
            when age < 55 then 3
            when age < 60 then 4
            when age < 65 then 5
            when age < 70 then 6
            when age < 75 then 7
            else 8
        end

define function SmokingPoints(isSmoker Boolean, isFemale Boolean) returns Integer:
    if not isSmoker then 0
    else if isFemale then 3
    else 4

define function DiabetesPoints(hasDiabetes Boolean, isFemale Boolean) returns Integer:
    if not hasDiabetes then 0
    else if isFemale then 4
    else 3

define function CalculateFraminghamPoints(
    age Integer,
    isFemale Boolean,
    isSmoker Boolean,
    hasDiabetes Boolean,
    totalCholesterol Integer,
    hdlCholesterol Integer,
    systolicBP Integer,
    onBPMeds Boolean
) returns Integer:
    FraminghamAgePoints(age, isFemale)
    + SmokingPoints(isSmoker, isFemale)
    + DiabetesPoints(hasDiabetes, isFemale)
    // Simplified - full calculation includes cholesterol and BP points

define function TenYearRisk(points Integer, isFemale Boolean) returns String:
    // Simplified risk categories
    case
        when points < 5 then 'Low (<5%)'
        when points < 10 then 'Low-Moderate (5-10%)'
        when points < 15 then 'Moderate (10-15%)'
        when points < 20 then 'Moderate-High (15-20%)'
        else 'High (>20%)'
    end

// Test case
define TestPoints: CalculateFraminghamPoints(
    55,     // age
    false,  // female
    true,   // smoker
    false,  // diabetes
    220,    // total cholesterol
    45,     // HDL
    140,    // systolic BP
    false   // on BP meds
)

define TestRisk: TenYearRisk(TestPoints, false)
```

---

### Advanced Query Examples

Complex queries for real-world scenarios.

#### Multi-Source Queries

```cql
library QueryExamples version '1.0'

using FHIR version '4.0.1'

context Patient

// Single source query
define ActiveConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'

// Multiple conditions
define SeriousConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'
            and C.severity.coding.code = 'severe'

// Query with let
define ConditionsWithAge:
    from C in [Condition]
    let onsetAge: years between Patient.birthDate and C.onset
    where onsetAge is not null
    return Tuple {
        condition: C.code.coding.first().display,
        onsetAge: onsetAge
    }

// Multi-source query
define ConditionMedications:
    from C in [Condition],
         M in [MedicationRequest]
    where M.reasonReference.reference = 'Condition/' + C.id
    return Tuple {
        condition: C.code.coding.first().display,
        medication: M.medication.coding.first().display
    }

// Aggregate query
define ConditionCountByStatus:
    from C in [Condition]
    return all C.clinicalStatus.coding.first().code

// Sort and limit
define RecentConditions:
    Take(
        [Condition] C
            sort by recorded desc,
        5
    )

// First and Last
define OldestCondition:
    First([Condition] C sort by onset)

define NewestCondition:
    Last([Condition] C sort by onset)
```

#### Observation Queries

```cql
library ObservationQueries version '1.0'

using FHIR version '4.0.1'

context Patient

// Most recent observation by type
define function MostRecentObs(loincCode String):
    Last(
        [Observation] O
            where O.code.coding.code contains loincCode
                and O.status = 'final'
            sort by effective
    )

// Blood pressure
define MostRecentSystolic: MostRecentObs('8480-6')
define MostRecentDiastolic: MostRecentObs('8462-4')

define BloodPressure:
    if MostRecentSystolic is not null and MostRecentDiastolic is not null then
        Tuple {
            systolic: MostRecentSystolic.value.value,
            diastolic: MostRecentDiastolic.value.value
        }
    else null

// Vital signs trend (last 5)
define RecentBPReadings:
    from O in Take(
        [Observation] O
            where O.code.coding.code contains '8480-6'
                and O.status = 'final'
            sort by effective desc,
        5
    )
    return Tuple {
        date: O.effective,
        value: O.value.value
    }

// Labs in abnormal range
define AbnormalLabs:
    [Observation] O
        where O.status = 'final'
            and O.interpretation.coding.code != 'N'

// Calculate average of recent values
define RecentGlucoseValues:
    from O in [Observation] O
        where O.code.coding.code contains '2339-0'
            and O.status = 'final'
            and O.effective after Today() - 90 days
    return O.value.value

define AverageGlucose:
    if Count(RecentGlucoseValues) > 0 then
        Round(Avg(RecentGlucoseValues), 1)
    else null
```

---

### Terminology Examples

Working with codes, valuesets, and concepts.

```cql
library TerminologyExamples version '1.0'

using FHIR version '4.0.1'

// Define code systems
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "LOINC": 'http://loinc.org'
codesystem "ICD10": 'http://hl7.org/fhir/sid/icd-10-cm'
codesystem "RxNorm": 'http://www.nlm.nih.gov/research/umls/rxnorm'

// Define individual codes
code "Type 2 Diabetes": '44054006' from "SNOMED" display 'Type 2 diabetes mellitus'
code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'
code "Metformin": '6809' from "RxNorm" display 'metformin'

// Define valuesets (would be expanded from external source)
valueset "Diabetes Conditions": 'http://example.org/ValueSet/diabetes'
valueset "Diabetes Medications": 'http://example.org/ValueSet/diabetes-meds'
valueset "Glucose Labs": 'http://example.org/ValueSet/glucose-labs'

// Define concepts (groups of equivalent codes)
concept "Diabetes Concept":
    {"Type 2 Diabetes"}
    display 'Diabetes Mellitus'

context Patient

// Check for specific condition code
define HasDiabetesCode:
    exists(
        [Condition: "Type 2 Diabetes"]
    )

// Check for condition in valueset
define HasDiabetesValueSet:
    exists(
        [Condition: "Diabetes Conditions"]
    )

// Get medications from valueset
define DiabetesMedications:
    [MedicationRequest: "Diabetes Medications"]

// Get specific lab results
define HbA1cResults:
    [Observation: "HbA1c"] O
        where O.status = 'final'

// Most recent HbA1c
define MostRecentHbA1c:
    Last(HbA1cResults O sort by effective)

// Code equivalence checking
define function CodeEquals(code1 Code, code2 Code) returns Boolean:
    code1.code = code2.code
        and code1.system = code2.system

// Check if observation matches a specific code
define IsHbA1cObservation:
    exists(
        [Observation] O
            where O.code.coding.code = '4548-4'
                and O.code.coding.system = 'http://loinc.org'
    )
```

---

### Complete Clinical Library

A comprehensive example combining multiple concepts.

Save as `diabetes-management.cql`:

```cql
library DiabetesManagement version '1.0.0'

using FHIR version '4.0.1'

// Code Systems
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "LOINC": 'http://loinc.org'

// Codes
code "Type2DM": '44054006' from "SNOMED"
code "HbA1c": '4548-4' from "LOINC"
code "FastingGlucose": '1558-6' from "LOINC"
code "RandomGlucose": '2339-0' from "LOINC"

// Parameters
parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// =============================================
// Patient Demographics
// =============================================

define PatientAge: years between Patient.birthDate and Today()
define PatientGender: Patient.gender

// =============================================
// Diabetes Status
// =============================================

define DiabetesConditions:
    [Condition] C
        where C.clinicalStatus.coding.code = 'active'
            and C.code.coding.code = '44054006'

define HasDiabetes: exists(DiabetesConditions)

// =============================================
// Lab Results
// =============================================

define HbA1cTests:
    [Observation: "HbA1c"] O
        where O.status = 'final'
            and O.effective during "Measurement Period"

define MostRecentHbA1c:
    Last(HbA1cTests O sort by effective)

define MostRecentHbA1cValue:
    MostRecentHbA1c.value.value

define MostRecentHbA1cDate:
    MostRecentHbA1c.effective

define AllHbA1cValues:
    from O in HbA1cTests
    return O.value.value

define AverageHbA1c:
    if Count(AllHbA1cValues) > 0 then
        Round(Avg(AllHbA1cValues), 1)
    else null

define HbA1cTrend:
    case
        when Count(AllHbA1cValues) < 2 then 'Insufficient data'
        when Last(AllHbA1cValues) < First(AllHbA1cValues) - 0.5 then 'Improving'
        when Last(AllHbA1cValues) > First(AllHbA1cValues) + 0.5 then 'Worsening'
        else 'Stable'
    end

// =============================================
// Control Status
// =============================================

define HbA1cControlStatus:
    case
        when MostRecentHbA1cValue is null then 'No recent test'
        when MostRecentHbA1cValue < 5.7 then 'Normal'
        when MostRecentHbA1cValue < 6.5 then 'Prediabetes range'
        when MostRecentHbA1cValue < 7.0 then 'Well controlled'
        when MostRecentHbA1cValue < 8.0 then 'Moderately controlled'
        when MostRecentHbA1cValue < 9.0 then 'Poorly controlled'
        else 'Very poorly controlled'
    end

define MeetsControlTarget:
    MostRecentHbA1cValue is not null and MostRecentHbA1cValue < 7.0

// =============================================
// Testing Compliance
// =============================================

define HbA1cTestCount:
    Count(HbA1cTests)

define DaysUntilTestDue:
    if MostRecentHbA1cDate is null then 0
    else
        let daysSinceTest: days between MostRecentHbA1cDate and Today()
        return Maximum(0, 90 - daysSinceTest)

define TestingCompliant:
    HbA1cTestCount >= 2

// =============================================
// Age-Adjusted Targets
// =============================================

define HbA1cTarget:
    case
        when PatientAge < 40 then 6.5
        when PatientAge < 65 then 7.0
        when PatientAge < 75 then 7.5
        else 8.0
    end

define MeetsAgeAdjustedTarget:
    MostRecentHbA1cValue is not null
        and MostRecentHbA1cValue <= HbA1cTarget

// =============================================
// Alerts and Recommendations
// =============================================

define Alerts:
    List<String> {
        if MostRecentHbA1cValue is null then 'No HbA1c on file - order test' else null,
        if MostRecentHbA1cValue >= 9.0 then 'URGENT: HbA1c critically elevated' else null,
        if DaysUntilTestDue = 0 then 'HbA1c test overdue' else null,
        if not TestingCompliant then 'Below recommended testing frequency' else null,
        if HbA1cTrend = 'Worsening' then 'HbA1c trend worsening - review treatment' else null
    }

define ActiveAlerts:
    from A in Alerts where A is not null return A

// =============================================
// Quality Measure Populations
// =============================================

define "Initial Population":
    HasDiabetes and PatientAge >= 18 and PatientAge <= 75

define "Denominator":
    "Initial Population"

define "Denominator Exclusion":
    PatientAge > 75

define "Numerator":
    "Initial Population" and MeetsControlTarget

define "Stratifier Age Group":
    case
        when PatientAge < 40 then '18-39'
        when PatientAge < 65 then '40-64'
        else '65-75'
    end

// =============================================
// Summary Report
// =============================================

define PatientSummary:
    Tuple {
        age: PatientAge,
        gender: PatientGender,
        hasDiabetes: HasDiabetes,
        mostRecentHbA1c: MostRecentHbA1cValue,
        hbA1cDate: MostRecentHbA1cDate,
        controlStatus: HbA1cControlStatus,
        meetsTarget: MeetsAgeAdjustedTarget,
        target: HbA1cTarget,
        trend: HbA1cTrend,
        testCount: HbA1cTestCount,
        alerts: ActiveAlerts
    }
```

```bash
fhir cql run diabetes-management.cql --data patient-bundle.json
```

---

## Quick Reference

### Library Structure
```cql
library Name version '1.0.0'
using FHIR version '4.0.1'
context Patient
define DefinitionName: expression
```

### Data Types
| Type | Example |
|------|---------|
| String | `'hello'` |
| Integer | `42` |
| Decimal | `3.14` |
| Boolean | `true` |
| Date | `@2024-06-15` |
| DateTime | `@2024-06-15T10:30:00` |
| List | `{1, 2, 3}` |
| Interval | `Interval[1, 10]` |

### Common Functions
| Function | Description |
|----------|-------------|
| `Sum(list)` | Sum of numbers |
| `Avg(list)` | Average |
| `Count(list)` | Count elements |
| `First(list)` | First element |
| `Last(list)` | Last element |
| `exists(list)` | Has elements |
| `Today()` | Current date |
| `years between` | Duration in years |

### Query Syntax
```cql
from item in collection
let temp: expression
where condition
return result
sort by field
```

---

## Next Steps

- Explore [examples/cql/](../examples/cql/) for more examples
- Read the [CQL API](cql-api.md) for Python integration
- Read the [CQL Specification](https://cql.hl7.org/) for complete details
- Try the existing example libraries:

```bash
fhir cql run examples/cql/01_hello_world.cql
fhir cql run examples/cql/09_string_functions.cql
fhir cql run examples/cql/10_math_functions.cql
fhir cql run examples/cql/16_clinical_calculations.cql
```
