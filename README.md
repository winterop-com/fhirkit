# python-fhir-cql

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

## CLI Usage

### CQL CLI

```bash
# Parse a CQL file
cql parse examples/cql/01_hello_world.cql

# Display AST tree
cql ast examples/cql/01_hello_world.cql

# Show token stream
cql tokens examples/cql/01_hello_world.cql --limit 20

# Validate multiple files
cql validate examples/cql/*.cql

# List definitions in a library
cql definitions examples/cql/08_quality_measure.cql

# Display with syntax highlighting
cql show examples/cql/01_hello_world.cql
```

### FHIRPath CLI

```bash
# Parse an expression
fhirpath parse "Patient.name.given.first()"

# Display AST tree
fhirpath ast "Patient.name.where(use = 'official').given.first()"

# Show token stream
fhirpath tokens "Patient.name.family"

# Parse a file with multiple expressions
fhirpath parse-file examples/fhirpath/01_basic_navigation.fhirpath

# Interactive REPL
fhirpath repl

# Display file with syntax highlighting
fhirpath show examples/fhirpath/01_basic_navigation.fhirpath
```

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
