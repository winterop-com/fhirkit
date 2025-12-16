# fhirkit

FHIRPath, CQL (Clinical Quality Language), ELM, and CDS Hooks for Python using ANTLR4.

## Overview

This project provides complete implementations of:

- **FHIRPath Evaluator**: Parse and evaluate [FHIRPath](http://hl7.org/fhirpath/) expressions against FHIR resources
- **CQL Evaluator**: Parse and evaluate [CQL](https://cql.hl7.org/) (Clinical Quality Language) libraries and expressions
- **ELM Support**: Load, execute, and export [ELM](https://cql.hl7.org/elm.html) (Expression Logical Model) - the compiled representation of CQL
- **CDS Hooks Server**: Build and deploy [CDS Hooks](https://cds-hooks.hl7.org/) services with CQL-based clinical decision support
- **CLI Tools**: Command-line interfaces for evaluation, AST visualization, validation, and CDS server management
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
from fhirkit.engine.cql import CQLEvaluator

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

| Feature | FHIRPath | CQL | ELM | CDS Hooks | Terminology |
|---------|----------|-----|-----|-----------|-------------|
| Parsing | Yes | Yes | - | - | - |
| Evaluation | Yes | Yes | Yes | - | - |
| AST visualization | Yes | Yes | - | - | - |
| Interactive REPL | Yes | Yes | - | - | - |
| Library compilation | - | Yes | - | - | - |
| Library resolution | - | Yes | - | - | - |
| User-defined functions | - | Yes | Yes | - | - |
| Queries (from/where/return) | - | Yes | Yes | - | - |
| Query aggregate clause | - | Yes | Yes | - | - |
| Interval operations | - | Yes | Yes | - | - |
| Temporal operations | - | Yes | Yes | - | - |
| Terminology (codes/valuesets) | - | Yes | Yes | - | Yes |
| FHIR data sources | - | Yes | Yes | - | - |
| Quality measures | - | Yes | Yes | - | - |
| CQL-to-ELM export | - | Yes | - | - | - |
| ELM JSON loading | - | - | Yes | - | - |
| Service discovery | - | - | - | Yes | - |
| Card generation | - | - | - | Yes | - |
| Prefetch templates | - | - | - | Yes | - |
| $validate-code | - | - | - | - | Yes |
| memberOf check | - | - | - | - | Yes |
| $subsumes | - | - | - | - | Yes |
| FastAPI server | - | - | - | - | Yes |

## Implementation Status

### CQL

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | Complete | Literals, arithmetic, comparisons, boolean logic |
| Phase 2: Collections | Complete | Lists, queries, aggregates |
| Phase 3: Temporal | Complete | Date/time, intervals, durations |
| Phase 4: Functions | Complete | String, math, type conversion, user-defined |
| Phase 5: FHIR Integration | Complete | Data sources, retrieve, patient context |
| Phase 6: Quality Measures | Complete | Measure evaluation, populations, stratification |
| Phase 7: Production | Complete | CLI commands, expression/library caching |

### ELM

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | Complete | Models, loader, visitor, evaluator |
| Phase 2: CQL-to-ELM | Complete | Serializer for exporting CQL to ELM JSON |
| Phase 3-5: Advanced | Complete | Query, clinical, and advanced expressions |
| Phase 6: CLI | Complete | ELM CLI commands |

### CDS Hooks

| Component | Status | Description |
|-----------|--------|-------------|
| API Server | Complete | FastAPI-based CDS Hooks server |
| Service Registry | Complete | YAML-based service configuration |
| Card Builder | Complete | Jinja2 template-based card generation |
| Executor | Complete | CQL evaluation engine integration |

### Terminology Service

| Component | Status | Description |
|-----------|--------|-------------|
| Models | Complete | Coding, ValueSet, CodeSystem models |
| InMemoryService | Complete | In-memory terminology validation |
| FHIRService | Complete | Proxy to external FHIR server |
| FastAPI Server | Complete | REST API for terminology operations |
| CLI Commands | Complete | serve, validate, member-of, list-valuesets |

**Current test count: 2244+ passing tests**

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Documentation

- [Getting Started](getting-started.md) - Installation and first steps
- [CLI Reference](cli.md) - Command-line tools

### Tutorials (Step-by-Step)
- [FHIRPath Tutorial](fhirpath-tutorial.md) - Learn FHIRPath from scratch
- [CQL Tutorial](cql-tutorial.md) - Learn CQL from scratch

### Reference Guides
- [FHIRPath Guide](fhirpath-guide.md) - Comprehensive FHIRPath documentation
- [FHIRPath API](fhirpath-api.md) - Python API for FHIRPath
- [CQL API](cql-api.md) - Python API for CQL
- [ELM Guide](elm-guide.md) - ELM loading, evaluation, and CQL-to-ELM export
- [ELM API](elm-api.md) - Python API for ELM (loading, evaluation, serialization)
- [ELM Reference](elm-reference.md) - Complete ELM expression types reference (168 types)
- [CDS Hooks Guide](cds-hooks-guide.md) - Building clinical decision support services
- [FHIRPath & CQL Reference](fhirpath-cql-tutorial.md) - Deep dive reference with examples

### Server & Services
- [FHIR Server Guide](fhir-server-guide.md) - Built-in FHIR server with synthetic data generation, 37 resource types
- [Supported Resources](fhir-server/resources/index.md) - All 37 supported FHIR resource types with examples
- [Terminology Operations](fhir-server/operations/terminology.md) - $expand, $lookup, $validate-code operations

### Advanced Topics
- [Measure Evaluation Guide](measure-guide.md) - Clinical quality measure evaluation
- [Data Sources Guide](datasources-guide.md) - FHIR data sources for CQL evaluation
- [Plugins Guide](plugins-guide.md) - Extending CQL with custom functions

## Examples

The `examples/` directory contains:

- **17 CQL example files** covering strings, math, lists, dates, intervals, queries, terminology, and clinical calculations
- **14 FHIR resource files** including patients, conditions, observations, and bundles
- **FHIRPath expression files** for testing

## Links

- [GitHub Repository](https://github.com/winterop-com/fhirkit)
- [CQL Specification](https://cql.hl7.org/)
- [FHIRPath Specification](http://hl7.org/fhirpath/)
- [FHIR R4](https://hl7.org/fhir/R4/)
