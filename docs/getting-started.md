# Getting Started

## Installation

```bash
# Clone the repository
git clone https://github.com/mortenoh/python-fhir-cql.git
cd python-fhir-cql

# Install dependencies
make install

# Generate ANTLR parsers (if not already generated)
make generate
```

## Verify Installation

```bash
# Check FHIRPath CLI
fhirpath --help

# Check CQL CLI
cql --help
```

## Your First FHIRPath Expression

Create a simple FHIR Patient resource:

```json
{
  "resourceType": "Patient",
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male"
}
```

Save it as `patient.json`, then evaluate:

```bash
# Get the family name
fhirpath eval "Patient.name.family" -r patient.json

# Check gender
fhirpath eval "Patient.gender = 'male'" -r patient.json
```

## Your First CQL Library

Create a simple CQL file:

```cql
library HelloWorld version '1.0.0'

using FHIR version '4.0.1'

define Greeting: 'Hello, CQL!'
```

Save it as `hello.cql`, then parse:

```bash
cql parse hello.cql
cql definitions hello.cql
```

## Project Structure

```
python-fhir-cql/
├── grammars/           # ANTLR grammar files
├── generated/          # Generated Python parsers
├── examples/           # Example files
│   ├── cql/           # CQL examples
│   ├── fhir/          # FHIR JSON resources
│   └── fhirpath/      # FHIRPath expressions
├── src/fhir_cql/      # Python source
└── tests/             # Test suite
```

## Next Steps

- Explore the [CLI Reference](cli.md) for all commands
- Check out the `examples/` folder for more examples
