# ELM Python API

This document describes the Python API for working with ELM (Expression Logical Model) - the compiled representation of CQL.

## Quick Start

```python
from fhirkit.engine.elm import ELMEvaluator

# Create evaluator
evaluator = ELMEvaluator()

# Load ELM from JSON
library = evaluator.load('''
{
    "library": {
        "identifier": {"id": "Example", "version": "1.0"},
        "statements": {
            "def": [{
                "name": "Sum",
                "expression": {
                    "type": "Add",
                    "operand": [
                        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
                    ]
                }
            }]
        }
    }
}
''')

# Evaluate definition
result = evaluator.evaluate_definition("Sum")
print(result)  # 3
```

## ELMEvaluator

The main class for loading and evaluating ELM libraries.

### Constructor

```python
from fhirkit.engine.elm import ELMEvaluator

evaluator = ELMEvaluator(
    data_source=None,       # Optional DataSource for retrieve operations
    library_manager=None    # Optional LibraryManager for library dependencies
)
```

### Methods

#### load(source) -> ELMLibrary

Load an ELM library from various sources.

```python
# From JSON string
library = evaluator.load(elm_json_string)

# From dictionary
library = evaluator.load(elm_dict)

# From file path (string)
library = evaluator.load("path/to/library.elm.json")

# From Path object
from pathlib import Path
library = evaluator.load(Path("library.elm.json"))
```

#### load_file(path) -> ELMLibrary

Load an ELM library from a file.

```python
library = evaluator.load_file("path/to/library.elm.json")
```

#### evaluate_definition(name, resource=None, parameters=None, library=None) -> Any

Evaluate a named definition within an ELM library.

```python
# Simple evaluation
result = evaluator.evaluate_definition("Sum")

# With patient context
patient = {"resourceType": "Patient", "birthDate": "1990-05-15"}
result = evaluator.evaluate_definition("PatientAge", resource=patient)

# With parameters
result = evaluator.evaluate_definition(
    "Calculation",
    parameters={"Multiplier": 10, "Offset": 5}
)
```

#### evaluate_all_definitions(resource=None, parameters=None, library=None, include_private=False) -> dict

Evaluate all definitions in a library.

```python
results = evaluator.evaluate_all_definitions(
    resource=patient,
    parameters={"MeasurementPeriod": interval}
)

# results is a dict: {"Definition1": value1, "Definition2": value2, ...}
for name, value in results.items():
    if name != "_errors":  # Skip error dict if present
        print(f"{name}: {value}")
```

#### get_definition_names(library=None, include_private=False) -> list[str]

Get names of all definitions in a library.

```python
names = evaluator.get_definition_names()
print(names)  # ['Sum', 'Greeting', 'PatientAge']

# Include private definitions
all_names = evaluator.get_definition_names(include_private=True)
```

#### get_function_names(library=None, include_private=False) -> list[str]

Get names of all functions in a library.

```python
functions = evaluator.get_function_names()
```

#### get_library_info(library=None) -> dict

Get summary information about a library.

```python
info = evaluator.get_library_info()
print(info)
# {
#     'id': 'MyLibrary',
#     'version': '1.0',
#     'schemaIdentifier': {'id': 'urn:hl7-org:elm', 'version': 'r1'},
#     'usings': [{'localIdentifier': 'FHIR', 'uri': '...', 'version': '4.0.1'}],
#     'includes': [],
#     'parameters': ['MeasurementPeriod'],
#     'codeSystems': ['LOINC', 'SNOMED'],
#     'valueSets': ['Diabetes', 'Hypertension'],
#     'definitions': ['Sum', 'PatientAge'],
#     'functions': ['CalculateBMI']
# }
```

#### get_elm_library(name, version=None) -> ELMLibrary | None

Get a loaded ELM library by name.

```python
library = evaluator.get_elm_library("MyLibrary", "1.0")
```

#### validate(source) -> tuple[bool, list[str]]

Validate ELM without fully loading.

```python
is_valid, errors = evaluator.validate(elm_json)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Properties

```python
evaluator.library_manager   # Get the LibraryManager
evaluator.current_library   # Get the currently loaded ELMLibrary
```

## ELMLoader

Static utility class for loading and validating ELM JSON.

```python
from fhirkit.engine.elm import ELMLoader
```

### Methods

#### load_file(path) -> ELMLibrary

Load an ELM library from a JSON file.

```python
library = ELMLoader.load_file("library.elm.json")
library = ELMLoader.load_file(Path("library.elm.json"))
```

#### load_json(json_str) -> ELMLibrary

Load an ELM library from a JSON string.

```python
library = ELMLoader.load_json(elm_json_string)
```

#### parse(data) -> ELMLibrary

Parse an ELM library from a dictionary.

```python
library = ELMLoader.parse(elm_dict)

# Handles both wrapped and unwrapped formats
# Wrapped: {"library": {...}}
# Unwrapped: {...} (library contents directly)
```

#### validate(data) -> list[str]

Validate ELM structure without fully parsing.

```python
errors = ELMLoader.validate(elm_dict)
if errors:
    print("Validation errors:", errors)
