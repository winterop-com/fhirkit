# CQL Python API

This document describes the Python API for evaluating CQL (Clinical Quality Language) expressions and libraries.

## Quick Start

```python
from fhirkit.engine.cql import CQLEvaluator

# Create evaluator
evaluator = CQLEvaluator()

# Evaluate a simple expression
result = evaluator.evaluate_expression("1 + 2 * 3")
print(result)  # 7

# Compile and run a library
lib = evaluator.compile("""
    library Example version '1.0'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, CQL!'
""")

# Evaluate definitions
sum_result = evaluator.evaluate_definition("Sum")  # 6
greeting = evaluator.evaluate_definition("Greeting")  # 'Hello, CQL!'
```

## CQLEvaluator

The main class for CQL evaluation.

### Constructor

```python
from fhirkit.engine.cql import CQLEvaluator

evaluator = CQLEvaluator(
    data_source=None,       # Optional DataSource for retrieve operations
    library_manager=None    # Optional LibraryManager for library dependencies
)
```

### Methods

#### compile(source: str) -> CQLLibrary

Compile CQL source code into a library.

```python
lib = evaluator.compile("""
    library MyLibrary version '1.0'
    using FHIR version '4.0.1'

    define Sum: 1 + 2 + 3
    define Product: 4 * 5
""")

print(lib.name)     # 'MyLibrary'
print(lib.version)  # '1.0'
```

#### evaluate_expression(expression, resource=None, parameters=None) -> Any

Evaluate a CQL expression directly.

```python
# Simple expression
result = evaluator.evaluate_expression("1 + 2 * 3")

# With patient resource
patient = {"resourceType": "Patient", "birthDate": "1990-05-15"}
result = evaluator.evaluate_expression(
    "years between @1990-05-15 and Today()",
    resource=patient
)

# With parameters
result = evaluator.evaluate_expression(
    "X + Y",
    parameters={"X": 10, "Y": 20}
)
```

#### evaluate_definition(name, resource=None, parameters=None, library=None) -> Any

Evaluate a named definition from a library.

```python
# Compile library first
lib = evaluator.compile("""
    library Test
    define Sum: 1 + 2 + 3
    define Double: Sum * 2
""")

# Evaluate specific definition
result = evaluator.evaluate_definition("Sum")  # 6
result = evaluator.evaluate_definition("Double")  # 12

# With patient context
patient = {"resourceType": "Patient", "birthDate": "1990-05-15"}
result = evaluator.evaluate_definition("PatientAge", resource=patient)
```

#### evaluate_all_definitions(resource=None, parameters=None, library=None) -> dict

Evaluate all definitions in a library.

```python
lib = evaluator.compile("""
    library Test
    define A: 1
    define B: 2
    define C: A + B
""")

results = evaluator.evaluate_all_definitions()
# {'A': 1, 'B': 2, 'C': 3}
```

#### load_library(name, version=None) -> CQLLibrary

Load a previously compiled library.

```python
# After compiling
evaluator.compile("library MyLib ...")

# Later load by name
lib = evaluator.load_library("MyLib")
```

#### get_definitions(library=None) -> list[str]

Get list of definition names.

```python
lib = evaluator.compile("""
    library Test
    define A: 1
    define B: 2
""")

names = evaluator.get_definitions()  # ['A', 'B']
```

#### get_parameters(library=None) -> dict

Get parameter definitions and defaults.

```python
lib = evaluator.compile("""
    library Test
    parameter X Integer default 10
    parameter Y String
""")

params = evaluator.get_parameters()
# {'X': 10, 'Y': None}
```

## CQLLibrary

Represents a compiled CQL library.

### Properties

```python
lib.name           # Library name
lib.version        # Library version
lib.using          # List of UsingDefinition
lib.includes       # List of IncludeDefinition
lib.codesystems    # Dict of CodeSystemDefinition
lib.valuesets      # Dict of ValueSetDefinition
lib.codes          # Dict of CodeDefinition
lib.concepts       # Dict of ConceptDefinition
lib.parameters     # Dict of ParameterDefinition
lib.definitions    # Dict of ExpressionDefinition
lib.functions      # Dict of FunctionDefinition
lib.contexts       # List of context names
```

### Methods

