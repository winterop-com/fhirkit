# python-fhir-cql

[![CI](https://github.com/mortenoh/python-fhir-cql/actions/workflows/ci.yml/badge.svg)](https://github.com/mortenoh/python-fhir-cql/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mortenoh/python-fhir-cql/branch/main/graph/badge.svg)](https://codecov.io/gh/mortenoh/python-fhir-cql)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

FHIRPath and CQL (Clinical Quality Language) parsers for Python using ANTLR4.

## Overview

This project provides:

- **FHIRPath Parser**: Parse and analyze [FHIRPath](http://hl7.org/fhirpath/) expressions
- **CQL Parser**: Parse and analyze [CQL](https://cql.hl7.org/) (Clinical Quality Language) libraries
- **CLI Tools**: Command-line interfaces for both parsers with AST visualization, token display, and validation
- **Examples**: Comprehensive examples with real FHIR JSON resources

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- ANTLR 4.13+ (for regenerating parsers)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd python-fhir-cql

# Install dependencies
make install

# Generate ANTLR parsers (if not already generated)
make generate
```

## CLI Tutorial

This tutorial walks through all CLI commands with practical examples.

### FHIRPath CLI

The `fhirpath` CLI provides commands for parsing, analyzing, and evaluating FHIRPath expressions.

#### Evaluating Expressions (eval)

The `eval` command evaluates FHIRPath expressions against FHIR resources:

```bash
# Basic navigation - get patient family name
fhirpath eval "Patient.name.family" -r examples/fhir/patient.json
# Output: 'Smith'

# Get all given names
fhirpath eval "Patient.name.given" -r examples/fhir/patient.json
# Output:
#   [0] 'John'
#   [1] 'William'
#   [2] 'Johnny'

# Count telecom entries
fhirpath eval "Patient.telecom.count()" -r examples/fhir/patient.json
# Output: 3

# Boolean comparison
fhirpath eval "Patient.gender = 'male'" -r examples/fhir/patient.json
# Output: True

# Filter with where()
fhirpath eval "Patient.name.where(use = 'official').given.first()" -r examples/fhir/patient.json
# Output: 'John'

# Get blood pressure values from observation
fhirpath eval "Observation.component.valueQuantity.value" -r examples/fhir/observation_bp.json
# Output:
#   [0] 142
#   [1] 88

# String functions
fhirpath eval "Patient.name.family.upper()" -r examples/fhir/patient.json
# Output: 'SMITH'

# Existence checks
fhirpath eval "Patient.address.exists()" -r examples/fhir/patient.json
# Output: True

# Output as JSON
fhirpath eval "Patient.name.given" -r examples/fhir/patient.json --json-output
# Output: ["John", "William", "Johnny"]

# Inline JSON resource
fhirpath eval "Patient.gender" --json '{"resourceType":"Patient","gender":"female"}'
# Output: 'female'
```

#### Evaluating Files (eval-file)

Evaluate multiple FHIRPath expressions from a file:

```bash
# Evaluate all expressions in a file
fhirpath eval-file examples/fhirpath/01_basic_navigation.fhirpath -r examples/fhir/patient.json

# Quiet mode (only show errors)
fhirpath eval-file examples/fhirpath/03_existence_checks.fhirpath -r examples/fhir/patient.json -q
```

#### Parsing Expressions (parse)

Validate FHIRPath syntax without evaluation:

```bash
# Parse and validate an expression
fhirpath parse "Patient.name.given.first()"
# Output: ✓ Valid FHIRPath expression

# Parse invalid expression
fhirpath parse "Patient.name.("
# Output: Parse errors: Line 1:14 - ...

# Quiet mode
fhirpath parse "Patient.name.family" -q
```

#### AST Visualization (ast)

Display the Abstract Syntax Tree for understanding expression structure:

```bash
# Show AST tree
fhirpath ast "Patient.name.given.first()"
# Output:
# expression
# ├── expression
# │   ├── expression
# │   │   ├── expression
# │   │   │   └── term
# │   │   │       └── invocation
# │   │   │           └── identifier
# │   │   │               └── 'Patient'
# │   │   ├── '.'
# │   │   └── invocation
# │   │       └── identifier
# │   │           └── 'name'
# │   ├── '.'
# │   └── invocation
# │       └── identifier
# │           └── 'given'
# ├── '.'
# └── invocation
#     └── function
#         ├── identifier
#         │   └── 'first'
#         ├── '('
#         └── ')'

# Limit tree depth
fhirpath ast "Patient.name.where(use='official').given" --depth 3
```

#### Token Stream (tokens)

View how the lexer tokenizes an expression:

```bash
fhirpath tokens "Patient.name.family"
# Output:
# IDENTIFIER          'Patient' (col 0)
# .                   '.'       (col 7)
# IDENTIFIER          'name'    (col 8)
# .                   '.'       (col 12)
# IDENTIFIER          'family'  (col 13)
```

#### Parsing Files (parse-file)

Validate multiple expressions from a file:

```bash
# Parse all expressions in a file
fhirpath parse-file examples/fhirpath/01_basic_navigation.fhirpath
# Output:
# ✓ Line 1: Patient.name...
# ✓ Line 2: Patient.name.family...
# ...
# Results: 14/14 passed, 0/14 failed

# Quiet mode
fhirpath parse-file examples/fhirpath/01_basic_navigation.fhirpath -q
```

#### Interactive REPL (repl)

Start an interactive session for experimentation:

```bash
fhirpath repl
# FHIRPath REPL
# Enter FHIRPath expressions to parse. Type 'quit' or 'exit' to quit.
#
# fhirpath> Patient.name.family
# ✓ Valid
#
# fhirpath> ast Patient.name
# (displays AST)
#
# fhirpath> tokens 1 + 2
# (displays tokens)
#
# fhirpath> quit
```

#### Display Files (show)

View FHIRPath files with syntax highlighting:

```bash
fhirpath show examples/fhirpath/01_basic_navigation.fhirpath
```

### CQL CLI

The `cql` CLI provides commands for parsing and analyzing CQL libraries.

#### Parsing CQL Files (parse)

```bash
# Parse a CQL file
cql parse examples/cql/01_hello_world.cql
# Output: ✓ Valid CQL library

# Parse invalid CQL
cql parse invalid.cql
# Output: Parse errors: ...
```

#### AST Visualization (ast)

```bash
# Display AST tree
cql ast examples/cql/01_hello_world.cql

# Limit depth
cql ast examples/cql/08_quality_measure.cql --depth 5
```

#### Token Stream (tokens)

```bash
# Show tokens (limited)
cql tokens examples/cql/01_hello_world.cql --limit 20

# Show all tokens
cql tokens examples/cql/01_hello_world.cql
```

#### Validate Multiple Files (validate)

```bash
# Validate all CQL files
cql validate examples/cql/*.cql
# Output:
# ✓ examples/cql/01_hello_world.cql
# ✓ examples/cql/02_patient_queries.cql
# ...
# Results: 8/8 passed
```

#### List Definitions (definitions)

```bash
# Show library definitions
cql definitions examples/cql/08_quality_measure.cql
# Output:
# Library: DiabetesQualityMeasure v1.0.0
# Using: FHIR v4.0.1
#
# Parameters:
#   • MeasurementPeriod (Interval<DateTime>)
#
# Definitions:
#   • InDemographic
#   • HasDiabetes
#   • HasHbA1cTest
#   ...
```

#### Display Files (show)

```bash
cql show examples/cql/01_hello_world.cql
```

### Common Use Cases

#### Validate FHIR Constraint Expressions

```bash
# Check if patient is active
fhirpath eval "Patient.active = true" -r examples/fhir/patient.json

# Check required elements
fhirpath eval "Patient.name.exists() and Patient.birthDate.exists()" -r examples/fhir/patient.json
```

#### Extract Data from Resources

```bash
# Get all phone numbers
fhirpath eval "Patient.telecom.where(system = 'phone').value" -r examples/fhir/patient.json

# Get LOINC codes from observations
fhirpath eval "Observation.code.coding.where(system = 'http://loinc.org').code" -r examples/fhir/observation_bp.json
```

#### Analyze Bundle Resources

```bash
# Count resources in bundle
fhirpath eval "Bundle.entry.count()" -r examples/fhir/bundle.json

# Get all patient resources from bundle
fhirpath eval "Bundle.entry.resource.where(resourceType = 'Patient')" -r examples/fhir/bundle.json
```

## Quick Reference

### FHIRPath CLI Commands

| Command | Description |
|---------|-------------|
| `fhirpath eval <expr> -r <file>` | Evaluate expression against resource |
| `fhirpath eval-file <file> -r <resource>` | Evaluate expressions from file |
| `fhirpath parse <expr>` | Validate expression syntax |
| `fhirpath ast <expr>` | Display AST tree |
| `fhirpath tokens <expr>` | Show token stream |
| `fhirpath parse-file <file>` | Parse expressions from file |
| `fhirpath repl` | Interactive REPL |
| `fhirpath show <file>` | Display file with highlighting |

### CQL CLI Commands

| Command | Description |
|---------|-------------|
| `cql parse <file>` | Parse CQL file |
| `cql ast <file>` | Display AST tree |
| `cql tokens <file>` | Show token stream |
| `cql validate <files...>` | Validate multiple files |
| `cql definitions <file>` | List library definitions |
| `cql show <file>` | Display file with highlighting |

### Example Output

```
$ cql ast examples/cql/01_hello_world.cql
library
├── libraryDefinition
│   ├── 'library'
│   ├── qualifiedIdentifier
│   │   └── identifier
│   │       └── 'HelloWorld'
│   ├── 'version'
│   └── versionSpecifier
│       └── ''1.0.0''
├── definition
│   └── usingDefinition
│       ├── 'using'
│       ├── qualifiedIdentifier
│       │   └── identifier
│       │       └── 'FHIR'
...
```

```
$ fhirpath ast "Patient.name.given.first()"
expression
├── expression
│   ├── expression
│   │   ├── expression
│   │   │   └── term
│   │   │       └── invocation
│   │   │           └── identifier
│   │   │               └── 'Patient'
│   │   ├── '.'
│   │   └── invocation
│   │       └── identifier
│   │           └── 'name'
│   ├── '.'
│   └── invocation
│       └── identifier
│           └── 'given'
├── '.'
└── invocation
    └── function
        ├── identifier
        │   └── 'first'
        ├── '('
        └── ')'
```

## Project Structure

```
python-fhir-cql/
├── grammars/                    # ANTLR grammar files
│   ├── cql.g4                   # CQL grammar (HL7 official)
│   └── fhirpath.g4              # FHIRPath grammar (HL7 official)
├── generated/                   # ANTLR-generated Python parsers
│   ├── cql/
│   │   ├── cqlLexer.py
│   │   ├── cqlParser.py
│   │   ├── cqlVisitor.py
│   │   └── cqlListener.py
│   └── fhirpath/
│       ├── fhirpathLexer.py
│       ├── fhirpathParser.py
│       ├── fhirpathVisitor.py
│       └── fhirpathListener.py
├── examples/
│   ├── cql/                     # CQL example files
│   ├── fhir/                    # FHIR JSON resources
│   └── fhirpath/                # FHIRPath expressions
├── src/fhir_cql/
│   ├── __init__.py
│   ├── cli.py                   # CQL CLI (typer)
│   └── fhirpath_cli.py          # FHIRPath CLI (typer)
├── tests/
│   ├── test_cql.py
│   └── test_fhirpath.py
├── Makefile
├── pyproject.toml
└── README.md
```

## Examples

### CQL Examples

| File | Description |
|------|-------------|
| `01_hello_world.cql` | Basic CQL structure, simple expressions |
| `02_patient_queries.cql` | Patient retrieval and filtering |
| `03_observations.cql` | Working with clinical observations |
| `04_conditions.cql` | Condition/diagnosis queries |
| `05_medications.cql` | Medication request queries |
| `06_intervals.cql` | Date/time intervals and operations |
| `07_functions.cql` | User-defined functions |
| `08_quality_measure.cql` | Complete quality measure example |

### FHIR JSON Resources

| File | Description |
|------|-------------|
| `patient.json` | Complete Patient with names, addresses, telecom |
| `observation_bp.json` | Blood pressure with systolic/diastolic components |
| `observation_lab.json` | HbA1c lab result with reference ranges |
| `condition.json` | Type 2 Diabetes with SNOMED/ICD-10 codes |
| `medication_request.json` | Metformin prescription with dosage |
| `bundle.json` | Bundle containing multiple resources |

### FHIRPath Examples

Each FHIRPath example file references specific FHIR resources and shows expected results:

| File | Expressions | Topics |
|------|-------------|--------|
| `01_basic_navigation.fhirpath` | 14 | Property access, first/last, nested paths |
| `02_filtering.fhirpath` | 11 | where(), filtering by code/system |
| `03_existence_checks.fhirpath` | 16 | exists(), empty(), count(), all() |
| `04_string_functions.fhirpath` | 14 | upper/lower, contains, startsWith, join |
| `05_math_and_quantities.fhirpath` | 19 | Quantity values, arithmetic, units |
| `06_dates_and_times.fhirpath` | 14 | DateTime fields, date literals |
| `07_boolean_logic.fhirpath` | 18 | and/or/not/xor, implies, comparisons |
| `08_collections.fhirpath` | 20 | first/last/tail, distinct, bundle queries |
| `09_type_checking.fhirpath` | 16 | Type checking with `is`, conversions |
| `10_coding_operations.fhirpath` | 21 | CodeableConcept, LOINC/SNOMED/RxNorm |

## Makefile Targets

```bash
make help       # Show available targets
make install    # Install Python dependencies
make generate   # Generate ANTLR parsers
make lint       # Format and lint code
make check      # Check code without fixing
make test       # Run pytest tests
make clean      # Remove generated files and caches
```

## Grammar Sources

The grammars are from the official HL7 CQL specification:

- **CQL Grammar**: [cqframework/clinical_quality_language](https://github.com/cqframework/clinical_quality_language/blob/master/Src/grammar/cql.g4)
- **FHIRPath Grammar**: [cqframework/clinical_quality_language](https://github.com/cqframework/clinical_quality_language/blob/master/Src/grammar/fhirpath.g4)

Version: CQL 1.5 (Mixed Normative/Trial-Use)

## Development

### Regenerating Parsers

If you modify the grammar files, regenerate the parsers:

```bash
make generate
```

This requires ANTLR 4.13+ installed:

```bash
# macOS
brew install antlr

# Or download JAR from https://www.antlr.org/download.html
```

### Running Tests

```bash
make test
```

### Code Quality

```bash
# Format and lint
make lint

# Check without modifying
make check
```

## Dependencies

- [antlr4-python3-runtime](https://pypi.org/project/antlr4-python3-runtime/) - ANTLR4 Python runtime
- [typer](https://typer.tiangolo.com/) - CLI framework
- [rich](https://rich.readthedocs.io/) - Terminal formatting

## References

- [CQL Specification](https://cql.hl7.org/) - Clinical Quality Language
- [FHIRPath Specification](http://hl7.org/fhirpath/) - FHIRPath navigation language
- [FHIR R4](https://hl7.org/fhir/R4/) - FHIR specification
- [ANTLR4](https://www.antlr.org/) - Parser generator

## License

MIT
