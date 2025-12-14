# CLI Reference

The unified `fhir` CLI provides access to CQL, FHIRPath, ELM, CDS Hooks, FHIR Server, and Terminology functionality:

```bash
fhir cql <command>         # CQL commands
fhir elm <command>         # ELM commands
fhir fhirpath <command>    # FHIRPath commands
fhir cds <command>         # CDS Hooks commands
fhir server <command>      # FHIR R4 server commands
fhir terminology <command> # Terminology service commands
```

---

## FHIRPath CLI

### eval

Evaluate a FHIRPath expression against a FHIR resource.

```bash
fhir fhirpath eval <expression> -r <resource.json>
fhir fhirpath eval <expression> --json '<inline-json>'
```

**Options:**

| Option | Description |
|--------|-------------|
| `-r, --resource` | Path to FHIR JSON resource file |
| `--json` | Inline JSON resource |
| `--json-output` | Output result as JSON |

**Examples:**

```bash
# Basic navigation
fhir fhirpath eval "Patient.name.family" -r patient.json

# Filtering
fhir fhirpath eval "Patient.name.where(use = 'official').given" -r patient.json

# Boolean expression
fhir fhirpath eval "Patient.gender = 'male'" -r patient.json

# JSON output
fhir fhirpath eval "Patient.name.given" -r patient.json --json-output
```

### eval-file

Evaluate multiple expressions from a file.

```bash
fhir fhirpath eval-file <expressions.fhirpath> -r <resource.json>
```

### parse

Validate FHIRPath syntax.

```bash
fhir fhirpath parse <expression>
fhir fhirpath parse <expression> -q  # quiet mode
```

### ast

Display the Abstract Syntax Tree.

```bash
fhir fhirpath ast <expression>
fhir fhirpath ast <expression> --depth 5  # limit depth
```

### tokens

Show the token stream.

```bash
fhir fhirpath tokens <expression>
fhir fhirpath tokens <expression> --limit 20
```

### parse-file

Parse multiple expressions from a file.

```bash
fhir fhirpath parse-file <file.fhirpath>
```

### repl

Start interactive REPL.

```bash
fhir fhirpath repl
fhir fhirpath repl -r patient.json  # with resource loaded
```

**REPL Commands:**

- Type expression to evaluate
- `ast <expr>` - show AST
- `tokens <expr>` - show tokens
- `quit` or `exit` - exit REPL

### show

Display a file with syntax highlighting.

```bash
fhir fhirpath show <file.fhirpath>
```

---

## CQL CLI

### eval

Evaluate a CQL expression directly.

```bash
fhir cql eval <expression>
fhir cql eval <expression> --library <file.cql>
fhir cql eval <expression> --data <resource.json>
```

**Options:**

| Option | Description |
|--------|-------------|
| `-l, --library` | CQL library file for context (definitions, functions) |
| `-d, --data` | JSON data file for context (patient, resources) |

**Examples:**

```bash
# Simple arithmetic
fhir cql eval "1 + 2 * 3"
# Output: 7

# String operations
fhir cql eval "Upper('hello')"
# Output: 'HELLO'

fhir cql eval "Combine({'a', 'b', 'c'}, ', ')"
# Output: 'a, b, c'

# Date operations
fhir cql eval "Today()"
fhir cql eval "Today() + 30 days"
fhir cql eval "years between @1990-01-01 and Today()"

# List operations
fhir cql eval "Sum({1, 2, 3, 4, 5})"
fhir cql eval "Avg({10, 20, 30})"
fhir cql eval "First({1, 2, 3})"

# Math functions
fhir cql eval "Round(3.14159, 2)"
fhir cql eval "Sqrt(16)"
fhir cql eval "Power(2, 10)"

# Evaluate definition from library
fhir cql eval "Sum" --library examples/cql/01_hello_world.cql

# With patient data
fhir cql eval "Patient.birthDate" --data patient.json
```

### run

Run a CQL library and evaluate definitions.