```python
# Get a specific definition
defn = lib.get_definition("Sum")

# Get a function
func = lib.get_function("MyFunc")

# Resolve a code reference
code = lib.resolve_code("DiabetesCode")
```

## Convenience Functions

### compile_library(source) -> CQLLibrary

Quick way to compile a library.

```python
from fhirkit.engine.cql import compile_library

lib = compile_library("""
    library Test
    define Sum: 1 + 2 + 3
""")
```

### evaluate(expression, resource=None) -> Any

Quick way to evaluate an expression.

```python
from fhirkit.engine.cql import evaluate

result = evaluate("1 + 2 * 3")  # 7
result = evaluate("Today()")    # Current date
```

## Working with Patient Data

### Basic Patient Context

```python
evaluator = CQLEvaluator()

lib = evaluator.compile("""
    library PatientLib version '1.0'
    using FHIR version '4.0.1'

    context Patient

    define PatientAge:
        years between Patient.birthDate and Today()

    define IsAdult:
        PatientAge >= 18

    define PatientGender:
        Patient.gender
""")

patient = {
    "resourceType": "Patient",
    "birthDate": "1990-05-15",
    "gender": "male",
    "name": [{"family": "Smith", "given": ["John"]}]
}

age = evaluator.evaluate_definition("PatientAge", resource=patient)
is_adult = evaluator.evaluate_definition("IsAdult", resource=patient)
gender = evaluator.evaluate_definition("PatientGender", resource=patient)
```

### With Parameters

```python
lib = evaluator.compile("""
    library MeasureLib

    parameter "Measurement Period" Interval<DateTime>
    parameter "Age Threshold" Integer default 18

    define IsAdultInPeriod:
        PatientAge >= "Age Threshold"
""")

from datetime import datetime

params = {
    "Measurement Period": {
        "low": datetime(2024, 1, 1),
        "high": datetime(2024, 12, 31)
    },
    "Age Threshold": 21
}

result = evaluator.evaluate_definition(
    "IsAdultInPeriod",
    resource=patient,
    parameters=params
)
```

## CQL Types

### Intervals

```python
from fhirkit.engine.cql.types import CQLInterval

# Create interval
interval = CQLInterval(low=1, high=10, low_closed=True, high_closed=True)

# Evaluate interval expressions
result = evaluator.evaluate_expression("Interval[1, 10] contains 5")  # True
result = evaluator.evaluate_expression("5 in Interval[1, 10]")  # True
```

### Tuples

```python
from fhirkit.engine.cql.types import CQLTuple

# Evaluate tuple expression
result = evaluator.evaluate_expression("""
    Tuple { name: 'John', age: 30, active: true }
""")
# CQLTuple with elements {'name': 'John', 'age': 30, 'active': True}

# Access elements
print(result.elements['name'])  # 'John'
```

### Codes and Concepts

```python
from fhirkit.engine.cql.types import CQLCode, CQLConcept

# In CQL
lib = evaluator.compile("""
    library TermLib

    codesystem "LOINC": 'http://loinc.org'
    code "Glucose": '2339-0' from "LOINC"

    define GlucoseCode: "Glucose"
""")

result = evaluator.evaluate_definition("GlucoseCode")
# CQLCode(code='2339-0', system='http://loinc.org', display=None)
```

### Quantities

```python
# Evaluate quantity expressions
result = evaluator.evaluate_expression("100 'mg'")
# Quantity(value=100, unit='mg')

result = evaluator.evaluate_expression("70 'kg' + 5 'kg'")
# Quantity(value=75, unit='kg')
```

## User-Defined Functions

```python
lib = evaluator.compile("""
    library FuncLib

    // Simple function
    define function Add(a Integer, b Integer) returns Integer:
        a + b

    // Function with null handling
    define function SafeDivide(num Decimal, denom Decimal) returns Decimal:
        if denom is null or denom = 0 then null
        else num / denom

    // Recursive function
    define function Factorial(n Integer) returns Integer:
        if n <= 1 then 1
        else n * Factorial(n - 1)

    // Using functions
    define Sum: Add(5, 3)
    define Division: SafeDivide(10.0, 2.0)
    define Fact5: Factorial(5)
""")

results = evaluator.evaluate_all_definitions()
# {'Sum': 8, 'Division': 5.0, 'Fact5': 120}
```

