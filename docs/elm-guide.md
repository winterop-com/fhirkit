# ELM (Expression Logical Model) Guide

This guide covers working with ELM JSON - the compiled representation of CQL (Clinical Quality Language). ELM enables interoperability between CQL implementations by providing a standardized executable format.

## What is ELM?

ELM (Expression Logical Model) is the compiled output of CQL. When CQL source code is compiled, it produces ELM JSON that can be:

- **Executed** by any ELM-compatible engine
- **Shared** between different CQL implementations
- **Stored** for later execution without recompilation

This library supports loading and executing pre-compiled ELM JSON from any CQL compiler (like the HL7 CQL-to-ELM translator).

## Quick Start

```python
from fhirkit.engine.elm import ELMEvaluator

# Create evaluator
evaluator = ELMEvaluator()

# Load ELM from JSON string
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

## Loading ELM

### From a File

```python
from fhirkit.engine.elm import ELMEvaluator

evaluator = ELMEvaluator()

# Load from file path (string or Path)
library = evaluator.load("path/to/library.elm.json")

# Or use load_file explicitly
library = evaluator.load_file("path/to/library.elm.json")
```

### From JSON String

```python
import json

elm_json = '''
{
    "library": {
        "identifier": {"id": "MyLibrary", "version": "1.0"},
        "statements": {
            "def": [
                {
                    "name": "Greeting",
                    "expression": {
                        "type": "Literal",
                        "valueType": "{urn:hl7-org:elm-types:r1}String",
                        "value": "Hello, ELM!"
                    }
                }
            ]
        }
    }
}
'''

library = evaluator.load(elm_json)
```

### From Dictionary

```python
elm_dict = {
    "library": {
        "identifier": {"id": "MyLibrary"},
        "statements": {
            "def": [{
                "name": "Answer",
                "expression": {
                    "type": "Literal",
                    "valueType": "{urn:hl7-org:elm-types:r1}Integer",
                    "value": "42"
                }
            }]
        }
    }
}

library = evaluator.load(elm_dict)
```

## Evaluating Definitions

### Single Definition

```python
# Evaluate a named definition
result = evaluator.evaluate_definition("Sum")
```

### With Patient Context

```python
patient = {
    "resourceType": "Patient",
    "id": "123",
    "birthDate": "1990-05-15",
    "gender": "female"
}

result = evaluator.evaluate_definition(
    "PatientAge",
    resource=patient
)
```

### With Parameters

```python
result = evaluator.evaluate_definition(
    "Calculation",
    parameters={"Multiplier": 10, "Offset": 5}
)
```

### All Definitions

```python
# Evaluate all public definitions
results = evaluator.evaluate_all_definitions(
    resource=patient,
    parameters={"MeasurementPeriod": interval}
)

# results is a dict: {"Definition1": value1, "Definition2": value2, ...}
for name, value in results.items():
    if name != "_errors":  # Skip error dict if present
        print(f"{name}: {value}")
```

## Library Information

### Get Definition Names

```python
# Get all public definition names
names = evaluator.get_definition_names()
print(names)  # ['Sum', 'Greeting', 'PatientAge']

# Include private definitions
all_names = evaluator.get_definition_names(include_private=True)
```

### Get Function Names

```python
functions = evaluator.get_function_names()
```

### Get Library Metadata

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

## Validation

### Validate Before Loading

```python
is_valid, errors = evaluator.validate(elm_json)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Using the Loader Directly

```python
from fhirkit.engine.elm import ELMLoader

# Validate structure
errors = ELMLoader.validate(elm_dict)
if errors:
    print("Validation errors:", errors)

# Get basic info without full parsing
info = ELMLoader.get_library_info(elm_dict)
print(f"Library: {info['id']} v{info['version']}")
print(f"Definitions: {info['definitions']}")
```

## ELM Structure Reference

### Library Structure

```json
{
    "library": {
        "identifier": {
            "id": "LibraryName",
            "version": "1.0.0"
        },
        "schemaIdentifier": {
            "id": "urn:hl7-org:elm",
            "version": "r1"
        },
        "usings": [{
            "localIdentifier": "FHIR",
            "uri": "http://hl7.org/fhir",
            "version": "4.0.1"
        }],
        "includes": [{
            "localIdentifier": "FHIRHelpers",
            "path": "FHIRHelpers",
            "version": "4.0.1"
        }],
        "parameters": [{
            "name": "MeasurementPeriod",
            "parameterType": "{urn:hl7-org:elm-types:r1}Interval"
        }],
        "codeSystems": [{
            "name": "LOINC",
            "id": "http://loinc.org"
        }],
        "valueSets": [{
            "name": "Diabetes",
            "id": "http://example.org/ValueSet/diabetes"
        }],
        "statements": {
            "def": [
                // Definition and function definitions
            ]
        }
    }
}
```

### Expression Types

#### Literals

```json
// Integer
{"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "42"}

// Decimal
{"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "3.14"}

// String
{"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "hello"}

// Boolean
{"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}

// Null
{"type": "Null"}
```

#### Arithmetic Operations

```json
// Add: 1 + 2
{
    "type": "Add",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
    ]
}

// Other arithmetic: Subtract, Multiply, Divide, TruncatedDivide, Modulo, Power, Negate
```

#### Comparison Operations

```json
// Equal: 5 = 5
{
    "type": "Equal",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}

// Other comparisons: NotEqual, Less, LessOrEqual, Greater, GreaterOrEqual, Equivalent
```