```bash
fhir cql run <file.cql>
fhir cql run <file.cql> --definition <name>
fhir cql run <file.cql> --data <resource.json>
fhir cql run <file.cql> --output <results.json>
```

**Options:**

| Option | Description |
|--------|-------------|
| `-e, --definition` | Specific definition to evaluate |
| `-d, --data` | JSON data file for context |
| `-o, --output` | Output file for results (JSON format) |

**Examples:**

```bash
# Run all definitions in library
fhir cql run examples/cql/01_hello_world.cql

# Evaluate specific definition
fhir cql run examples/cql/01_hello_world.cql --definition Sum

# Run with patient data
fhir cql run library.cql --data patient.json

# Run with patient bundle
fhir cql run library.cql --data examples/fhir/bundle_patient_diabetic.json

# Save results to JSON file
fhir cql run library.cql --output results.json
```

**Output Format:**

The `run` command displays a table with all definition results:

```
Library: HelloWorld v1.0.0

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Definition       ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ HelloMessage     │ 'Hello, World!'         │
│ Sum              │ 6                       │
│ IsTrue           │ true                    │
└──────────────────┴─────────────────────────┘
```

### check

Validate and analyze a CQL library.

```bash
fhir cql check <file.cql>
```

**Output includes:**

- Library structure validation
- Definition count
- Function count with signatures
- Code systems, value sets, and codes
- Any parse errors

### measure

Evaluate a quality measure against patient data.

```bash
fhir cql measure <file.cql> --data <patient.json>
fhir cql measure <file.cql> --data <bundle.json>
```

**Options:**

| Option | Description |
|--------|-------------|
| `-d, --data` | Patient data (JSON resource or bundle) |

### parse

Parse a CQL file and report syntax errors.

```bash
fhir cql parse <file.cql>
fhir cql parse <file.cql> -q  # quiet mode
```

### ast

Display the Abstract Syntax Tree.

```bash
fhir cql ast <file.cql>
fhir cql ast <file.cql> --depth 5
```

### tokens

Show the token stream.

```bash
fhir cql tokens <file.cql>
fhir cql tokens <file.cql> --limit 50
```

### validate

Validate multiple CQL files.

```bash
fhir cql validate file1.cql file2.cql
fhir cql validate examples/cql/*.cql
```

**Output:**

```
[ OK ] 01_hello_world.cql
[ OK ] 02_patient_queries.cql
[ OK ] 03_observations.cql
...

Results: 17/17 passed, 0/17 failed
```

### definitions

List library definitions.

```bash
fhir cql definitions <file.cql>
```

**Output includes:**

- Library name and version
- Using declarations (FHIR version)
- Parameters
- Value sets and code systems
- Codes and concepts
- Named expressions
- Functions

### show

Display a file with syntax highlighting.

```bash
fhir cql show <file.cql>
```

### export

Export a CQL library to ELM JSON format.

```bash
fhir cql export <file.cql>
fhir cql export <file.cql> -o <output.elm.json>
fhir cql export <file.cql> --quiet > output.elm.json
```

**Options:**

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file for ELM JSON |
| `-i, --indent` | JSON indentation level (default: 2) |
| `-q, --quiet` | Only output JSON (no status messages) |

**Examples:**

```bash
# Export to file
fhir cql export library.cql -o library.elm.json

# Export to stdout (quiet mode)
fhir cql export library.cql --quiet > library.elm.json

# View ELM with syntax highlighting
fhir cql export library.cql
```

---

## ELM CLI

### load

Load and validate an ELM JSON file.

```bash
fhir elm load <file.elm.json>
fhir elm load <file.elm.json> --verbose
```

**Options:**

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show detailed library information |

**Examples:**

```bash
# Basic load and validate
fhir elm load library.elm.json

# Show full details
fhir elm load library.elm.json --verbose
```

**Output:**

```
✓ Successfully loaded: library.elm.json

Library: MyLibrary v1.0.0

Definitions   3
Functions     1
Parameters    0
Value Sets    2
Code Systems  1
Codes         0
```

### eval

Evaluate a specific definition from an ELM library.

