# python-fhir-cql

[![CI](https://github.com/mortenoh/python-fhir-cql/actions/workflows/ci.yml/badge.svg)](https://github.com/mortenoh/python-fhir-cql/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mortenoh/python-fhir-cql/branch/main/graph/badge.svg)](https://codecov.io/gh/mortenoh/python-fhir-cql)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://mortenoh.github.io/python-fhir-cql)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

FHIRPath and CQL (Clinical Quality Language) evaluators for Python using ANTLR4.

## Overview

This project provides complete implementations of:

- **FHIRPath Evaluator**: Parse and evaluate [FHIRPath](http://hl7.org/fhirpath/) expressions against FHIR resources
- **CQL Evaluator**: Parse and evaluate [CQL](https://cql.hl7.org/) (Clinical Quality Language) libraries and expressions
- **CLI Tools**: Command-line interfaces for evaluation, AST visualization, and validation
- **Python API**: Programmatic access to evaluators for integration into applications

**Current test count: 1190+ passing tests**

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- ANTLR 4.13+ (for regenerating parsers)

## Installation

```bash
# Clone the repository
git clone https://github.com/mortenoh/python-fhir-cql.git
cd python-fhir-cql

# Install dependencies
make install

# Generate ANTLR parsers (if not already generated)
make generate
```

## Quick Start

### FHIRPath CLI

```bash
# Evaluate FHIRPath against a FHIR resource
fhir fhirpath eval "Patient.name.family" -r examples/fhir/patient.json
# Output: 'Smith'

# Filter and transform
fhir fhirpath eval "Patient.name.where(use = 'official').given.first()" -r examples/fhir/patient.json

# Boolean expressions
fhir fhirpath eval "Patient.gender = 'male'" -r examples/fhir/patient.json
# Output: True
```

### CQL CLI

```bash
# Evaluate CQL expressions directly
fhir cql eval "1 + 2 * 3"
# Output: 7

fhir cql eval "Upper('hello world')"
# Output: 'HELLO WORLD'

fhir cql eval "Today() + 30 days"
# Output: @2025-01-12

fhir cql eval "Sum({1, 2, 3, 4, 5})"
# Output: 15

# Run a CQL library
fhir cql run examples/cql/01_hello_world.cql

# Evaluate specific definition
fhir cql run examples/cql/01_hello_world.cql --definition Sum

# Run with patient data
fhir cql run library.cql --data patient.json
```

### Python API

```python
from fhir_cql.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()

# Evaluate expressions
result = evaluator.evaluate_expression("1 + 2 * 3")  # 7
result = evaluator.evaluate_expression("Upper('hello')")  # 'HELLO'

# Compile and run library
lib = evaluator.compile("""
    library Example version '1.0'

    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, CQL!'

    define function Double(x Integer):
        x * 2
""")

sum_result = evaluator.evaluate_definition("Sum")  # 6
greeting = evaluator.evaluate_definition("Greeting")  # 'Hello, CQL!'

# Evaluate all definitions
all_results = evaluator.evaluate_all_definitions()
# {'Sum': 6, 'Greeting': 'Hello, CQL!'}
```

## Features

| Feature | FHIRPath | CQL |
|---------|----------|-----|
| Parsing | Yes | Yes |
| Evaluation | Yes | Yes |
| AST visualization | Yes | Yes |
| Interactive REPL | Yes | - |
| Library compilation | - | Yes |
| User-defined functions | - | Yes |
| Queries (from/where/return) | - | Yes |
| Interval operations | - | Yes |
| Temporal operations | - | Yes |
| Terminology (codes/valuesets) | - | Yes |
| FHIR data sources | - | Yes |
| Retrieve with patient context | - | Yes |
| Quality measures | - | Yes |

## CQL Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | Complete | Literals, arithmetic, comparisons, boolean logic |
| Phase 2: Collections | Complete | Lists, queries, aggregates, First/Last/Take/Skip |
| Phase 3: Temporal | Complete | Date/time, intervals, durations |
| Phase 4: Functions | Complete | String, math, type conversion, user-defined |
| Phase 5: FHIR Integration | Complete | Data sources, retrieve operations, patient context |
| Phase 6: Quality Measures | Complete | Measure evaluation, populations, stratification |
| Phase 7: Production | Complete | CLI commands, expression caching, library caching |

## CLI Commands

The unified `fhir` CLI provides access to both CQL and FHIRPath functionality:

```bash
fhir cql <command>      # CQL commands
fhir fhirpath <command> # FHIRPath commands
```

Standalone commands are also available: `cql` and `fhirpath`.

### CQL

| Command | Description |
|---------|-------------|
| `fhir cql eval <expr>` | Evaluate CQL expression |
| `fhir cql run <file>` | Run library and evaluate definitions |
| `fhir cql check <file>` | Validate and analyze library |
| `fhir cql measure <file>` | Evaluate quality measure |
| `fhir cql parse <file>` | Parse and validate file |
| `fhir cql ast <file>` | Display AST tree |
| `fhir cql tokens <file>` | Show token stream |
| `fhir cql validate <files...>` | Validate multiple files |
| `fhir cql definitions <file>` | List library definitions |

### FHIRPath

| Command | Description |
|---------|-------------|
| `fhir fhirpath eval <expr> -r <file>` | Evaluate expression against resource |
| `fhir fhirpath eval-file <file> -r <resource>` | Evaluate expressions from file |
| `fhir fhirpath parse <expr>` | Validate expression syntax |
| `fhir fhirpath ast <expr>` | Display AST tree |
| `fhir fhirpath tokens <expr>` | Show token stream |
| `fhir fhirpath repl` | Interactive REPL |

## Examples

### CQL Examples (17 files)

| File | Description |
|------|-------------|
| `01_hello_world.cql` | Basic CQL structure |
| `02_patient_queries.cql` | Patient retrieval and filtering |
| `03_observations.cql` | Clinical observations |
| `04_conditions.cql` | Condition/diagnosis queries |
| `05_medications.cql` | Medication requests |
| `06_intervals.cql` | Date/time intervals |
| `07_functions.cql` | User-defined functions |
| `08_quality_measure.cql` | Quality measure example |
| `09_string_functions.cql` | String operations |
| `10_math_functions.cql` | Math and calculations |
| `11_list_operations.cql` | List handling |
| `12_date_time_operations.cql` | Date/time operations |
| `13_interval_operations.cql` | Interval operations |
| `14_queries_advanced.cql` | Complex queries |
| `15_terminology.cql` | Codes and value sets |
| `16_clinical_calculations.cql` | BMI, eGFR, etc. |
| `17_type_conversions.cql` | Type conversions |

### FHIR Resources (14 files)

| File | Description |
|------|-------------|
| `patient.json` | Complete Patient resource |
| `patient_john_smith.json` | Detailed patient |
| `patient_diabetic.json` | Diabetic patient |
| `condition.json` | Condition resource |
| `condition_diabetes.json` | Diabetes condition |
| `observation_bp.json` | Blood pressure |
| `observation_lab.json` | Lab result |
| `observation_hba1c.json` | HbA1c result |
| `observation_glucose.json` | Blood glucose |
| `observation_blood_pressure.json` | BP panel |
| `medication_request.json` | Prescription |
| `bundle.json` | Resource bundle |
| `bundle_patient_diabetic.json` | Complete diabetic patient bundle |

## Documentation

- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli.md)
- [FHIRPath Tutorial](docs/fhirpath-tutorial.md) - Step-by-step guide
- [CQL Tutorial](docs/cql-tutorial.md) - Step-by-step guide
- [FHIRPath Guide](docs/fhirpath-guide.md)
- [FHIRPath API](docs/fhirpath-api.md)
- [CQL API](docs/cql-api.md)
- [FHIRPath & CQL Reference](docs/fhirpath-cql-tutorial.md)

## Development

```bash
make help       # Show available targets
make install    # Install dependencies
make generate   # Generate ANTLR parsers
make test       # Run tests
make lint       # Format and lint
make check      # Check without fixing
make coverage   # Run with coverage
make docs       # Build documentation
```

## Grammar Sources

The grammars are from the official HL7 CQL specification:

- **CQL Grammar**: [cqframework/clinical_quality_language](https://github.com/cqframework/clinical_quality_language/blob/master/Src/grammar/cql.g4)
- **FHIRPath Grammar**: [cqframework/clinical_quality_language](https://github.com/cqframework/clinical_quality_language/blob/master/Src/grammar/fhirpath.g4)

Version: CQL 1.5 (Mixed Normative/Trial-Use)

## References

- [CQL Specification](https://cql.hl7.org/)
- [FHIRPath Specification](http://hl7.org/fhirpath/)
- [FHIR R4](https://hl7.org/fhir/R4/)
- [ANTLR4](https://www.antlr.org/)

## License

MIT
