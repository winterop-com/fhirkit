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
- **ELM Support**: Load, execute, and export [ELM](https://cql.hl7.org/elm.html) (Expression Logical Model) - the compiled representation of CQL
- **FHIR R4 Server**: Full FHIR REST API with synthetic data generation, terminology operations, and CQL integration
- **CDS Hooks Server**: Build and deploy [CDS Hooks](https://cds-hooks.hl7.org/) services with CQL-based clinical decision support
- **CLI Tools**: Command-line interfaces for evaluation, AST visualization, validation, and server management
- **Python API**: Programmatic access to evaluators for integration into applications

**Current test count: 2244+ passing tests**

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

| Feature | FHIRPath | CQL | ELM | FHIR Server | CDS Hooks | Terminology |
|---------|----------|-----|-----|-------------|-----------|-------------|
| Parsing | Yes | Yes | - | - | - | - |
| Evaluation | Yes | Yes | Yes | - | - | - |
| AST visualization | Yes | Yes | - | - | - | - |
| Interactive REPL | Yes | Yes | - | - | - | - |
| Library compilation | - | Yes | - | - | - | - |
| User-defined functions | - | Yes | Yes | - | - | - |
| Queries (from/where/return) | - | Yes | Yes | - | - | - |
| Interval operations | - | Yes | Yes | - | - | - |
| Temporal operations | - | Yes | Yes | - | - | - |
| Terminology (codes/valuesets) | - | Yes | Yes | Yes | - | Yes |
| FHIR data sources | - | Yes | Yes | Yes | - | - |
| Quality measures | - | Yes | Yes | Yes | - | - |
| CQL-to-ELM export | - | Yes | - | - | - | - |
| FHIR REST API (CRUD+PATCH) | - | - | - | Yes | - | - |
| Search parameters | - | - | - | Yes | - | - |
| Batch/transaction | - | - | - | Yes | - | - |
| Conditional operations | - | - | - | Yes | - | - |
| Synthetic data generation | - | - | - | Yes | - | - |
| Group resource support | - | - | - | Yes | - | - |
| $validate | - | - | - | Yes | - | - |
| $diff | - | - | - | Yes | - | - |
| $export (Bulk Data) | - | - | - | Yes | - | - |
| $everything | - | - | - | Yes | - | - |
| $evaluate-measure | - | - | - | Yes | - | - |
| $expand, $lookup | - | - | - | Yes | - | Yes |
| $validate-code | - | - | - | Yes | - | Yes |
| $subsumes | - | - | - | Yes | - | Yes |
| YAML-based service config | - | - | - | - | Yes | - |
| Service discovery | - | - | - | - | Yes | - |
| Card generation | - | - | - | - | Yes | - |
| Prefetch templates | - | - | - | - | Yes | - |

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

The unified `fhir` CLI provides access to CQL, ELM, FHIRPath, FHIR Server, CDS Hooks, and Terminology functionality:

```bash
fhir cql <command>         # CQL commands
fhir elm <command>         # ELM commands
fhir fhirpath <command>    # FHIRPath commands
fhir server <command>      # FHIR R4 server commands
fhir cds <command>         # CDS Hooks commands
fhir terminology <command> # Terminology Service commands
```

### CQL

| Command | Description |
|---------|-------------|
| `fhir cql eval <expr>` | Evaluate CQL expression |
| `fhir cql run <file>` | Run library and evaluate definitions |
| `fhir cql repl` | Interactive REPL |
| `fhir cql check <file>` | Validate and analyze library |
| `fhir cql measure <file>` | Evaluate quality measure |
| `fhir cql export <file>` | Export CQL to ELM JSON |
| `fhir cql parse <file>` | Parse and validate file |
| `fhir cql ast <file>` | Display AST tree |
| `fhir cql validate <files...>` | Validate multiple files |

### ELM

| Command | Description |
|---------|-------------|
| `fhir elm load <file>` | Load and validate ELM JSON |
| `fhir elm eval <file> <def>` | Evaluate a specific definition |
| `fhir elm run <file>` | Run all definitions |
| `fhir elm convert <file>` | Convert CQL to ELM JSON |
| `fhir elm validate <files...>` | Validate ELM JSON files |
| `fhir elm show <file>` | Display ELM with highlighting |

### FHIRPath

| Command | Description |
|---------|-------------|
| `fhir fhirpath eval <expr> -r <file>` | Evaluate expression against resource |
| `fhir fhirpath eval-file <file> -r <resource>` | Evaluate expressions from file |
| `fhir fhirpath parse <expr>` | Validate expression syntax |
| `fhir fhirpath ast <expr>` | Display AST tree |
| `fhir fhirpath tokens <expr>` | Show token stream |
| `fhir fhirpath repl` | Interactive REPL |

### FHIR Server

| Command | Description |
|---------|-------------|
| `fhir serve` | Start the FHIR R4 server |
| `fhir serve --patients 100` | Start with synthetic patient data |
| `fhir server generate Patient -n 10` | Generate specific resource types |
| `fhir server populate` | Populate server with all 53 linked resource types |
| `fhir server load <file>` | Load resources into running server |
| `fhir server stats` | Show server resource statistics |
| `fhir server info` | Show server capability statement |

### CDS Hooks

| Command | Description |
|---------|-------------|
| `fhir cds serve` | Start the CDS Hooks server |
| `fhir cds validate <config>` | Validate service configuration |
| `fhir cds list` | List configured services |
| `fhir cds test <service>` | Test a service with sample data |

### Terminology Service

| Command | Description |
|---------|-------------|
| `fhir terminology serve` | Start the terminology server |
| `fhir terminology validate <code>` | Validate a code against a value set |
| `fhir terminology member-of <code>` | Check value set membership |
| `fhir terminology list-valuesets <dir>` | List value sets in directory |

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

### FHIR Resources (53 files)

**53 supported resource types** with example JSON files in `examples/fhir/`:

| Category | Example Resources |
|----------|-------------------|
| Administrative | Patient, Practitioner, PractitionerRole, Organization, Location, RelatedPerson |
| Clinical | Encounter, Condition, Observation, Procedure, DiagnosticReport, AllergyIntolerance, Immunization, ClinicalImpression, FamilyMemberHistory |
| Medications | Medication, MedicationRequest, MedicationAdministration, MedicationStatement, MedicationDispense |
| Care Management | CarePlan, CareTeam, Goal, Task |
| Scheduling | Appointment, Schedule, Slot, HealthcareService |
| Financial | Coverage, Claim, ExplanationOfBenefit |
| Devices | Device |
| Documents | ServiceRequest, DocumentReference, Media |
| Forms & Consent | Questionnaire, QuestionnaireResponse, Consent |
| Quality Measures | Measure, MeasureReport, Library |
| Terminology | ValueSet, CodeSystem |
| Groups | Group |
| Communication & Alerts | Communication, Flag |
| Diagnostics | Specimen |
| Orders | NutritionOrder |
| Clinical Decision Support | RiskAssessment, DetectedIssue |
| Safety | AdverseEvent |
| Infrastructure | Bundle, Provenance, AuditEvent |

See [Supported Resources](docs/fhir-server/resources/index.md) for complete documentation.

## Documentation

- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli.md)

### Tutorials
- [FHIRPath Tutorial](docs/fhirpath-tutorial.md) - Step-by-step guide
- [CQL Tutorial](docs/cql-tutorial.md) - Step-by-step guide

### Reference Guides
- [FHIRPath Guide](docs/fhirpath-guide.md)
- [FHIRPath API](docs/fhirpath-api.md)
- [CQL API](docs/cql-api.md)
- [ELM Guide](docs/elm-guide.md) - ELM loading, evaluation, and CQL-to-ELM export
- [FHIR Server Guide](docs/fhir-server-guide.md) - REST API, synthetic data, terminology operations
- [Supported Resources](docs/fhir-server/resources/index.md) - All 53 supported FHIR resource types
- [CDS Hooks Guide](docs/cds-hooks-guide.md) - Building clinical decision support services
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