```bash
fhir elm eval <file.elm.json> <definition>
fhir elm eval <file.elm.json> <definition> --data <data.json>
fhir elm eval <file.elm.json> <definition> --param name=value
```

**Options:**

| Option | Description |
|--------|-------------|
| `-d, --data` | JSON data file for context |
| `-p, --param` | Parameter in name=value format (repeatable) |

**Examples:**

```bash
# Evaluate simple definition
fhir elm eval library.elm.json Sum

# With patient data
fhir elm eval library.elm.json PatientAge --data patient.json

# With parameters
fhir elm eval library.elm.json Calculate --param Multiplier=10
```

### run

Run all definitions in an ELM library.

```bash
fhir elm run <file.elm.json>
fhir elm run <file.elm.json> --data <data.json>
fhir elm run <file.elm.json> --output <results.json>
```

**Options:**

| Option | Description |
|--------|-------------|
| `-d, --data` | JSON data file for context |
| `-p, --param` | Parameter in name=value format (repeatable) |
| `-o, --output` | Output file for results (JSON format) |
| `--private` | Include private definitions |

**Examples:**

```bash
# Run all definitions
fhir elm run library.elm.json

# With patient data
fhir elm run library.elm.json --data patient.json

# Save results to file
fhir elm run library.elm.json --output results.json
```

**Output:**

```
Library: MyLibrary v1.0.0

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Definition       ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Sum              │ 6                       │
│ Greeting         │ 'Hello, ELM!'           │
│ IsActive         │ true                    │
└──────────────────┴─────────────────────────┘
```

### show

Display an ELM JSON file with syntax highlighting.

```bash
fhir elm show <file.elm.json>
```

### validate

Validate one or more ELM JSON files.

```bash
fhir elm validate <file.elm.json>
fhir elm validate *.elm.json
```

**Output:**

```
✓ library1.elm.json
✓ library2.elm.json
✗ library3.elm.json
    • Missing required field: library.identifier

Results: 2/3 passed, 1/3 failed
```

### convert

Convert a CQL file to ELM JSON.

```bash
fhir elm convert <file.cql>
fhir elm convert <file.cql> -o <output.elm.json>
fhir elm convert <file.cql> --quiet > output.elm.json
```

**Options:**

| Option | Description |
|--------|-------------|
| `-o, --output` | Output ELM JSON file |
| `-i, --indent` | JSON indentation level (default: 2) |
| `-q, --quiet` | Only output JSON (no status messages) |

**Examples:**

```bash
# Convert to file
fhir elm convert library.cql -o library.elm.json

# Convert to stdout
fhir elm convert library.cql --quiet > library.elm.json

# View with syntax highlighting
fhir elm convert library.cql
```

---

## CDS Hooks CLI

### serve

Start the CDS Hooks server.

```bash
fhir cds serve
fhir cds serve --port 8080 --config cds_services.yaml
```

**Options:**

| Option | Description |
|--------|-------------|
| `-h, --host` | Host to bind to (default: 0.0.0.0) |
| `-p, --port` | Port to bind to (default: 8080) |
| `-c, --config` | Services config file (default: cds_services.yaml) |
| `-r, --reload` | Enable auto-reload for development |
| `--cql-path` | Base path for CQL library files |

**Example:**

```bash
# Start server with default settings
fhir cds serve

# Start on custom port with specific config
fhir cds serve --port 9000 --config my_services.yaml

# Development mode with auto-reload
fhir cds serve --reload
```

### validate

Validate a CDS Hooks configuration file.

```bash
fhir cds validate <config.yaml>
```

**Example:**

```bash
fhir cds validate cds_services.yaml
```

**Output:**

```
Valid configuration with 3 service(s)

┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID              ┃ Hook           ┃ Title                          ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ greeting        │ patient-view   │ Patient Greeting               │
│ age-check       │ patient-view   │ Age-Based Recommendations      │
│ drug-alert      │ order-sign     │ Drug Interaction Alert         │
└─────────────────┴────────────────┴────────────────────────────────┘
```