## Error Handling

```python
from fhirkit.engine.exceptions import CQLError

try:
    evaluator.compile("invalid cql syntax !!!")
except CQLError as e:
    print(f"Compilation error: {e}")

try:
    evaluator.evaluate_definition("NonExistent")
except CQLError as e:
    print(f"Evaluation error: {e}")
```

## Complete Example

```python
from fhirkit.engine.cql import CQLEvaluator
import json

# Load patient data
with open("patient.json") as f:
    patient = json.load(f)

# Create evaluator
evaluator = CQLEvaluator()

# Compile clinical logic
lib = evaluator.compile("""
    library DiabetesRisk version '1.0'
    using FHIR version '4.0.1'

    context Patient

    // Patient demographics
    define PatientAge:
        years between Patient.birthDate and Today()

    define IsFemale:
        Patient.gender = 'female'

    // Risk factors
    define HasDiabetesRiskFactors:
        PatientAge >= 45

    // BMI calculation helper
    define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
        if weightKg is null or heightCm is null or heightCm = 0 then null
        else Round(weightKg / Power(heightCm / 100, 2), 1)

    // Age categories
    define AgeCategory:
        case
            when PatientAge < 18 then 'Pediatric'
            when PatientAge < 65 then 'Adult'
            else 'Geriatric'
        end
""")

# Evaluate all definitions
results = evaluator.evaluate_all_definitions(resource=patient)

print("Patient Analysis:")
for name, value in results.items():
    print(f"  {name}: {value}")
```

## FHIR Data Sources

CQL evaluation can query FHIR resources using data sources. Three implementations are provided:

### InMemoryDataSource

Store resources in memory for testing and simple use cases:

```python
from fhirkit.engine.cql import CQLEvaluator, InMemoryDataSource

# Create data source and add resources
ds = InMemoryDataSource()
ds.add_resource({"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"})
ds.add_resources([
    {
        "resourceType": "Condition",
        "id": "c1",
        "subject": {"reference": "Patient/p1"},
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
    },
    {
        "resourceType": "Observation",
        "id": "o1",
        "subject": {"reference": "Patient/p1"},
        "code": {"coding": [{"system": "http://loinc.org", "code": "2339-0"}]},
    },
])

# Create evaluator with data source
evaluator = CQLEvaluator(data_source=ds)

lib = evaluator.compile("""
    library Example
    using FHIR version '4.0.1'
    context Patient

    define Conditions: [Condition]
    define Observations: [Observation]
""")

patient = {"resourceType": "Patient", "id": "p1"}
conditions = evaluator.evaluate_definition("Conditions", resource=patient)
# Returns: [{"resourceType": "Condition", ...}]
```

### BundleDataSource

Load resources from a FHIR Bundle:

```python
from fhirkit.engine.cql import CQLEvaluator, BundleDataSource

bundle = {
    "resourceType": "Bundle",
    "entry": [
        {"resource": {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"}},
        {"resource": {
            "resourceType": "Condition",
            "id": "c1",
            "subject": {"reference": "Patient/p1"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
        }},
    ],
}

ds = BundleDataSource(bundle)
evaluator = CQLEvaluator(data_source=ds)

# Compile and evaluate...
```

### PatientBundleDataSource

For patient-centric bundles, automatically filters to the patient:

```python
from fhirkit.engine.cql import CQLEvaluator, PatientBundleDataSource

# Load patient bundle (e.g., from a FHIR server)
with open("patient_bundle.json") as f:
    bundle = json.load(f)

ds = PatientBundleDataSource(bundle)
evaluator = CQLEvaluator(data_source=ds)

# The patient is automatically extracted
patient = ds.patient  # {"resourceType": "Patient", ...}

# Retrieve operations are automatically scoped to this patient
conditions = evaluator.evaluate_definition("Conditions", resource=patient)
```

### Retrieve Operations

CQL retrieve syntax queries the data source:

```cql
library Example
using FHIR version '4.0.1'

context Patient

// Simple retrieve - all resources of type
define AllConditions: [Condition]

// Retrieve with code filter
codesystem "SNOMED": 'http://snomed.info/sct'
valueset "Diabetes": 'http://example.org/vs/diabetes'

define DiabetesConditions: [Condition: code in "Diabetes"]

// Retrieve uses patient context automatically
define PatientObservations: [Observation]  // Filtered to current patient
```