```

#### get_library_info(data) -> dict

Extract basic library information without full parsing.

```python
info = ELMLoader.get_library_info(elm_dict)
print(f"Library: {info['id']} v{info['version']}")
print(f"Definitions: {info['definitions']}")
print(f"Functions: {info['functions']}")
```

## ELMSerializer

Converts CQL source code to ELM JSON format.

```python
from fhirkit.engine.elm import ELMSerializer
```

### Methods

#### serialize_library(source) -> dict

Serialize CQL source to ELM dictionary.

```python
serializer = ELMSerializer()

cql_source = """
    library Example version '1.0'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, ELM!'
"""

elm_dict = serializer.serialize_library(cql_source)
```

#### serialize_library_json(source, indent=2) -> str

Serialize CQL source to ELM JSON string.

```python
elm_json = serializer.serialize_library_json(cql_source, indent=2)
print(elm_json)
```

#### serialize_to_model(source) -> ELMLibrary

Serialize CQL source to ELMLibrary Pydantic model.

```python
elm_model = serializer.serialize_to_model(cql_source)
print(elm_model.identifier.id)  # 'Example'
```

#### serialize_expression(expression) -> dict

Serialize a single CQL expression to ELM.

```python
elm_expr = serializer.serialize_expression("1 + 2 * 3")
# {'type': 'Add', 'operand': [...]}
```

### Convenience Functions

```python
from fhirkit.engine.elm import (
    serialize_to_elm,
    serialize_to_elm_json,
    serialize_to_elm_model,
)

# Convert CQL to ELM dictionary
elm_dict = serialize_to_elm(cql_source)

# Convert CQL to ELM JSON string
elm_json = serialize_to_elm_json(cql_source, indent=2)

# Convert CQL to ELMLibrary model
elm_model = serialize_to_elm_model(cql_source)
```

## ELMLibrary Model

Pydantic model representing a parsed ELM library.

```python
from fhirkit.engine.elm import ELMLibrary
```

### Properties

```python
library.identifier       # ELMIdentifier with id and version
library.schemaIdentifier # Schema identifier
library.usings           # List of using declarations
library.includes         # List of library includes
library.parameters       # List of parameters
library.codeSystems      # List of code systems
library.valueSets        # List of value sets
library.codes            # List of code definitions
library.concepts         # List of concept definitions
library.contexts         # List of context definitions
library.statements       # Statement definitions container
```

### Methods

```python
# Get a specific definition
definition = library.get_definition("Sum")

# Get a function
function = library.get_function("CalculateBMI")

# Get all definitions
definitions = library.get_definitions()

# Get all functions
functions = library.get_functions()
```

## ELMExpressionVisitor

Low-level visitor for evaluating ELM expressions directly.

```python
from fhirkit.engine.elm import ELMExpressionVisitor
from fhirkit.engine.cql.context import CQLContext

# Create context
context = CQLContext(resource=patient)

# Create visitor
visitor = ELMExpressionVisitor(context)

# Set library for definition resolution
visitor.set_library(elm_library)

# Evaluate an expression
result = visitor.evaluate({
    "type": "Add",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
    ]
})
print(result)  # 3
```

## Exception Handling

```python
from fhirkit.engine.elm import (
    ELMError,
    ELMValidationError,
    ELMExecutionError,
)
from fhirkit.engine.elm.exceptions import ELMReferenceError

try:
    library = evaluator.load(elm_json)
    result = evaluator.evaluate_definition("MyDefinition")
except ELMValidationError as e:
    print(f"Invalid ELM structure: {e}")
except ELMReferenceError as e:
    print(f"Reference not found: {e}")
except ELMExecutionError as e:
    print(f"Execution error: {e}")
except ELMError as e:
    print(f"General ELM error: {e}")
```

### Exception Hierarchy

| Exception | Description |
|-----------|-------------|
| `ELMError` | Base class for all ELM exceptions |
| `ELMValidationError` | Invalid ELM structure or parsing failure |
| `ELMExecutionError` | Runtime evaluation error |
| `ELMReferenceError` | Definition or function not found |

## Working with Data Sources

```python
from fhirkit.engine.cql import InMemoryDataSource
from fhirkit.engine.elm import ELMEvaluator

