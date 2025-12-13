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

### What You Learned

- `using FHIR version '4.0.1'` declares FHIR model
- `context Patient` scopes to patient
- Access patient properties with `Patient.property`
- `[ResourceType]` retrieves resources
- `--data` loads JSON data

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
