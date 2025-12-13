# python-fhir-cql

FHIRPath and CQL (Clinical Quality Language) evaluators for Python using ANTLR4.

## Overview

This project provides complete implementations of:

- **FHIRPath Evaluator**: Parse and evaluate [FHIRPath](http://hl7.org/fhirpath/) expressions against FHIR resources
- **CQL Evaluator**: Parse and evaluate [CQL](https://cql.hl7.org/) (Clinical Quality Language) libraries and expressions
- **CLI Tools**: Command-line interfaces for evaluation, AST visualization, and validation
- **Python API**: Programmatic access to evaluators for integration into applications

## Quick Examples

### FHIRPath

```bash
# Evaluate FHIRPath against a FHIR resource
fhir fhirpath eval "Patient.name.family" -r patient.json
# Output: 'Smith'

# Filter and transform
fhir fhirpath eval "Patient.name.where(use = 'official').given.first()" -r patient.json
```

### CQL

```bash
# Evaluate a CQL expression
fhir cql eval "1 + 2 * 3"
# Output: 7

# Run a CQL library
fhir cql run examples/cql/01_hello_world.cql
# Output: Table with all definition results

# Evaluate specific definition
fhir cql run library.cql --definition "Initial Population" --data patient.json
```

### Python API

```python
from fhir_cql.engine.cql import CQLEvaluator

evaluator = CQLEvaluator()

# Evaluate expression
result = evaluator.evaluate_expression("1 + 2 * 3")  # 7

# Compile and run library
lib = evaluator.compile("""
    library Example version '1.0'
    define Sum: 1 + 2 + 3
    define Greeting: 'Hello, CQL!'
""")

sum_result = evaluator.evaluate_definition("Sum")  # 6
greeting = evaluator.evaluate_definition("Greeting")  # 'Hello, CQL!'
```

## Features

| Feature | FHIRPath | CQL |
|---------|----------|-----|
| Parsing | Yes | Yes |
| Evaluation | Yes | Yes |
| AST visualization | Yes | Yes |
| Token stream | Yes | Yes |
| Interactive REPL | Yes | - |
| Library compilation | - | Yes |
| User-defined functions | - | Yes |
| Queries with from/where/return | - | Yes |
| Interval operations | - | Yes |
| Temporal operations | - | Yes |
| Terminology (codes/valuesets) | - | Yes |
| FHIR data sources | - | Yes |
| Quality measures | - | Yes |

## CQL Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | Complete | Literals, arithmetic, comparisons, boolean logic |
| Phase 2: Collections | Complete | Lists, queries, aggregates |
| Phase 3: Temporal | Complete | Date/time, intervals, durations |
| Phase 4: Functions | Complete | String, math, type conversion, user-defined |
| Phase 5: FHIR Integration | Complete | Data sources, retrieve, patient context |
| Phase 6: Quality Measures | Complete | Measure evaluation, populations, stratification |
| Phase 7: Production | Complete | CLI commands, expression/library caching |

**Current test count: 1190+ passing tests**

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Documentation

- [Getting Started](getting-started.md) - Installation and first steps
- [CLI Reference](cli.md) - Command-line tools

### Tutorials (Step-by-Step)
- [FHIRPath Tutorial](fhirpath-tutorial.md) - Learn FHIRPath from scratch
- [CQL Tutorial](cql-tutorial.md) - Learn CQL from scratch

### Reference
- [FHIRPath Guide](fhirpath-guide.md) - Comprehensive FHIRPath documentation
- [FHIRPath API](fhirpath-api.md) - Python API for FHIRPath
- [CQL API](cql-api.md) - Python API for CQL
- [FHIRPath & CQL Reference](fhirpath-cql-tutorial.md) - Deep dive reference with examples

## Examples

The `examples/` directory contains:

- **17 CQL example files** covering strings, math, lists, dates, intervals, queries, terminology, and clinical calculations
- **14 FHIR resource files** including patients, conditions, observations, and bundles
- **FHIRPath expression files** for testing

## Links

- [GitHub Repository](https://github.com/mortenoh/python-fhir-cql)
- [CQL Specification](https://cql.hl7.org/)
- [FHIRPath Specification](http://hl7.org/fhirpath/)
- [FHIR R4](https://hl7.org/fhir/R4/)
