# FHIRPath Step-by-Step Tutorial

A hands-on guide to learning FHIRPath from scratch.

## Prerequisites

- Python 3.13+ installed
- This library installed (`make install`)
- Basic understanding of JSON

## Tutorial Overview

1. [Step 1: Your First Expression](#step-1-your-first-expression)
2. [Step 2: Navigating Resources](#step-2-navigating-resources)
3. [Step 3: Working with Arrays](#step-3-working-with-arrays)
4. [Step 4: Filtering with where()](#step-4-filtering-with-where)
5. [Step 5: String Operations](#step-5-string-operations)
6. [Step 6: Boolean Expressions](#step-6-boolean-expressions)
7. [Step 7: Combining Data](#step-7-combining-data)
8. [Step 8: Real-World Examples](#step-8-real-world-examples)

---

## Step 1: Your First Expression

### Goal

Learn to run a simple FHIRPath expression.

### Create a Test File

Save this as `patient.json`:

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
  "gender": "male",
  "birthDate": "1990-05-15"
}
```

### Run Your First Command

```bash
fhir fhirpath eval "Patient.id" -r patient.json
```

Output:
```
'example'
```

### Try It Yourself

Run these commands and observe the output:

```bash
fhir fhirpath eval "Patient.gender" -r patient.json
fhir fhirpath eval "Patient.birthDate" -r patient.json
fhir fhirpath eval "Patient.resourceType" -r patient.json
```

### What You Learned

- FHIRPath uses dot notation to access properties
- The resource type (Patient) starts the path
- Simple properties return their values directly

---

## Step 2: Navigating Resources

### Goal

Learn to navigate nested properties.

### Understanding the Structure

Look at the `name` field in our patient - it's an array of objects:

```json
"name": [
  {
    "use": "official",
    "family": "Smith",
    "given": ["John", "Robert"]
  }
]
```

### Navigate to Nested Properties

```bash
# Get the name array
fhir fhirpath eval "Patient.name" -r patient.json

# Get family names (from all name entries)
fhir fhirpath eval "Patient.name.family" -r patient.json
```

Output:
```
['Smith']
```

### Go Deeper

```bash
# Get given names
fhir fhirpath eval "Patient.name.given" -r patient.json
```

Output:
```
['John', 'Robert']
```

### Add More Data

Update `patient.json` with an address:

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
  "gender": "male",
  "birthDate": "1990-05-15",
  "address": [
    {
      "use": "home",
      "city": "Boston",
      "state": "MA",
      "postalCode": "02101"
    }
  ]
}
```

### Try It Yourself

```bash
fhir fhirpath eval "Patient.address.city" -r patient.json
fhir fhirpath eval "Patient.address.state" -r patient.json
fhir fhirpath eval "Patient.address.postalCode" -r patient.json
```

### What You Learned

- Dot notation works through nested objects
- Arrays are automatically traversed
- Multiple values return as a list

---

## Step 3: Working with Arrays

### Goal

Learn to select specific elements from arrays.

### First and Last

```bash
# Get first given name
fhir fhirpath eval "Patient.name.given.first()" -r patient.json
```

Output:
```
'John'
```

```bash
# Get last given name
fhir fhirpath eval "Patient.name.given.last()" -r patient.json
```

Output:
```
'Robert'
```

### Take and Skip

```bash
# Get first N elements
fhir fhirpath eval "Patient.name.given.take(1)" -r patient.json

# Skip first N elements
fhir fhirpath eval "Patient.name.given.skip(1)" -r patient.json
```

### Counting

```bash
# Count elements
fhir fhirpath eval "Patient.name.given.count()" -r patient.json
```

Output:
```
2
```

### Check if Empty

```bash
# Check if array is empty
fhir fhirpath eval "Patient.name.empty()" -r patient.json

# Check if array has elements
fhir fhirpath eval "Patient.name.exists()" -r patient.json
```

### Add More Names

Update `patient.json` with multiple names:

```json
{
  "resourceType": "Patient",
  "id": "example",
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["John", "Robert"]
    },
    {
      "use": "nickname",
      "given": ["Johnny"]
    }
  ],
  "gender": "male",
  "birthDate": "1990-05-15"
}
```

### Try It Yourself

```bash
fhir fhirpath eval "Patient.name.count()" -r patient.json
fhir fhirpath eval "Patient.name.family" -r patient.json
fhir fhirpath eval "Patient.name.given" -r patient.json
fhir fhirpath eval "Patient.name.first().family" -r patient.json
```

### What You Learned

- `first()` and `last()` get single elements
- `take(n)` and `skip(n)` slice arrays
- `count()` returns the number of elements
- `empty()` and `exists()` check for content

---

## Step 4: Filtering with where()

### Goal

Learn to filter collections based on conditions.

### Basic Filtering

Using our patient with multiple names:

```bash
# Get only official names
fhir fhirpath eval "Patient.name.where(use = 'official')" -r patient.json
```

### Chain with Property Access

```bash
# Get family name from official name only
fhir fhirpath eval "Patient.name.where(use = 'official').family" -r patient.json
```

Output:
```
['Smith']
```

### Create an Observation File

Save this as `observation.json`:

```json
{
  "resourceType": "Observation",
  "id": "glucose-1",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "2339-0",
        "display": "Glucose"
      }
    ]
  },
  "valueQuantity": {
    "value": 95,
    "unit": "mg/dL"
  }
}
```

### Filter on Nested Properties

```bash
# Check the status
fhir fhirpath eval "Observation.status = 'final'" -r observation.json

# Get coding with specific system
fhir fhirpath eval "Observation.code.coding.where(system = 'http://loinc.org')" -r observation.json
```

### Multiple Conditions

```bash
# Multiple conditions with 'and'
fhir fhirpath eval "Observation.code.coding.where(system = 'http://loinc.org' and code = '2339-0')" -r observation.json
```

### Try It Yourself

```bash
# Get the code value
fhir fhirpath eval "Observation.code.coding.where(system = 'http://loinc.org').code" -r observation.json

# Get the display text
fhir fhirpath eval "Observation.code.coding.where(system = 'http://loinc.org').display" -r observation.json
```

### What You Learned

- `where()` filters based on conditions
- Conditions use `=` for equality
- Multiple conditions combine with `and`
- Can chain property access after filtering

---

## Step 5: String Operations

### Goal

Learn string manipulation functions.

### Case Conversion

```bash
fhir fhirpath eval "Patient.name.family.lower()" -r patient.json
fhir fhirpath eval "Patient.name.family.upper()" -r patient.json
```

### Substring

```bash
# Get first 2 characters
fhir fhirpath eval "Patient.name.family.first().substring(0, 2)" -r patient.json
```

Output:
```
'Sm'
```

### Pattern Matching

```bash
# Check if starts with
fhir fhirpath eval "Patient.name.family.first().startsWith('Sm')" -r patient.json

# Check if contains
fhir fhirpath eval "Patient.name.family.first().contains('mit')" -r patient.json

# Check if ends with
fhir fhirpath eval "Patient.name.family.first().endsWith('th')" -r patient.json
```

### Length

```bash
fhir fhirpath eval "Patient.name.family.first().length()" -r patient.json
```

### String Concatenation

```bash
# Combine strings
fhir fhirpath eval "Patient.name.given.first() + ' ' + Patient.name.family.first()" -r patient.json
```

Output:
```
'John Smith'
```

### Try It Yourself

```bash
# Get the first letter of the family name
fhir fhirpath eval "Patient.name.family.first().substring(0, 1)" -r patient.json

# Check if any given name contains 'ob'
fhir fhirpath eval "Patient.name.given.where(contains('ob'))" -r patient.json
```

### What You Learned

- `lower()` and `upper()` change case
- `substring(start, length)` extracts parts
- `startsWith()`, `contains()`, `endsWith()` check patterns
- `+` concatenates strings

---

## Step 6: Boolean Expressions

### Goal

Learn to write conditions and comparisons.

### Comparison Operators

```bash
# Equality
fhir fhirpath eval "Patient.gender = 'male'" -r patient.json

# Not equal
fhir fhirpath eval "Patient.gender != 'female'" -r patient.json
```

### Numeric Comparisons

Using our observation file:

```bash
# Greater than
fhir fhirpath eval "Observation.valueQuantity.value > 90" -r observation.json

# Less than or equal
fhir fhirpath eval "Observation.valueQuantity.value <= 100" -r observation.json
```

### Combining with and/or

```bash
# Both conditions true
fhir fhirpath eval "Observation.status = 'final' and Observation.valueQuantity.value > 50" -r observation.json

# Either condition true
fhir fhirpath eval "Patient.gender = 'male' or Patient.gender = 'female'" -r patient.json
```

### Negation

```bash
# Not
fhir fhirpath eval "Patient.gender != 'female'" -r patient.json
fhir fhirpath eval "not(Patient.gender = 'female')" -r patient.json
```

### Existence Checks

```bash
# Check if property exists
fhir fhirpath eval "Patient.birthDate.exists()" -r patient.json

# Check if missing
fhir fhirpath eval "Patient.deceased.exists()" -r patient.json
```

### Try It Yourself

Create a condition file `condition.json`:

```json
{
  "resourceType": "Condition",
  "id": "diabetes",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active"
      }
    ]
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
```

```bash
# Check if condition is active
fhir fhirpath eval "Condition.clinicalStatus.coding.code.first() = 'active'" -r condition.json

# Check the SNOMED code
fhir fhirpath eval "Condition.code.coding.where(system = 'http://snomed.info/sct').code" -r condition.json
```

### What You Learned

- `=`, `!=`, `>`, `<`, `>=`, `<=` for comparisons
- `and`, `or` combine conditions
- `not()` negates conditions
- `exists()` checks for presence

---

## Step 7: Combining Data

### Goal

Learn to combine and transform data.

### Union Operator

```bash
# Combine two lists
fhir fhirpath eval "Patient.name.given | Patient.name.family" -r patient.json
```

### Distinct

```bash
# Remove duplicates
fhir fhirpath eval "(Patient.name.given | Patient.name.given).distinct()" -r patient.json
```

### All/Any Checks

```bash
# Check if all names have a family
fhir fhirpath eval "Patient.name.all(family.exists())" -r patient.json

# Check if any name is a nickname
fhir fhirpath eval "Patient.name.where(use = 'nickname').exists()" -r patient.json
```

### Transform with select

Save multiple observations as `observations.json`:

```json
{
  "resourceType": "Bundle",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-1",
        "status": "final",
        "valueQuantity": {"value": 95, "unit": "mg/dL"}
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-2",
        "status": "final",
        "valueQuantity": {"value": 102, "unit": "mg/dL"}
      }
    }
  ]
}
```

```bash
# Get all observation values
fhir fhirpath eval "Bundle.entry.resource.valueQuantity.value" -r observations.json
```

### Try It Yourself

```bash
# Combine family and given into full name
fhir fhirpath eval "Patient.name.first().given.first() + ' ' + Patient.name.first().family" -r patient.json

# Get all unique values from observations
fhir fhirpath eval "Bundle.entry.resource.valueQuantity.value.distinct()" -r observations.json
```

### What You Learned

- `|` creates a union of lists
- `distinct()` removes duplicates
- `all()` checks if condition is true for all elements
- Paths work through Bundle.entry

---

## Step 8: Real-World Examples

### Goal

Apply FHIRPath to real clinical scenarios.

### Example 1: Find Active Conditions

Save this bundle as `patient-data.json`:

```json
{
  "resourceType": "Bundle",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Smith", "given": ["John"]}],
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
          "coding": [{"display": "Hypertension"}]
        }
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "condition-2",
        "subject": {"reference": "Patient/patient-1"},
        "clinicalStatus": {
          "coding": [{"code": "resolved"}]
        },
        "code": {
          "coding": [{"display": "Common Cold"}]
        }
      }
    }
  ]
}
```

Find active conditions:

```bash
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Condition' and clinicalStatus.coding.code = 'active').code.coding.display" -r patient-data.json
```

### Example 2: Get Patient's Age Data

```bash
# Get birth date
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Patient').birthDate" -r patient-data.json

# Get patient name
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Patient').name.given.first() + ' ' + Bundle.entry.resource.where(resourceType = 'Patient').name.family.first()" -r patient-data.json
```

### Example 3: Count Resources

```bash
# Count all conditions
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Condition').count()" -r patient-data.json

# Count active conditions
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Condition' and clinicalStatus.coding.code = 'active').count()" -r patient-data.json
```

### Example 4: Check for Specific Condition

```bash
# Does patient have hypertension?
fhir fhirpath eval "Bundle.entry.resource.where(resourceType = 'Condition').code.coding.where(display = 'Hypertension').exists()" -r patient-data.json
```

### Using the Interactive REPL

Start the REPL for experimentation:

```bash
fhir fhirpath repl -r patient-data.json
```

In the REPL, type expressions interactively:

```
> Bundle.entry.count()
3

> Bundle.entry.resource.resourceType
['Patient', 'Condition', 'Condition']

> quit
```

### What You Learned

- Complex filters combine multiple conditions
- Bundles contain resources in `entry.resource`
- REPL mode allows interactive exploration

---

## Quick Reference

### Navigation
| Expression | Description |
|------------|-------------|
| `Resource.property` | Access property |
| `property.nested` | Access nested |
| `array.first()` | First element |
| `array.last()` | Last element |
| `array[n]` | Element at index |

### Filtering
| Expression | Description |
|------------|-------------|
| `where(condition)` | Filter by condition |
| `exists()` | Has elements |
| `empty()` | No elements |
| `count()` | Number of elements |

### Strings
| Expression | Description |
|------------|-------------|
| `lower()` | Lowercase |
| `upper()` | Uppercase |
| `contains(str)` | Contains substring |
| `startsWith(str)` | Starts with |
| `substring(start, len)` | Extract part |

### Boolean
| Expression | Description |
|------------|-------------|
| `=`, `!=` | Equality |
| `>`, `<`, `>=`, `<=` | Comparison |
| `and`, `or` | Combine |
| `not()` | Negate |

---

## Next Steps

- Read the [CQL Tutorial](cql-tutorial.md) to learn CQL
- Explore [examples/fhirpath/](../examples/fhirpath/) for more examples
- Read the [FHIRPath Specification](http://hl7.org/fhirpath/) for complete details
