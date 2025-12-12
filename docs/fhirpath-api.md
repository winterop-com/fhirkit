# FHIRPath Python API

This guide covers using the FHIRPath evaluator as a Python library. Whether you're building a FHIR server, clinical decision support system, or data extraction pipeline, this API lets you evaluate FHIRPath expressions programmatically.

## Quick Start

```python
from fhir_cql import evaluate_fhirpath

# Load a FHIR resource (dict or JSON)
patient = {
    "resourceType": "Patient",
    "id": "example",
    "name": [{"family": "Smith", "given": ["John", "William"]}],
    "gender": "male",
    "birthDate": "1985-06-15"
}

# Evaluate FHIRPath expressions
result = evaluate_fhirpath("Patient.name.given", patient)
print(result)  # ['John', 'William']

result = evaluate_fhirpath("Patient.gender", patient)
print(result)  # ['male']

result = evaluate_fhirpath("Patient.birthDate", patient)
print(result)  # ['1985-06-15']
```

## Core Functions

### `evaluate_fhirpath(expression, resource, variables=None)`

The main function for evaluating FHIRPath expressions.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `expression` | `str` | The FHIRPath expression to evaluate |
| `resource` | `dict` | The FHIR resource (as a Python dict) |
| `variables` | `dict` | Optional variables available in the expression |

**Returns:** `list` - The result collection (FHIRPath always returns collections)

**Example:**

```python
from fhir_cql import evaluate_fhirpath

observation = {
    "resourceType": "Observation",
    "status": "final",
    "code": {
        "coding": [{"system": "http://loinc.org", "code": "85354-9"}]
    },
    "valueQuantity": {"value": 120, "unit": "mmHg"}
}

# Simple navigation
status = evaluate_fhirpath("Observation.status", observation)
# Returns: ['final']

# Nested navigation
code = evaluate_fhirpath("Observation.code.coding.code", observation)
# Returns: ['85354-9']

# With filtering
loinc = evaluate_fhirpath(
    "Observation.code.coding.where(system = 'http://loinc.org').code",
    observation
)
# Returns: ['85354-9']
```

### `parse_fhirpath(expression)`

Parses a FHIRPath expression and returns the AST (Abstract Syntax Tree).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `expression` | `str` | The FHIRPath expression to parse |

**Returns:** The parsed AST

**Example:**

```python
from fhir_cql import parse_fhirpath

# Parse an expression
ast = parse_fhirpath("Patient.name.given.first()")

# The AST can be inspected or used for analysis
print(type(ast))  # <class 'FHIRPathParser.ExpressionContext'>
```

## Working with Results

FHIRPath always returns collections (lists). Here are common patterns:

### Getting Single Values

```python
from fhir_cql import evaluate_fhirpath

patient = {"resourceType": "Patient", "gender": "male"}

# Results are always lists
result = evaluate_fhirpath("Patient.gender", patient)
print(result)  # ['male']

# Get single value safely
gender = result[0] if result else None
print(gender)  # 'male'

# Or use FHIRPath's single() function
result = evaluate_fhirpath("Patient.gender.single()", patient)
# Returns: ['male'] - but would error if multiple values
```

### Checking Existence

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "name": [{"family": "Smith"}]
}

# Check if element exists
has_name = evaluate_fhirpath("Patient.name.exists()", patient)
print(has_name)  # [True]

# Check if empty
no_telecom = evaluate_fhirpath("Patient.telecom.empty()", patient)
print(no_telecom)  # [True]

# Count elements
count = evaluate_fhirpath("Patient.name.count()", patient)
print(count)  # [1]
```

### Boolean Results

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "gender": "male",
    "active": True
}

# Comparisons return boolean
is_male = evaluate_fhirpath("Patient.gender = 'male'", patient)
print(is_male)  # [True]

# Combined conditions
result = evaluate_fhirpath(
    "Patient.gender = 'male' and Patient.active = true",
    patient
)
print(result)  # [True]

# Helper to get boolean
def get_bool(result):
    return result[0] if result else False

if get_bool(evaluate_fhirpath("Patient.active", patient)):
    print("Patient is active")
```

## Filtering and Selection

### Using `where()`

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "telecom": [
        {"system": "phone", "value": "555-1234", "use": "home"},
        {"system": "phone", "value": "555-5678", "use": "mobile"},
        {"system": "email", "value": "john@example.com"}
    ]
}