#### Boolean Operations

```json
// And: true and false
{
    "type": "And",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"}
    ]
}

// Other boolean: Or, Not, Xor, Implies
```

#### Conditional

```json
// If-then-else
{
    "type": "If",
    "condition": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
    "then": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
    "else": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
}

// Coalesce (first non-null)
{
    "type": "Coalesce",
    "operand": [
        {"type": "Null"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

#### Lists

```json
// List literal: {1, 2, 3}
{
    "type": "List",
    "element": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

#### Intervals

```json
// Interval: Interval[1, 10]
{
    "type": "Interval",
    "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
    "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
    "lowClosed": true,
    "highClosed": true
}
```

#### Expression References

```json
// Reference another definition
{
    "type": "ExpressionRef",
    "name": "OtherDefinition"
}

// Reference a parameter
{
    "type": "ParameterRef",
    "name": "MeasurementPeriod"
}
```

## Using with Data Sources

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

# Load and evaluate ELM that uses Retrieve operations
library = evaluator.load(elm_json)
result = evaluator.evaluate_definition("PatientConditions", resource=patient)
```

## Error Handling

```python
from fhirkit.engine.elm import ELMEvaluator
from fhirkit.engine.elm.exceptions import (
    ELMError,
    ELMValidationError,
    ELMExecutionError,
    ELMReferenceError
)

evaluator = ELMEvaluator()

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

## Supported Expression Types

The following ELM expression types are supported:

| Category | Types |
|----------|-------|
| Literals | Literal, Null, List, Tuple, Instance, Interval, Quantity, Code, Concept |
| Arithmetic | Add, Subtract, Multiply, Divide, TruncatedDivide, Modulo, Power, Negate, Abs, Ceiling, Floor, Truncate, Round, Ln, Log, Exp |
| Comparison | Equal, NotEqual, Equivalent, Less, LessOrEqual, Greater, GreaterOrEqual |
| Boolean | And, Or, Not, Xor, Implies, IsTrue, IsFalse, IsNull |
| Control Flow | If, Case, Coalesce |
| String | Concatenate, Combine, Split, Length, Upper, Lower, Substring, StartsWith, EndsWith, Matches, ReplaceMatches |
| Collections | First, Last, IndexOf, Exists, Count, Sum, Avg, Min, Max, Distinct, Flatten, Union, Intersect, Except, In, Contains |
| Type Operations | As, Is, ToBoolean, ToInteger, ToDecimal, ToString, ToDate, ToDateTime, ToTime, ToQuantity |
| Date/Time | Today, Now, Date, DateTime, Time, DurationBetween, DifferenceBetween, DateFrom, TimeFrom |
| Intervals | Start, End, Width, Overlaps, Meets, Before, After, Contains, In |
| References | ExpressionRef, FunctionRef, ParameterRef, Property, AliasRef |
| Clinical | Retrieve, CodeRef, ValueSetRef, InValueSet, InCodeSystem, CalculateAge |
| Query | Query, AliasedQuerySource, ReturnClause, SortClause, With, Without |

## Converting CQL to ELM

This library includes a built-in CQL-to-ELM serializer that converts CQL source code to ELM JSON without requiring external tools.

### Using the CLI

```bash
# Convert CQL to ELM JSON file
fhir elm convert library.cql -o library.elm.json

# Convert and output to stdout
fhir elm convert library.cql --quiet > library.elm.json

# Or use the CQL export command
fhir cql export library.cql -o library.elm.json
```

### Using the Python API

```python
from fhirkit.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()

# Compile a library first
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

### Using the Serializer Directly

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

### External CQL-to-ELM Translators

You can also use external CQL-to-ELM translators:

```bash
# Using the HL7 CQL translator (Java-based)
java -jar cql-to-elm.jar -f path/to/library.cql -o output/

# This produces library.json (ELM JSON) that can be loaded with this library
```

Or use the CQL testing framework available at [cql-execution](https://github.com/cqframework/cql-execution).

## CLI Commands

The `fhir elm` CLI provides commands for working with ELM files.

### Load and Validate

```bash
# Load and validate an ELM file
fhir elm load library.elm.json

# Show detailed information
fhir elm load library.elm.json --verbose
```

### Evaluate Definitions

```bash
# Evaluate a specific definition
fhir elm eval library.elm.json MyDefinition

# With patient data
fhir elm eval library.elm.json PatientAge --data patient.json

# With parameters
fhir elm eval library.elm.json Calculate --param Multiplier=10
```

### Run All Definitions

```bash
# Run all definitions
fhir elm run library.elm.json

# With data and save results
fhir elm run library.elm.json --data patient.json --output results.json
```

### Validate Multiple Files

```bash
# Validate multiple ELM files
fhir elm validate *.elm.json
```

### Display ELM

```bash
# Show ELM with syntax highlighting
fhir elm show library.elm.json
```

### Convert CQL to ELM

```bash
# Convert CQL file to ELM JSON
fhir elm convert library.cql -o library.elm.json

# Output to stdout
fhir elm convert library.cql --quiet
```

For complete CLI documentation, see the [CLI Reference](cli.md#elm-cli).

## Next Steps

- [CQL Tutorial](cql-tutorial.md) - Learn CQL syntax
- [CQL API](cql-api.md) - Direct CQL evaluation (source code)
- [CDS Hooks Guide](cds-hooks-guide.md) - Using ELM with CDS Hooks
