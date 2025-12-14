# Getting Started

## Installation

```bash
# Clone the repository
git clone https://github.com/winterop-com/fhirkit.git
cd fhirkit

# Install dependencies
make install

# Generate ANTLR parsers (if not already generated)
make generate
```

## Verify Installation

```bash
# Check unified CLI
fhir --help

# Check subcommands
fhir cql --help
fhir fhirpath --help

# Run tests
make test
```

## Your First FHIRPath Expression

Create a simple FHIR Patient resource:

```json
{
  "resourceType": "Patient",
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1990-05-15"
}
```

Save it as `patient.json`, then evaluate:

```bash
# Get the family name
fhir fhirpath eval "Patient.name.family" -r patient.json
# Output: 'Smith'

# Get given names
fhir fhirpath eval "Patient.name.given" -r patient.json
# Output: ['John']

# Check gender
fhir fhirpath eval "Patient.gender = 'male'" -r patient.json
# Output: true

# Calculate something with dates
fhir fhirpath eval "Patient.birthDate" -r patient.json
```

## Your First CQL Expression

CQL can be evaluated directly without a library:

```bash
# Simple arithmetic
fhir cql eval "1 + 2 * 3"
# Output: 7

# String operations
fhir cql eval "Upper('hello world')"
# Output: 'HELLO WORLD'

# Date operations
fhir cql eval "Today()"
# Output: @2024-12-13

# List operations
fhir cql eval "Sum({1, 2, 3, 4, 5})"
# Output: 15
```

## Your First CQL Library

Create a simple CQL file:

```cql
library HelloWorld version '1.0.0'

using FHIR version '4.0.1'

// Simple values
define Greeting: 'Hello, CQL!'
define Sum: 1 + 2 + 3
define IsTrue: true and not false

// Date operations
define CurrentDate: Today()
define NextWeek: Today() + 7 days

// List operations
define Numbers: {1, 2, 3, 4, 5}
define Total: Sum(Numbers)
define Average: Avg(Numbers)
```

Save it as `hello.cql`, then run:

```bash
# Parse and validate
fhir cql parse hello.cql

# List definitions
fhir cql definitions hello.cql

# Run and evaluate all definitions
fhir cql run hello.cql

# Evaluate specific definition
fhir cql run hello.cql --definition Sum
```

## Using CQL with Patient Data

Create a CQL library that uses patient data:

```cql
library PatientInfo version '1.0'

using FHIR version '4.0.1'

context Patient

define PatientAge:
    years between Patient.birthDate and Today()

define IsAdult:
    PatientAge >= 18

define PatientName:
    Patient.name.first().family
```

Run with patient data:

```bash
fhir cql run patient_info.cql --data patient.json
```

## Your First FHIR Server

Start a FHIR R4 server with synthetic patient data:

```bash
# Start with 10 synthetic patients
fhir serve --patients 10

# Server is now running at http://localhost:8080
# - API Docs: http://localhost:8080/docs
# - Metadata: http://localhost:8080/metadata
```

### Query Your Server

In another terminal, query the server:

```bash
# Get all patients
curl http://localhost:8080/baseR4/Patient

# Get a specific patient
curl http://localhost:8080/baseR4/Patient | jq '.entry[0].resource'

# Search by name
curl "http://localhost:8080/baseR4/Patient?name=Smith"

# Get patient conditions
curl "http://localhost:8080/baseR4/Condition?patient=Patient/patient-001"

# Get observations
curl "http://localhost:8080/baseR4/Observation?_count=5"
```

### Generate Synthetic Data

Generate FHIR resources without starting a server:

```bash
# Generate 5 patients to stdout
fhir server generate Patient -n 5

# Generate and pipe to jq
fhir server generate Patient -n 3 | jq '.entry[].resource.name'

# Generate to file
fhir server generate Patient ./patients.json -n 10

# Generate observations linked to a patient
fhir server generate Observation -n 5 --patient-ref Patient/123

# List all 34 available resource types
fhir server generate --list
```

### Populate Server with Linked Data