### list

List configured CDS services.

```bash
fhir cds list
fhir cds list --config custom_services.yaml
```

**Options:**

| Option | Description |
|--------|-------------|
| `-c, --config` | Services config file (default: cds_services.yaml) |

### test

Test a CDS service with sample data.

```bash
fhir cds test <service-id>
fhir cds test <service-id> --config services.yaml --patient patient.json
```

**Options:**

| Option | Description |
|--------|-------------|
| `-c, --config` | Services config file (default: cds_services.yaml) |
| `-p, --patient` | Patient JSON file for prefetch data |

**Example:**

```bash
# Test with default patient
fhir cds test greeting

# Test with specific patient data
fhir cds test age-check --patient elderly_patient.json
```

**Output:**

```
Testing service: greeting

CQL Results:
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Definition     ┃ Value                      ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Greeting       │ 'Hello, World!'            │
│ HasGreeting    │ true                       │
└────────────────┴────────────────────────────┘

Cards generated: 1

┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Indicator   ┃ Summary                    ┃ Source          ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ info        │ Hello, World!              │ Greeting CDS    │
└─────────────┴────────────────────────────┴─────────────────┘
```

---

## FHIR Server CLI

### serve

Start the FHIR R4 server.

```bash
fhir server serve [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-h, --host` | Host to bind to (default: 0.0.0.0) |
| `-p, --port` | Port to bind to (default: 8080) |
| `-n, --patients` | Number of synthetic patients to generate |
| `-s, --seed` | Random seed for reproducible data |
| `--preload-cql` | Directory of CQL files to preload |
| `--preload-valuesets` | Directory of ValueSet/CodeSystem JSON files |
| `--preload-data` | FHIR Bundle JSON file to preload |
| `-r, --reload` | Enable auto-reload for development |
| `-l, --log-level` | Logging level (default: INFO) |

**Examples:**

```bash
# Start with synthetic patients
fhir server serve --patients 100

# With reproducible seed
fhir server serve --patients 50 --seed 42

# Preload terminology and CQL
fhir server serve --preload-cql ./cql --preload-valuesets ./valuesets

# Development mode
fhir server serve --patients 10 --reload
```

### generate

Generate synthetic FHIR data to a file.

```bash
fhir server generate OUTPUT [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-n, --patients` | Number of patients to generate (default: 10) |
| `-s, --seed` | Random seed for reproducible data |
| `-f, --format` | Output format: bundle, ndjson, or files |
| `--pretty/--no-pretty` | Pretty-print JSON output |

**Examples:**

```bash
# Generate as FHIR Bundle
fhir server generate ./data.json --patients 100

# Generate as NDJSON
fhir server generate ./data.ndjson --patients 100 --format ndjson

# With reproducible seed
fhir server generate ./data.json --patients 50 --seed 42
```

### load

Load FHIR resources from a file into a running server.