### Adding ValueSets

For code filtering with valuesets:

```python
from fhirkit.engine.cql import CQLCode, InMemoryDataSource

ds = InMemoryDataSource()

# Add expanded valueset
ds.add_valueset(
    "http://example.org/vs/diabetes",
    [
        CQLCode(code="44054006", system="http://snomed.info/sct"),
        CQLCode(code="E11", system="http://hl7.org/fhir/sid/icd-10"),
    ],
)

# Now [Condition: code in "Diabetes"] will filter appropriately
```

## Advanced Examples

### Batch Patient Processing

```python
from fhirkit.engine.cql import CQLEvaluator, InMemoryDataSource
import json
from pathlib import Path

def process_patient_population(
    cql_source: str,
    patient_bundles: list[Path],
    definitions: list[str]
) -> list[dict]:
    """Process multiple patients through CQL logic."""
    evaluator = CQLEvaluator()
    evaluator.compile(cql_source)

    results = []

    for bundle_path in patient_bundles:
        with open(bundle_path) as f:
            bundle = json.load(f)

        # Create data source for this patient
        ds = PatientBundleDataSource(bundle)
        evaluator._data_source = ds

        # Evaluate requested definitions
        patient_result = {
            "patient_id": ds.patient.get("id"),
            "file": str(bundle_path),
        }

        for defn in definitions:
            try:
                value = evaluator.evaluate_definition(defn, resource=ds.patient)
                patient_result[defn] = value
            except Exception as e:
                patient_result[defn] = f"Error: {e}"

        results.append(patient_result)

    return results

# Example usage
cql = """
    library PatientAnalysis version '1.0'
    using FHIR version '4.0.1'
    context Patient

    define PatientAge: years between Patient.birthDate and Today()
    define ConditionCount: Count([Condition])
    define HasDiabetes: exists([Condition] C where C.code.coding.code = '44054006')
"""

patient_files = list(Path("patients/").glob("*.json"))
results = process_patient_population(
    cql,
    patient_files,
    ["PatientAge", "ConditionCount", "HasDiabetes"]
)

for r in results:
    print(f"Patient {r['patient_id']}: Age={r['PatientAge']}, Conditions={r['ConditionCount']}")
```

### Dynamic CQL Generation

```python
from fhirkit.engine.cql import CQLEvaluator

def create_age_filter_cql(min_age: int, max_age: int, condition_codes: list[str]) -> str:
    """Dynamically generate CQL for custom filtering."""
    code_checks = " or ".join([
        f"C.code.coding.code = '{code}'" for code in condition_codes
    ])

    return f"""
        library DynamicFilter version '1.0'
        using FHIR version '4.0.1'
        context Patient

        define PatientAge: years between Patient.birthDate and Today()

        define MeetsAgeCriteria:
            PatientAge >= {min_age} and PatientAge <= {max_age}

        define HasTargetCondition:
            exists([Condition] C where {code_checks})

        define IncludePatient:
            MeetsAgeCriteria and HasTargetCondition
    """

# Generate and evaluate
evaluator = CQLEvaluator()
cql = create_age_filter_cql(
    min_age=40,
    max_age=75,
    condition_codes=["44054006", "73211009"]  # Diabetes codes
)
evaluator.compile(cql)

patient = {"resourceType": "Patient", "id": "p1", "birthDate": "1970-01-01"}
include = evaluator.evaluate_definition("IncludePatient", resource=patient)
```

### Caching and Performance

```python
from fhirkit.engine.cql import CQLEvaluator, compile_library
from functools import lru_cache
import hashlib

class CachedCQLEvaluator:
    """CQL evaluator with compiled library caching."""

    def __init__(self):
        self._evaluator = CQLEvaluator()
        self._compiled_cache = {}

    def _hash_source(self, source: str) -> str:
        return hashlib.md5(source.encode()).hexdigest()

    def compile(self, source: str):
        """Compile CQL with caching."""
        cache_key = self._hash_source(source)

        if cache_key not in self._compiled_cache:
            lib = self._evaluator.compile(source)
            self._compiled_cache[cache_key] = lib
        else:
            # Load from cache
            self._evaluator._current_library = self._compiled_cache[cache_key]

        return self._compiled_cache[cache_key]

    def evaluate(self, definition: str, resource=None):
        return self._evaluator.evaluate_definition(definition, resource=resource)

# Usage
cached_evaluator = CachedCQLEvaluator()

# First call compiles
cached_evaluator.compile(cql_source)
result1 = cached_evaluator.evaluate("SomeDefinition", resource=patient1)

# Second call uses cache
cached_evaluator.compile(cql_source)  # Same source, uses cache
result2 = cached_evaluator.evaluate("SomeDefinition", resource=patient2)
```