Create a complete dataset with all 37 resource types properly linked together:

```bash
# Populate with linked resources (3 patients by default)
fhir server populate

# Populate with more patients
fhir server populate --patients 10

# Dry run - generate without loading
fhir server populate --dry-run --output ./population.json
```

This creates:
- Organizations, Practitioners, Locations
- Patients with clinical data (Encounters, Conditions, Observations)
- Care plans, Care teams, Goals
- Coverage, Claims, ExplanationOfBenefit
- Measures with MeasureReports
- And more - all properly linked!

### Server Statistics

```bash
# Show resource counts
fhir server stats

# Show server capabilities
fhir server info
```

## Using the Python API

### FHIRPath

```python
from fhirkit.engine.fhirpath import FHIRPathEvaluator

# Create evaluator
evaluator = FHIRPathEvaluator()

# Patient resource
patient = {
    "resourceType": "Patient",
    "name": [{"family": "Smith", "given": ["John"]}],
    "gender": "male"
}

# Evaluate expressions
family = evaluator.evaluate("Patient.name.family", patient)
print(family)  # ['Smith']

is_male = evaluator.evaluate("Patient.gender = 'male'", patient)
print(is_male)  # True
```

### CQL

```python
from fhirkit.engine.cql import CQLEvaluator

# Create evaluator
evaluator = CQLEvaluator()

# Evaluate expression directly
result = evaluator.evaluate_expression("1 + 2 * 3")
print(result)  # 7

# Compile a library
lib = evaluator.compile("""
    library Example version '1.0'

    define Sum: 1 + 2 + 3
    define Greeting: 'Hello!'

    define function Double(x Integer):
        x * 2
""")

# Evaluate definitions
sum_result = evaluator.evaluate_definition("Sum")
print(sum_result)  # 6

greeting = evaluator.evaluate_definition("Greeting")
print(greeting)  # 'Hello!'

# Evaluate all definitions
all_results = evaluator.evaluate_all_definitions()
print(all_results)  # {'Sum': 6, 'Greeting': 'Hello!'}

# With patient data
patient = {"resourceType": "Patient", "birthDate": "1990-05-15"}
age = evaluator.evaluate_expression(
    "years between @1990-05-15 and Today()",
    resource=patient
)
```

## Project Structure

```
fhirkit/
├── grammars/              # ANTLR grammar files
│   ├── cql.g4
│   └── fhirpath.g4
├── generated/             # Generated Python parsers
│   ├── cql/
│   └── fhirpath/
├── examples/              # Example files
│   ├── cql/              # 17 CQL example files
│   ├── fhir/             # 14 FHIR JSON resources
│   └── fhirpath/         # FHIRPath expressions
├── src/fhirkit/         # Python source
│   ├── engine/
│   │   ├── cql/          # CQL evaluator
│   │   └── fhirpath/     # FHIRPath evaluator
│   ├── cli.py            # Unified CLI
│   ├── cql_cli.py        # CQL CLI
│   └── fhirpath_cli.py   # FHIRPath CLI
├── tests/                 # Test suite (1225+ tests)
└── docs/                  # Documentation
```

## Example Files

Explore the examples:

```bash
# List CQL examples
ls examples/cql/

# Run a specific example
fhir cql run examples/cql/01_hello_world.cql
fhir cql run examples/cql/10_math_functions.cql
fhir cql run examples/cql/16_clinical_calculations.cql

# View an example
fhir cql show examples/cql/08_quality_measure.cql
```

## Next Steps

- Explore the [CLI Reference](cli.md) for all commands
- Read the [FHIR Server Guide](fhir-server-guide.md) for full server documentation
- Check the [Supported Resources](fhir-server/resources/index.md) for all 37 resource types with examples
- Read the [FHIRPath Guide](fhirpath-guide.md) for comprehensive FHIRPath documentation
- Check the [CQL API](cql-api.md) for Python integration
- Work through the [Tutorial](fhirpath-cql-tutorial.md) for in-depth examples
- Browse the `examples/` folder for real-world patterns