# Filter by condition
phones = evaluate_fhirpath(
    "Patient.telecom.where(system = 'phone').value",
    patient
)
print(phones)  # ['555-1234', '555-5678']

# Multiple conditions
mobile = evaluate_fhirpath(
    "Patient.telecom.where(system = 'phone' and use = 'mobile').value",
    patient
)
print(mobile)  # ['555-5678']
```

### Using `select()`

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "name": [
        {"family": "Smith", "given": ["John", "William"]},
        {"family": "Jones", "given": ["Johnny"]}
    ]
}

# Project specific fields
families = evaluate_fhirpath("Patient.name.select(family)", patient)
print(families)  # ['Smith', 'Jones']

# Complex projections
formatted = evaluate_fhirpath(
    "Patient.name.select(given.first() & ' ' & family)",
    patient
)
print(formatted)  # ['John Smith', 'Johnny Jones']
```

## Working with Different Resource Types

### Patient

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "id": "12345",
    "identifier": [
        {"system": "http://hospital.org", "value": "MRN12345"}
    ],
    "name": [{"family": "Smith", "given": ["John"]}],
    "birthDate": "1985-06-15",
    "address": [
        {"city": "Boston", "state": "MA", "postalCode": "02101"}
    ]
}

# Get MRN
mrn = evaluate_fhirpath(
    "Patient.identifier.where(system = 'http://hospital.org').value",
    patient
)

# Get full name
name = evaluate_fhirpath(
    "Patient.name.first().given.first() & ' ' & Patient.name.first().family",
    patient
)

# Get formatted address
address = evaluate_fhirpath(
    "Patient.address.first().city & ', ' & Patient.address.first().state",
    patient
)
```

### Observation (Vitals)

```python
from fhir_cql import evaluate_fhirpath

bp_observation = {
    "resourceType": "Observation",
    "status": "final",
    "code": {
        "coding": [{"system": "http://loinc.org", "code": "85354-9"}]
    },
    "component": [
        {
            "code": {"coding": [{"code": "8480-6"}]},
            "valueQuantity": {"value": 120, "unit": "mmHg"}
        },
        {
            "code": {"coding": [{"code": "8462-4"}]},
            "valueQuantity": {"value": 80, "unit": "mmHg"}
        }
    ]
}

# Get systolic (LOINC 8480-6)
systolic = evaluate_fhirpath(
    "Observation.component.where(code.coding.code = '8480-6').valueQuantity.value",
    bp_observation
)
print(systolic)  # [120]

# Get diastolic (LOINC 8462-4)
diastolic = evaluate_fhirpath(
    "Observation.component.where(code.coding.code = '8462-4').valueQuantity.value",
    bp_observation
)
print(diastolic)  # [80]

# Check if elevated
elevated = evaluate_fhirpath(
    "Observation.component.where(code.coding.code = '8480-6').valueQuantity.value > 140",
    bp_observation
)
print(elevated)  # [False]
```

### Bundle Processing

```python
from fhir_cql import evaluate_fhirpath

bundle = {
    "resourceType": "Bundle",
    "type": "searchset",
    "entry": [
        {"resource": {"resourceType": "Patient", "id": "1", "gender": "male"}},
        {"resource": {"resourceType": "Patient", "id": "2", "gender": "female"}},
        {"resource": {"resourceType": "Observation", "id": "3", "status": "final"}}
    ]
}

# Get all resources
resources = evaluate_fhirpath("Bundle.entry.resource", bundle)
print(len(resources))  # 3

# Get only Patient resources
patients = evaluate_fhirpath(
    "Bundle.entry.resource.where(resourceType = 'Patient')",
    bundle
)
print(len(patients))  # 2

# Using ofType() - type-safe filtering
patients = evaluate_fhirpath(
    "Bundle.entry.resource.ofType(Patient)",
    bundle
)
```

## Using Variables

Pass external variables into expressions:

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "birthDate": "1985-06-15"
}

# Using %variable syntax
variables = {"cutoffDate": "1990-01-01"}

result = evaluate_fhirpath(
    "Patient.birthDate < %cutoffDate",
    patient,
    variables=variables
)
print(result)  # [True]
```

## String Manipulation