### Error Handling Patterns

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.exceptions import CQLError

class SafeCQLEvaluator:
    """CQL evaluator with comprehensive error handling."""

    def __init__(self):
        self._evaluator = CQLEvaluator()
        self._compiled = False

    def compile_safe(self, source: str) -> tuple[bool, str | None]:
        """Compile with error handling."""
        try:
            self._evaluator.compile(source)
            self._compiled = True
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except CQLError as e:
            return False, f"CQL error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def evaluate_safe(
        self,
        definition: str,
        resource=None,
        default=None
    ) -> tuple[any, str | None]:
        """Evaluate with error handling."""
        if not self._compiled:
            return default, "No library compiled"

        try:
            result = self._evaluator.evaluate_definition(definition, resource=resource)
            return result, None
        except KeyError:
            return default, f"Definition not found: {definition}"
        except CQLError as e:
            return default, f"Evaluation error: {e}"
        except Exception as e:
            return default, f"Unexpected error: {e}"

# Usage
evaluator = SafeCQLEvaluator()

success, error = evaluator.compile_safe(cql_source)
if not success:
    print(f"Compilation failed: {error}")
else:
    result, error = evaluator.evaluate_safe("PatientAge", resource=patient, default=0)
    if error:
        print(f"Evaluation warning: {error}")
    print(f"Result: {result}")
```

### Working with Complex Data

```python
from fhirkit.engine.cql import CQLEvaluator, InMemoryDataSource
from datetime import datetime, timedelta
import random

def generate_test_data(num_patients: int, seed: int = 42) -> InMemoryDataSource:
    """Generate synthetic test data for CQL evaluation."""
    random.seed(seed)
    ds = InMemoryDataSource()

    condition_codes = [
        ("44054006", "Type 2 diabetes"),
        ("38341003", "Hypertension"),
        ("84114007", "Heart failure"),
    ]

    for i in range(num_patients):
        # Generate patient
        birth_year = random.randint(1940, 2000)
        patient = {
            "resourceType": "Patient",
            "id": f"patient-{i}",
            "birthDate": f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "gender": random.choice(["male", "female"]),
        }
        ds.add_resource(patient)

        # Add random conditions
        num_conditions = random.randint(0, 3)
        for j in range(num_conditions):
            code, display = random.choice(condition_codes)
            condition = {
                "resourceType": "Condition",
                "id": f"condition-{i}-{j}",
                "subject": {"reference": f"Patient/patient-{i}"},
                "clinicalStatus": {
                    "coding": [{"code": "active"}]
                },
                "code": {
                    "coding": [{"system": "http://snomed.info/sct", "code": code, "display": display}]
                },
            }
            ds.add_resource(condition)

        # Add random observations
        for j in range(random.randint(1, 5)):
            obs_date = datetime.now() - timedelta(days=random.randint(1, 365))
            observation = {
                "resourceType": "Observation",
                "id": f"obs-{i}-{j}",
                "subject": {"reference": f"Patient/patient-{i}"},
                "status": "final",
                "effectiveDateTime": obs_date.isoformat(),
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "HbA1c"}]
                },
                "valueQuantity": {"value": round(random.uniform(5.0, 12.0), 1), "unit": "%"},
            }
            ds.add_resource(observation)

    return ds

# Generate test data
ds = generate_test_data(100)

# Evaluate CQL against test population
evaluator = CQLEvaluator(data_source=ds)
evaluator.compile("""
    library TestAnalysis version '1.0'
    using FHIR version '4.0.1'
    context Patient

    define HasDiabetes: exists([Condition] C where C.code.coding.code = '44054006')
    define LatestHbA1c: Last([Observation] O where O.code.coding.code = '4548-4' sort by effective).value.value
""")