```bash
fhir server load INPUT_FILE [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-u, --url` | FHIR server base URL (default: http://localhost:8080) |
| `--batch/--no-batch` | Use batch transaction for loading |

**Examples:**

```bash
# Load a bundle
fhir server load ./data.json

# Load to specific server
fhir server load ./data.json --url http://fhir.example.com
```

### stats

Show statistics for a running FHIR server.

```bash
fhir server stats [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-u, --url` | FHIR server base URL (default: http://localhost:8080) |

### info

Show server capability statement information.

```bash
fhir server info [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-u, --url` | FHIR server base URL (default: http://localhost:8080) |

---

## Terminology CLI

### serve

Start the standalone terminology server.

```bash
fhir terminology serve [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-h, --host` | Host to bind to (default: 0.0.0.0) |
| `-p, --port` | Port to bind to (default: 8080) |
| `--valueset-dir` | Directory of ValueSet JSON files |

**Note:** The FHIR server includes full terminology support. Use `fhir server serve` with `--preload-valuesets` for integrated terminology operations.

---

## Quick Reference

### FHIRPath Commands

| Command | Description |
|---------|-------------|
| `fhir fhirpath eval` | Evaluate expression against resource |
| `fhir fhirpath eval-file` | Evaluate expressions from file |
| `fhir fhirpath parse` | Validate syntax |
| `fhir fhirpath ast` | Show Abstract Syntax Tree |
| `fhir fhirpath tokens` | Show token stream |
| `fhir fhirpath parse-file` | Parse expressions from file |
| `fhir fhirpath repl` | Interactive REPL mode |
| `fhir fhirpath show` | Display file with highlighting |

### CQL Commands

| Command | Description |
|---------|-------------|
| `fhir cql eval` | Evaluate expression |
| `fhir cql run` | Run library and evaluate definitions |
| `fhir cql check` | Validate and analyze library |
| `fhir cql measure` | Evaluate quality measure |
| `fhir cql parse` | Parse and validate file |
| `fhir cql ast` | Show Abstract Syntax Tree |
| `fhir cql tokens` | Show token stream |
| `fhir cql validate` | Validate multiple files |
| `fhir cql definitions` | List library definitions |
| `fhir cql show` | Display file with highlighting |
| `fhir cql export` | Export CQL to ELM JSON |

### ELM Commands

| Command | Description |
|---------|-------------|
| `fhir elm load` | Load and validate ELM JSON |
| `fhir elm eval` | Evaluate a specific definition |
| `fhir elm run` | Run all definitions in a library |
| `fhir elm show` | Display ELM with syntax highlighting |
| `fhir elm validate` | Validate ELM JSON files |
| `fhir elm convert` | Convert CQL to ELM JSON |

### CDS Hooks Commands

| Command | Description |
|---------|-------------|
| `fhir cds serve` | Start the CDS Hooks server |
| `fhir cds validate` | Validate configuration file |
| `fhir cds list` | List configured services |
| `fhir cds test` | Test a service with sample data |

### FHIR Server Commands

| Command | Description |
|---------|-------------|
| `fhir server serve` | Start the FHIR R4 server |
| `fhir server generate` | Generate synthetic FHIR data to file |
| `fhir server load` | Load FHIR resources into running server |
| `fhir server stats` | Show server resource statistics |
| `fhir server info` | Show server capability statement |

### Terminology Commands

| Command | Description |
|---------|-------------|
| `fhir terminology serve` | Start standalone terminology server |

---

## Common Patterns

### Evaluate arithmetic

```bash
fhir cql eval "1 + 2 * 3"           # 7
fhir cql eval "10 / 3"              # 3.333...
fhir cql eval "10 div 3"            # 3 (integer division)
fhir cql eval "10 mod 3"            # 1 (modulo)
```

### Work with strings

```bash
fhir cql eval "'Hello' + ' ' + 'World'"
fhir cql eval "Upper('hello')"
fhir cql eval "Substring('Hello World', 0, 5)"
fhir cql eval "Split('a,b,c', ',')"
```

### Work with dates

```bash
fhir cql eval "Today()"
fhir cql eval "Now()"
fhir cql eval "@2024-06-15 + 30 days"
fhir cql eval "years between @1990-01-01 and Today()"
```

### Work with lists

```bash
fhir cql eval "{1, 2, 3, 4, 5}"
fhir cql eval "Sum({1, 2, 3})"
fhir cql eval "First({1, 2, 3})"
fhir cql eval "from n in {1,2,3,4,5} where n > 2 return n * 2"
```

### Work with intervals

```bash
fhir cql eval "Interval[1, 10] contains 5"
fhir cql eval "5 in Interval[1, 10]"
fhir cql eval "Interval[1, 5] overlaps Interval[3, 8]"
```

### Run example libraries

```bash
# Hello World basics
fhir cql run examples/cql/01_hello_world.cql

# String functions
fhir cql run examples/cql/09_string_functions.cql

# Math functions
fhir cql run examples/cql/10_math_functions.cql

# Date/time operations
fhir cql run examples/cql/12_date_time_operations.cql

# Clinical calculations
fhir cql run examples/cql/16_clinical_calculations.cql
```