```python
from fhir_cql import evaluate_fhirpath

patient = {
    "resourceType": "Patient",
    "name": [{"family": "Smith", "given": ["John"]}],
    "telecom": [{"value": "+1-555-123-4567"}]
}

# Uppercase
upper = evaluate_fhirpath("Patient.name.family.upper()", patient)
print(upper)  # ['SMITH']

# String contains
has_area = evaluate_fhirpath(
    "Patient.telecom.value.contains('555')",
    patient
)
print(has_area)  # [True]

# Join names
full_name = evaluate_fhirpath(
    "Patient.name.given.join(' ')",
    patient
)
print(full_name)  # ['John']

# Replace characters
cleaned = evaluate_fhirpath(
    "Patient.telecom.value.replace('-', '')",
    patient
)
print(cleaned)  # ['+15551234567']

# Substring
area_code = evaluate_fhirpath(
    "Patient.telecom.value.substring(3, 3)",
    patient
)
print(area_code)  # ['555']
```

## Math Operations

```python
from fhir_cql import evaluate_fhirpath

observation = {
    "resourceType": "Observation",
    "valueQuantity": {"value": 98.6}
}

# Basic arithmetic
result = evaluate_fhirpath("1 + 2 * 3", {})
print(result)  # [7]

# Using observation values
value = evaluate_fhirpath("Observation.valueQuantity.value", observation)
print(value)  # [98.6]

# Math functions
rounded = evaluate_fhirpath(
    "Observation.valueQuantity.value.round(1)",
    observation
)
print(rounded)  # [98.6]

# Ceiling/floor
ceil = evaluate_fhirpath("(3.2).ceiling()", {})
print(ceil)  # [4]

floor = evaluate_fhirpath("(3.8).floor()", {})
print(floor)  # [3]
```

## Type Conversion

```python
from fhir_cql import evaluate_fhirpath

# String to integer
result = evaluate_fhirpath("'42'.toInteger()", {})
print(result)  # [42]

# Integer to string
result = evaluate_fhirpath("(42).toString()", {})
print(result)  # ['42']

# String to boolean
result = evaluate_fhirpath("'true'.toBoolean()", {})
print(result)  # [True]

# Check if conversion is possible
result = evaluate_fhirpath("'hello'.convertsToInteger()", {})
print(result)  # [False]

result = evaluate_fhirpath("'42'.convertsToInteger()", {})
print(result)  # [True]
```

## Collection Operations

```python
from fhir_cql import evaluate_fhirpath

# Union
result = evaluate_fhirpath("(1 | 2 | 3) | (3 | 4 | 5)", {})
print(result)  # [1, 2, 3, 4, 5]

# Distinct
result = evaluate_fhirpath("(1 | 2 | 2 | 3 | 3).distinct()", {})
print(result)  # [1, 2, 3]

# Intersect
result = evaluate_fhirpath("(1 | 2 | 3).intersect(2 | 3 | 4)", {})
print(result)  # [2, 3]

# Exclude
result = evaluate_fhirpath("(1 | 2 | 3 | 4).exclude(2 | 4)", {})
print(result)  # [1, 3]

# Membership
result = evaluate_fhirpath("2 in (1 | 2 | 3)", {})
print(result)  # [True]

result = evaluate_fhirpath("(1 | 2 | 3) contains 2", {})
print(result)  # [True]
```

## Date/Time Operations

```python
from fhir_cql import evaluate_fhirpath

# Date literals
result = evaluate_fhirpath("@2024-06-15", {})
print(result)  # [Date(2024, 6, 15)]

# DateTime literals
result = evaluate_fhirpath("@2024-06-15T10:30:00", {})
print(result)  # [DateTime(2024, 6, 15, 10, 30, 0)]

# Date comparison
patient = {"resourceType": "Patient", "birthDate": "1985-06-15"}

result = evaluate_fhirpath(
    "Patient.birthDate < @1990-01-01",
    patient
)
print(result)  # [True]

# Current date/time
result = evaluate_fhirpath("today()", {})
print(result)  # [<current date>]

result = evaluate_fhirpath("now()", {})
print(result)  # [<current datetime>]
```

## Error Handling

```python
from fhir_cql import evaluate_fhirpath, parse_fhirpath

# Parse errors
try:
    parse_fhirpath("Patient.name.where(")  # Invalid syntax
except Exception as e:
    print(f"Parse error: {e}")

# Evaluation with missing data returns empty
patient = {"resourceType": "Patient"}

result = evaluate_fhirpath("Patient.name.family", patient)
print(result)  # [] (empty, no error)

# single() on multiple values raises error
patient = {
    "resourceType": "Patient",
    "name": [{"family": "Smith"}, {"family": "Jones"}]
}

try:
    result = evaluate_fhirpath("Patient.name.single()", patient)
except Exception as e:
    print(f"Error: {e}")  # single() requires exactly one element
```

