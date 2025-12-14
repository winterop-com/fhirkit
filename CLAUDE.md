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

FHIRKit - FHIR toolkit with FHIRPath, CQL (Clinical Quality Language), CDS Hooks, and FHIR R4 Server for Python using ANTLR4.

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
- **NO EMOJIS**: Never use emojis in code, documentation, or commit messages

## Documentation Requirements

**IMPORTANT**: For every new feature or fix:

1. Update `docs/` - Add/update relevant documentation files:
   - `docs/index.md` - Main overview and feature list
   - `docs/cli.md` - CLI command reference
   - `docs/cql-api.md` - CQL Python API
   - `docs/fhirpath-api.md` - FHIRPath Python API
   - `docs/fhirpath-cql-tutorial.md` - Tutorial examples

2. Update `README.md` - Keep the main README in sync with features

3. Add examples in `examples/` when appropriate:
   - `examples/cql/` - CQL library examples
   - `examples/fhir/` - FHIR resource examples
   - `examples/fhirpath/` - FHIRPath expression examples
   - `examples/postman/` - Postman collection updates

## FHIR Server Requirements

When adding new FHIR server features:

1. **Update Postman Collection**: Always update `examples/postman/fhir-server.postman_collection.json`:
   - Add requests for new resource types (CRUD operations)
   - Add requests for new search parameters
   - Add requests for new operations
   - Include example request bodies with realistic data

2. **Update Documentation**: Add/update docs in `docs/fhir-server/`:
   - Resource documentation in `docs/fhir-server/resources/`
   - Search feature documentation in `docs/fhir-server/search/`

3. **Add Example Resources**: Add JSON examples in `examples/fhir/` for new resource types

4. **Update Generators**: If adding a new resource type:
   - Create generator in `src/fhir_cql/server/generator/`
   - Create fixture in `src/fhir_cql/server/generator/fixtures/`
   - Update `clinical_codes.py` to load fixture
   - Update `generator/__init__.py` exports
   - Add to `SUPPORTED_TYPES` in `routes.py`
   - Add search params in `search.py`
   - Add to compartments in `compartments.py` if applicable
