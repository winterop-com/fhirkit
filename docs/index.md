# python-fhir-cql

FHIRPath and CQL (Clinical Quality Language) parsers for Python using ANTLR4.

## Overview

This project provides:

- **FHIRPath Parser**: Parse and evaluate [FHIRPath](http://hl7.org/fhirpath/) expressions against FHIR resources
- **CQL Parser**: Parse and analyze [CQL](https://cql.hl7.org/) (Clinical Quality Language) libraries
- **CLI Tools**: Command-line interfaces with AST visualization, token display, and validation
- **Python API**: Programmatic access to parsers and evaluators

## Quick Example

```bash
# Evaluate FHIRPath against a FHIR resource
fhirpath eval "Patient.name.family" -r patient.json
# Output: 'Smith'

# Parse a CQL library
cql parse quality_measure.cql
# Output: Valid CQL library
```

## Features

| Feature | FHIRPath | CQL |
|---------|----------|-----|
| Parsing | Yes | Yes |
| AST visualization | Yes | Yes |
| Token stream | Yes | Yes |
| Evaluation | Yes | - |
| Interactive REPL | Yes | - |

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Links

- [GitHub Repository](https://github.com/mortenoh/python-fhir-cql)
- [CQL Specification](https://cql.hl7.org/)
- [FHIRPath Specification](http://hl7.org/fhirpath/)
- [FHIR R4](https://hl7.org/fhir/R4/)