## Best Practices

### 1. Always Handle Empty Results

```python
from fhir_cql import evaluate_fhirpath

def get_patient_gender(patient):
    result = evaluate_fhirpath("Patient.gender", patient)
    return result[0] if result else "unknown"
```

### 2. Use exists() for Conditional Logic

```python
from fhir_cql import evaluate_fhirpath

def has_email(patient):
    result = evaluate_fhirpath(
        "Patient.telecom.exists(system = 'email')",
        patient
    )
    return result[0] if result else False
```

### 3. Validate Before Complex Operations

```python
from fhir_cql import evaluate_fhirpath

def get_blood_pressure(observation):
    # First check it's a BP observation
    is_bp = evaluate_fhirpath(
        "Observation.code.coding.exists(code = '85354-9')",
        observation
    )
    if not (is_bp and is_bp[0]):
        return None

    systolic = evaluate_fhirpath(
        "Observation.component.where(code.coding.code = '8480-6').valueQuantity.value",
        observation
    )
    diastolic = evaluate_fhirpath(
        "Observation.component.where(code.coding.code = '8462-4').valueQuantity.value",
        observation
    )

    return {
        "systolic": systolic[0] if systolic else None,
        "diastolic": diastolic[0] if diastolic else None
    }
```

### 4. Cache Parsed Expressions for Performance

```python
from fhir_cql import parse_fhirpath, evaluate_fhirpath

# If evaluating the same expression many times,
# consider caching the parsed AST
# (Implementation detail - evaluate_fhirpath handles this internally)
```

## Complete Example: Patient Data Extraction

```python
from fhir_cql import evaluate_fhirpath
import json

def extract_patient_summary(patient: dict) -> dict:
    """Extract key patient information using FHIRPath."""

    def get_value(expr, default=None):
        result = evaluate_fhirpath(expr, patient)
        return result[0] if result else default

    def get_list(expr):
        return evaluate_fhirpath(expr, patient)

    return {
        "id": get_value("Patient.id"),
        "name": get_value(
            "Patient.name.where(use = 'official').select("
            "given.first() & ' ' & family).first()",
            "Unknown"
        ),
        "gender": get_value("Patient.gender", "unknown"),
        "birthDate": get_value("Patient.birthDate"),
        "active": get_value("Patient.active", False),
        "phones": get_list(
            "Patient.telecom.where(system = 'phone').value"
        ),
        "email": get_value(
            "Patient.telecom.where(system = 'email').value.first()"
        ),
        "address": get_value(
            "Patient.address.first().select("
            "line.join(', ') & ', ' & city & ', ' & state & ' ' & postalCode"
            ").first()"
        ),
        "mrn": get_value(
            "Patient.identifier.where("
            "type.coding.code = 'MR'"
            ").value.first()"
        )
    }

# Usage
patient_json = '''
{
    "resourceType": "Patient",
    "id": "12345",
    "identifier": [
        {"type": {"coding": [{"code": "MR"}]}, "value": "MRN12345"}
    ],
    "name": [{"use": "official", "family": "Smith", "given": ["John", "William"]}],
    "gender": "male",
    "birthDate": "1985-06-15",
    "active": true,
    "telecom": [
        {"system": "phone", "value": "555-1234"},
        {"system": "email", "value": "john@example.com"}
    ],
    "address": [{"line": ["123 Main St"], "city": "Boston", "state": "MA", "postalCode": "02101"}]
}
'''

patient = json.loads(patient_json)
summary = extract_patient_summary(patient)
print(json.dumps(summary, indent=2))
```

Output:
```json
{
  "id": "12345",
  "name": "John Smith",
  "gender": "male",
  "birthDate": "1985-06-15",
  "active": true,
  "phones": ["555-1234"],
  "email": "john@example.com",
  "address": "123 Main St, Boston, MA 02101",
  "mrn": "MRN12345"
}
```

## See Also

- [FHIRPath Language Guide](fhirpath-guide.md) - Complete language reference
- [CLI Reference](cli.md) - Command-line tools for testing expressions
- [Getting Started](getting-started.md) - Installation and setup