# Create data source with FHIR resources
data_source = InMemoryDataSource()
data_source.add_resources([
    {"resourceType": "Patient", "id": "1", "birthDate": "1990-05-15"},
    {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/1"}}
])

# Create evaluator with data source
evaluator = ELMEvaluator(data_source=data_source)

# Load ELM that uses Retrieve operations
library = evaluator.load(elm_json)

# Evaluate with patient context
patient = {"resourceType": "Patient", "id": "1"}
result = evaluator.evaluate_definition("PatientConditions", resource=patient)
```

## CQL-to-ELM Conversion

### Using CQLEvaluator

```python
from fhirkit.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()

# Compile CQL first
library = evaluator.compile("""
    library Example version '1.0'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, ELM!'
""")

# Convert to ELM model
elm_model = evaluator.to_elm()

# Convert to ELM JSON string
elm_json = evaluator.to_elm_json(indent=2)
print(elm_json)

# Convert to ELM dictionary
elm_dict = evaluator.to_elm_dict()
```

### Using ELMSerializer Directly

```python
from fhirkit.engine.elm import ELMSerializer

serializer = ELMSerializer()

cql_source = """
    library MyLibrary version '1.0'
    using FHIR version '4.0.1'

    define PatientAge: AgeInYears()
    define IsAdult: PatientAge >= 18
"""

# Convert to ELMLibrary model
elm_model = serializer.serialize_to_model(cql_source)

# Convert to JSON string
elm_json = serializer.serialize_library_json(cql_source, indent=2)

# Convert to dictionary
elm_dict = serializer.serialize_library(cql_source)
```

## Loading External ELM

ELM JSON from external CQL compilers (like the HL7 CQL-to-ELM translator) can be loaded directly:

```python
from fhirkit.engine.elm import ELMEvaluator

evaluator = ELMEvaluator()

# Load ELM produced by external tools
library = evaluator.load_file("library-from-external-compiler.elm.json")

# Evaluate definitions
result = evaluator.evaluate_definition("InitialPopulation", resource=patient)
```

## Complete Example

```python
from fhirkit.engine.elm import ELMEvaluator, ELMSerializer
from fhirkit.engine.cql import InMemoryDataSource
import json

# 1. Create CQL source
cql_source = """
    library DiabetesRisk version '1.0'
    using FHIR version '4.0.1'

    context Patient

    define PatientAge:
        years between Patient.birthDate and Today()

    define HasDiabetesRiskFactors:
        PatientAge >= 45

    define function CalculateBMI(weightKg Decimal, heightCm Decimal) returns Decimal:
        if weightKg is null or heightCm is null or heightCm = 0 then null
        else Round(weightKg / Power(heightCm / 100, 2), 1)
"""

# 2. Convert CQL to ELM
serializer = ELMSerializer()
elm_json = serializer.serialize_library_json(cql_source, indent=2)
print("Generated ELM:")
print(elm_json[:500] + "...")

# 3. Load and evaluate ELM
evaluator = ELMEvaluator()
library = evaluator.load(elm_json)

# 4. Get library info
info = evaluator.get_library_info()
print(f"\nLibrary: {info['id']} v{info['version']}")
print(f"Definitions: {info['definitions']}")
print(f"Functions: {info['functions']}")

# 5. Evaluate definitions
patient = {
    "resourceType": "Patient",
    "id": "p1",
    "birthDate": "1970-05-15"
}

results = evaluator.evaluate_all_definitions(resource=patient)
print("\nResults:")
for name, value in results.items():
    if name != "_errors":
        print(f"  {name}: {value}")
```

## Integration with FHIR Server

```python
from fhirkit.engine.elm import ELMEvaluator
from fhirkit.engine.cql import BundleDataSource
import json

# Load patient bundle from FHIR server response
with open("patient_bundle.json") as f:
    bundle = json.load(f)

# Create data source from bundle
data_source = BundleDataSource(bundle)

# Create evaluator
evaluator = ELMEvaluator(data_source=data_source)

# Load ELM library
library = evaluator.load_file("quality_measure.elm.json")

# Find patient in bundle
patient = next(
    e["resource"] for e in bundle.get("entry", [])
    if e.get("resource", {}).get("resourceType") == "Patient"
)

# Evaluate measure populations
results = evaluator.evaluate_all_definitions(resource=patient)
print(f"Initial Population: {results.get('Initial Population')}")
print(f"Numerator: {results.get('Numerator')}")
print(f"Denominator: {results.get('Denominator')}")
```

## Batch Processing

```python
from fhirkit.engine.elm import ELMEvaluator
from pathlib import Path
import json

def process_patients(elm_file: str, patient_files: list[Path]) -> list[dict]:
    """Process multiple patients through an ELM library."""
    evaluator = ELMEvaluator()
    evaluator.load_file(elm_file)

    results = []
    for path in patient_files:
        with open(path) as f:
            patient = json.load(f)

        patient_results = evaluator.evaluate_all_definitions(resource=patient)
        results.append({
            "patient_id": patient.get("id"),
            "file": str(path),
            **patient_results
        })

    return results

# Usage
patient_files = list(Path("patients/").glob("*.json"))
results = process_patients("measure.elm.json", patient_files)

for r in results:
    print(f"Patient {r['patient_id']}: {r.get('InitialPopulation')}")
```

---

## See Also

- [ELM Guide](elm-guide.md) - Overview and quick start
- [ELM Reference](elm-reference.md) - Expression types and examples
- [CQL API](cql-api.md) - Direct CQL evaluation
- [CLI Reference](cli.md#elm-cli) - Command-line interface