# Analyze population
patients = ds.retrieve("Patient")
diabetes_count = 0
hba1c_values = []

for patient in patients:
    has_diabetes = evaluator.evaluate_definition("HasDiabetes", resource=patient)
    hba1c = evaluator.evaluate_definition("LatestHbA1c", resource=patient)

    if has_diabetes:
        diabetes_count += 1
    if hba1c is not None:
        hba1c_values.append(hba1c)

print(f"Total patients: {len(patients)}")
print(f"Diabetes prevalence: {diabetes_count/len(patients)*100:.1f}%")
print(f"Average HbA1c: {sum(hba1c_values)/len(hba1c_values):.1f}%")
```

### Library Dependencies and Includes

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.library import InMemoryLibraryResolver

# Create library resolver for dependencies
resolver = InMemoryLibraryResolver()

# Add base library
resolver.add_library("CommonFunctions", "1.0", """
    library CommonFunctions version '1.0'

    define function IsAdult(birthDate Date) returns Boolean:
        years between birthDate and Today() >= 18

    define function FormatAge(birthDate Date) returns String:
        ToString(years between birthDate and Today()) + ' years'
""")

# Add library that depends on CommonFunctions
resolver.add_library("PatientAnalysis", "1.0", """
    library PatientAnalysis version '1.0'
    using FHIR version '4.0.1'

    include CommonFunctions version '1.0'

    context Patient

    define PatientIsAdult: CommonFunctions.IsAdult(Patient.birthDate)
    define PatientAgeFormatted: CommonFunctions.FormatAge(Patient.birthDate)
""")

# Create evaluator with resolver
evaluator = CQLEvaluator(library_resolver=resolver)

# Load and evaluate
evaluator.load_library("PatientAnalysis", "1.0")
result = evaluator.evaluate_definition("PatientIsAdult", resource=patient)
```

### Custom Type Conversions

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.types import FHIRDate, FHIRDateTime, FHIRTime
from datetime import date, datetime, time

def convert_cql_result(value):
    """Convert CQL results to Python native types."""
    if value is None:
        return None

    # Handle FHIR date/time types
    if isinstance(value, FHIRDate):
        return value.to_date()
    if isinstance(value, FHIRDateTime):
        return value.to_datetime()
    if isinstance(value, FHIRTime):
        return time(
            hour=value.hour or 0,
            minute=value.minute or 0,
            second=value.second or 0
        )

    # Handle CQL types
    if hasattr(value, 'elements'):  # CQLTuple
        return {k: convert_cql_result(v) for k, v in value.elements.items()}

    if hasattr(value, 'low') and hasattr(value, 'high'):  # CQLInterval
        return {
            "low": convert_cql_result(value.low),
            "high": convert_cql_result(value.high),
            "low_closed": value.low_closed,
            "high_closed": value.high_closed,
        }

    # Handle lists
    if isinstance(value, list):
        return [convert_cql_result(v) for v in value]

    # Return as-is for basic types
    return value

# Usage
evaluator = CQLEvaluator()
evaluator.compile("""
    library TypeDemo version '1.0'
    define DateResult: @2024-06-15
    define IntervalResult: Interval[1, 10]
    define TupleResult: Tuple { name: 'John', age: 30 }
""")

# Evaluate and convert
date_val = convert_cql_result(evaluator.evaluate_definition("DateResult"))
print(f"Date: {date_val}")  # datetime.date object

interval_val = convert_cql_result(evaluator.evaluate_definition("IntervalResult"))
print(f"Interval: {interval_val}")  # dict with low, high, etc.

tuple_val = convert_cql_result(evaluator.evaluate_definition("TupleResult"))
print(f"Tuple: {tuple_val}")  # dict with name, age
```

---

## Integration Patterns

### With FastAPI

```python
from fastapi import FastAPI
from fhirkit.engine.cql import CQLEvaluator

app = FastAPI()
evaluator = CQLEvaluator()

@app.post("/evaluate")
async def evaluate_cql(expression: str, patient: dict = None):
    result = evaluator.evaluate_expression(expression, resource=patient)
    return {"result": result}

@app.post("/library/compile")
async def compile_library(source: str):
    lib = evaluator.compile(source)
    return {"name": lib.name, "definitions": list(lib.definitions.keys())}
