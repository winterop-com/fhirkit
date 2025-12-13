# CLI Reference

The unified `fhir` CLI provides access to both CQL and FHIRPath functionality:

```bash
fhir cql <command>      # CQL commands
fhir fhirpath <command> # FHIRPath commands
```

Standalone commands are also available: `cql` and `fhirpath`.

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
