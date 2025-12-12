# Claude Code Project Guidelines

## Commit Rules

- **Use conventional commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- **NO attribution**: Do not add "Generated with Claude Code", "Co-Authored-By", or any AI attribution
- **Keep messages concise**: Subject line under 72 chars, bullet points in body

Example:
```
feat(fhirpath): add replaceMatches function

- Add replaceMatches() for regex replacement
- Fix replace() to use simple string replacement
```

## Project Overview

FHIRPath and CQL (Clinical Quality Language) parsers for Python using ANTLR4.

## Build Commands

```bash
make install    # Install dependencies with uv
make generate   # Generate ANTLR parsers from grammars
make test       # Run pytest tests
make lint       # Format and lint with ruff, mypy, pyright
make check      # Check without fixing
make clean      # Remove generated files
```

## Key Files

- `grammars/*.g4` - ANTLR grammar files (HL7 official)
- `generated/` - Auto-generated parser code (do not edit manually)
- `src/fhir_cql/cql_cli.py` - CQL CLI using typer
- `src/fhir_cql/fhirpath_cli.py` - FHIRPath CLI using typer
- `examples/fhir/` - Sample FHIR JSON resources
- `examples/cql/` - CQL example files
- `examples/fhirpath/` - FHIRPath expression examples

## CLI Commands

```bash
# CQL
cql parse <file>
cql ast <file>
cql tokens <file>
cql validate <files...>
cql definitions <file>

# FHIRPath
fhirpath parse <expr>
fhirpath ast <expr>
fhirpath tokens <expr>
fhirpath parse-file <file>
fhirpath eval <expr> [-r resource.json]
fhirpath repl
```

## Conventions

- Python 3.13+
- Use `uv` for dependency management
- Generated code excluded from linting
- Type hints throughout source code