```

### With Pandas

```python
import pandas as pd
from fhirkit.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()
lib = evaluator.compile("""
    library Analysis
    context Patient
    define PatientAge: years between Patient.birthDate and Today()
""")

# Process multiple patients
patients = [
    {"resourceType": "Patient", "id": "1", "birthDate": "1990-01-01"},
    {"resourceType": "Patient", "id": "2", "birthDate": "1985-06-15"},
    {"resourceType": "Patient", "id": "3", "birthDate": "2000-03-22"},
]

results = []
for patient in patients:
    age = evaluator.evaluate_definition("PatientAge", resource=patient)
    results.append({"id": patient["id"], "age": age})

df = pd.DataFrame(results)
print(df)
```

## Quality Measure Evaluation

The `MeasureEvaluator` class provides support for evaluating CQL-based clinical quality measures.

### Basic Usage

```python
from fhirkit.engine.cql import MeasureEvaluator

# Create measure evaluator
evaluator = MeasureEvaluator()

# Load a measure from CQL source
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

# Evaluate for a single patient
patient = {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"}
result = evaluator.evaluate_patient(patient)

print(result.patient_id)  # 'p1'
print(result.populations)  # {'initial-population': True, 'denominator': True, 'numerator': False}
```

### Population Evaluation

Evaluate a measure across multiple patients:

```python
patients = [
    {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"},
    {"resourceType": "Patient", "id": "p2", "birthDate": "1980-01-01"},
    {"resourceType": "Patient", "id": "p3", "birthDate": "1970-01-01"},
]

# Evaluate for entire population
report = evaluator.evaluate_population(patients)

print(report.measure_id)  # 'DiabetesMeasure'
print(len(report.patient_results))  # 3

# Get population counts
for group in report.groups:
    print(f"Group: {group.id}")
    for pop_type, count in group.populations.items():
        print(f"  {pop_type}: {count.count}")
    print(f"  Measure Score: {group.measure_score}")
```

### With Data Sources

```python
from fhirkit.engine.cql import MeasureEvaluator, InMemoryDataSource

# Create data source with conditions
ds = InMemoryDataSource()
ds.add_resource({"resourceType": "Patient", "id": "p1", "birthDate": "1980-01-01"})
ds.add_resource({
    "resourceType": "Condition",
    "id": "c1",
    "subject": {"reference": "Patient/p1"},
    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
})

evaluator = MeasureEvaluator(data_source=ds)
evaluator.load_measure("""
    library DiabetesMeasure version '1.0'
    using FHIR version '4.0.1'

    context Patient

    define "Initial Population":
        exists([Patient])

    define "Denominator":
        "Initial Population"

    define "Numerator":
        exists([Condition])
""")

patient = {"resourceType": "Patient", "id": "p1", "birthDate": "1980-01-01"}
result = evaluator.evaluate_patient(patient, data_source=ds)
print(result.populations["numerator"])  # True (patient has conditions)
```

### Stratification

Measures can include stratifiers for population breakdown:

```python
evaluator.load_measure("""
    library StratifiedMeasure version '1.0'

    context Patient

    define "Initial Population":
        true

    define "Denominator":
        true

    define "Numerator":
        AgeInYears() >= 50

    define "Stratifier Age Group":
        if AgeInYears() < 50 then 'Under 50'
        else '50+'
""")

patients = [
    {"resourceType": "Patient", "id": "p1", "birthDate": "2000-01-01"},  # Under 50
    {"resourceType": "Patient", "id": "p2", "birthDate": "1960-01-01"},  # 50+
]

report = evaluator.evaluate_population(patients)

# Access stratified results
for group in report.groups:
    for strat_name, strat_results in group.stratifiers.items():
        print(f"Stratifier: {strat_name}")
        for result in strat_results:
            print(f"  {result.value}: {result.populations}")
```

### MeasureReport to FHIR

Convert measure results to a FHIR MeasureReport:

```python
report = evaluator.evaluate_population(patients)

# Convert to FHIR MeasureReport
fhir_report = report.to_fhir()
print(json.dumps(fhir_report, indent=2))

# Output:
# {
#   "resourceType": "MeasureReport",
#   "status": "complete",
#   "type": "summary",
#   "measure": "DiabetesMeasure",
#   "date": "2025-12-13T10:30:00",
#   "group": [{
#     "id": "default",
#     "population": [
#       {"code": {"coding": [{"code": "initial-population"}]}, "count": 3},
#       {"code": {"coding": [{"code": "denominator"}]}, "count": 3},
#       {"code": {"coding": [{"code": "numerator"}]}, "count": 2}
#     ],
#     "measureScore": {"value": 0.6667}
#   }]
# }
```

### Population Summary

Get a quick summary of population counts:

```python
report = evaluator.evaluate_population(patients)
summary = evaluator.get_population_summary(report)

print(summary)
# {
#   'measure': 'DiabetesMeasure',
#   'total_patients': 3,
#   'groups': [{
#     'id': 'default',
#     'populations': {
#       'initial-population': 3,
#       'denominator': 3,
#       'numerator': 2
#     },
#     'measure_score': 0.6667
#   }]
# }
```

### Measure Scoring Types

```python
from fhirkit.engine.cql import MeasureScoring

evaluator = MeasureEvaluator()
evaluator.set_scoring(MeasureScoring.PROPORTION)  # Default
# evaluator.set_scoring(MeasureScoring.RATIO)
# evaluator.set_scoring(MeasureScoring.COHORT)
# evaluator.set_scoring(MeasureScoring.CONTINUOUS_VARIABLE)
```

### Population Types

The following population types are supported:

| Type | CQL Definition Names |
|------|---------------------|
| Initial Population | `Initial Population`, `InitialPopulation` |
| Denominator | `Denominator` |
| Denominator Exclusion | `Denominator Exclusion`, `DenominatorExclusion` |
| Denominator Exception | `Denominator Exception`, `DenominatorException` |
| Numerator | `Numerator` |
| Numerator Exclusion | `Numerator Exclusion`, `NumeratorExclusion` |
| Measure Population | `Measure Population`, `MeasurePopulation` |
| Measure Observation | `Measure Observation`, `MeasureObservation` |

### Proportion Score Calculation

For proportion measures, the score is calculated as:

```
Score = (Numerator - Numerator Exclusion) /
        (Denominator - Denominator Exclusion - Denominator Exception)
```

### Complete Example

```python
from fhirkit.engine.cql import MeasureEvaluator, InMemoryDataSource
import json

# Create data source with patient data
ds = InMemoryDataSource()

# Add patients
patients = []
for i in range(10):
    age = 30 + i * 5  # Ages 30, 35, 40, ..., 75
    birth_year = 2025 - age
    patient = {
        "resourceType": "Patient",
        "id": f"p{i}",
        "birthDate": f"{birth_year}-01-01",
        "gender": "male" if i % 2 == 0 else "female",
    }
    ds.add_resource(patient)
    patients.append(patient)

    # Add diabetes condition for some patients
    if age >= 50:
        ds.add_resource({
            "resourceType": "Condition",
            "id": f"cond-{i}",
            "subject": {"reference": f"Patient/p{i}"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
        })

# Create evaluator
evaluator = MeasureEvaluator(data_source=ds)

# Load diabetes screening measure
evaluator.load_measure("""
    library DiabetesScreening version '1.0'
    using FHIR version '4.0.1'

    context Patient

    define "Initial Population":
        AgeInYears() >= 18

    define "Denominator":
        "Initial Population" and AgeInYears() >= 45

    define "Denominator Exclusion":
        AgeInYears() > 75

    define "Numerator":
        exists([Condition])

    define "Stratifier Gender":
        Patient.gender
""")

# Evaluate population
report = evaluator.evaluate_population(patients, data_source=ds)

# Print summary
summary = evaluator.get_population_summary(report)
print("Diabetes Screening Measure Results")
print("=" * 40)
print(f"Total Patients: {summary['total_patients']}")
for group in summary['groups']:
    print(f"\nGroup: {group['id']}")
    for pop, count in group['populations'].items():
        print(f"  {pop}: {count}")
    if group['measure_score'] is not None:
        print(f"  Score: {group['measure_score']:.1%}")

# Export FHIR MeasureReport
fhir_report = report.to_fhir()
print("\nFHIR MeasureReport:")
print(json.dumps(fhir_report, indent=2))
```
