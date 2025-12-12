# CLI Reference

## FHIRPath CLI

### eval

Evaluate a FHIRPath expression against a FHIR resource.

```bash
fhirpath eval <expression> -r <resource.json>
fhirpath eval <expression> --json '<inline-json>'
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
fhirpath eval "Patient.name.family" -r patient.json

# Filtering
fhirpath eval "Patient.name.where(use = 'official').given" -r patient.json

# Boolean expression
fhirpath eval "Patient.gender = 'male'" -r patient.json

# JSON output
fhirpath eval "Patient.name.given" -r patient.json --json-output
```

### eval-file

Evaluate multiple expressions from a file.

```bash
fhirpath eval-file <expressions.fhirpath> -r <resource.json>
```

### parse

Validate FHIRPath syntax.

```bash
fhirpath parse <expression>
fhirpath parse <expression> -q  # quiet mode
```

### ast

Display the Abstract Syntax Tree.

```bash
fhirpath ast <expression>
fhirpath ast <expression> --depth 5  # limit depth
```

### tokens

Show the token stream.

```bash
fhirpath tokens <expression>
fhirpath tokens <expression> --limit 20
```

### parse-file

Parse multiple expressions from a file.

```bash
fhirpath parse-file <file.fhirpath>
```

### repl

Start interactive REPL.

```bash
fhirpath repl
fhirpath repl -r patient.json  # with resource loaded
```

**REPL Commands:**

- Type expression to evaluate
- `ast <expr>` - show AST
- `tokens <expr>` - show tokens
- `quit` or `exit` - exit REPL

### show

Display a file with syntax highlighting.

```bash
fhirpath show <file.fhirpath>
```

---

## CQL CLI

### parse

Parse a CQL file.

```bash
cql parse <file.cql>
cql parse <file.cql> -q  # quiet mode
```

### ast

Display the Abstract Syntax Tree.

```bash
cql ast <file.cql>
cql ast <file.cql> --depth 5
```

### tokens

Show the token stream.

```bash
cql tokens <file.cql>
cql tokens <file.cql> --limit 50
```

### validate

Validate multiple CQL files.

```bash
cql validate file1.cql file2.cql
cql validate examples/cql/*.cql
```

### definitions

List library definitions.

```bash
cql definitions <file.cql>
```

**Output includes:**

- Library name and version
- Using declarations (FHIR version)
- Parameters
- Value sets
- Code systems
- Named expressions

### show

Display a file with syntax highlighting.

```bash
cql show <file.cql>
```

---

## Quick Reference

| FHIRPath Command | Description |
|------------------|-------------|
| `fhirpath eval` | Evaluate expression |
| `fhirpath eval-file` | Evaluate from file |
| `fhirpath parse` | Validate syntax |
| `fhirpath ast` | Show AST |
| `fhirpath tokens` | Show tokens |
| `fhirpath parse-file` | Parse from file |
| `fhirpath repl` | Interactive mode |
| `fhirpath show` | Display file |

| CQL Command | Description |
|-------------|-------------|
| `cql parse` | Parse file |
| `cql ast` | Show AST |
| `cql tokens` | Show tokens |
| `cql validate` | Validate files |
| `cql definitions` | List definitions |
| `cql show` | Display file |
