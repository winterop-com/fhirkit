# FHIR Server Guide

A comprehensive guide to the built-in FHIR R4 server with synthetic data generation.

## What is the FHIR Server?

The `fhir server` command provides a fully functional FHIR R4 REST server designed for:

- **Development & Testing**: Quickly spin up a FHIR server with realistic synthetic data
- **CQL Testing**: Evaluate CQL expressions against generated patient data
- **UI Development**: Build and test FHIR-based applications without external dependencies
- **CI/CD Pipelines**: Reproducible test data for automated testing
- **Demos & Training**: Showcase FHIR applications with realistic data

### Key Features

- **Full FHIR REST API**: CRUD operations, search, history, batch/transaction
- **Synthetic Data Generation**: Realistic clinical data using Faker and clinical code templates
- **Preloading**: Load CQL libraries, ValueSets, and existing FHIR data
- **Reproducibility**: Seed-based generation for consistent test data
- **OpenAPI Documentation**: Built-in Swagger UI for API exploration

---

## Quick Start

### Start Server with Synthetic Data

```bash
# Generate 100 patients with related clinical data
fhir serve --patients 100

# Output:
# Starting FHIR R4 Server
#   Host: 0.0.0.0
#   Port: 8080
#   Synthetic patients: 100
#
# Endpoints:
#   Web UI:       http://0.0.0.0:8080/
#   FHIR API:     http://0.0.0.0:8080/baseR4
#   Metadata:     http://0.0.0.0:8080/baseR4/metadata
#   API Docs:     http://0.0.0.0:8080/docs
```

### Make Your First Request

```bash
# List all patients
curl http://localhost:8080/baseR4/Patient

# Get a specific patient
curl http://localhost:8080/baseR4/Patient/patient-001

# Search by name
curl "http://localhost:8080/baseR4/Patient?name=Smith"

# Get capability statement
curl http://localhost:8080/baseR4/metadata
```

### View Web UI

Open http://localhost:8080/ in your browser to browse resources through the web interface.

### View API Documentation

Open http://localhost:8080/docs in your browser to see the interactive Swagger UI with all available endpoints.

---

## CLI Reference

### fhir serve

Start the FHIR server.

```bash
fhir serve [OPTIONS]
```

#### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--host` | `-h` | `0.0.0.0` | Host to bind to |
| `--port` | `-p` | `8080` | Port to bind to |
| `--patients` | `-n` | `0` | Number of synthetic patients to generate |
| `--seed` | `-s` | None | Random seed for reproducible data |
| `--preload-cql` | | None | Directory of CQL files to preload |
| `--preload-valuesets` | | None | Directory of ValueSet/CodeSystem JSON files |
| `--preload-data` | | None | FHIR Bundle JSON file to preload |
| `--reload` | `-r` | `False` | Enable auto-reload for development |
| `--log-level` | `-l` | `INFO` | Logging level |

#### Examples

```bash
# Start with 100 patients on custom port
fhir serve --patients 100 --port 9000

# Reproducible data with seed
fhir serve --patients 50 --seed 42

# Preload CQL libraries and ValueSets
fhir serve --preload-cql ./cql --preload-valuesets ./valuesets

# Load existing FHIR data
fhir serve --preload-data ./patients-bundle.json

# Development mode with auto-reload
fhir serve --patients 10 --reload
```

### fhir server generate

Generate FHIR resources of a specific type. Supports all 37 resource types.

```bash
fhir server generate RESOURCE_TYPE [OUTPUT] [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `RESOURCE_TYPE` | Type of resource to generate (e.g., Patient, Observation) |
| `OUTPUT` | Output file path (optional - outputs to stdout if not specified) |

#### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--count` | `-n` | `1` | Number of resources to generate |
| `--seed` | `-s` | None | Random seed for reproducible data |
| `--format` | `-f` | `bundle` | Output format: `bundle`, `ndjson`, or `json` |
| `--pretty/--no-pretty` | | `True` | Pretty-print JSON output |
| `--list` | `-l` | | List available resource types |
| `--patient-ref` | | None | Patient reference (e.g., Patient/123) |
| `--practitioner-ref` | | None | Practitioner reference |
| `--organization-ref` | | None | Organization reference |
| `--encounter-ref` | | None | Encounter reference |
| `--hierarchy-depth` | | None | For Location: generate hierarchy (1-6 levels) |
| `--load` | | `False` | Load generated resources directly to FHIR server |
| `--url` | `-u` | `http://localhost:8080` | FHIR server URL (used with --load) |

#### Examples

```bash
# List all available resource types
fhir server generate --list

# Generate 5 patients to stdout
fhir server generate Patient -n 5

# Generate patients to file
fhir server generate Patient ./patients.json -n 10

# Generate observations linked to a patient
fhir server generate Observation -n 5 --patient-ref Patient/123

# Generate location hierarchy (Site → Building → Wing → Room)
fhir server generate Location --hierarchy-depth 4

# Generate with reproducible seed
fhir server generate Condition ./conditions.json -n 20 --seed 42

# Generate and load directly to server
fhir server generate Patient -n 10 --load --url http://localhost:8080

# Pipe to jq for processing
fhir server generate Patient -n 3 | jq '.entry[0].resource.name'

# Generate as NDJSON format
fhir server generate Patient -n 5 -f ndjson
```

### fhir server populate

Populate a FHIR server with linked examples of all 37 resource types. Creates a complete, realistic dataset with proper references between resources.

```bash
fhir server populate [OPTIONS]
```

#### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--url` | `-u` | `http://localhost:8080` | FHIR server URL |
| `--patients` | `-n` | `3` | Number of patients to generate |
| `--seed` | `-s` | None | Random seed for reproducible data |
| `--dry-run` | | `False` | Generate but don't load to server |
| `--output` | `-o` | None | Save generated resources to file |

#### What Gets Generated

Resources are created in dependency order with proper linking:

- **Foundation**: Organizations, Location hierarchy (Site → Building → Wing → Room), Practitioners, ValueSet, CodeSystem
- **Administrative**: PractitionerRoles, Devices
- **Scheduling**: Schedules, Slots, Appointments
- **Per patient**:
  - Patient, RelatedPerson
  - Encounters with linked Conditions, Observations
  - AllergyIntolerance, Immunization
  - CareTeam, CarePlan, Goal, Task
  - Medication, MedicationRequest, Procedure, ServiceRequest
  - DiagnosticReport (linked to Observations), DocumentReference
  - Coverage, Claim, ExplanationOfBenefit (financial chain)
- **Quality Measures**: Library → Measure → MeasureReport (per patient + summary)
- **Groups**: Patient cohort Group with member references

#### Examples

```bash
# Populate local server with 3 patients (default)
fhir server populate

# Populate with more patients
fhir server populate --patients 10

# Dry run - generate without loading
fhir server populate --dry-run --output ./population.json

# With reproducible seed
fhir server populate --seed 42 --patients 5

# Populate remote server
fhir server populate --url http://fhir.example.com --patients 20
```

### fhir server load

Load FHIR resources from a file into a running server.

```bash
fhir server load INPUT_FILE [OPTIONS]
```

#### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--url` | `-u` | `http://localhost:8080` | FHIR server base URL |
| `--batch/--no-batch` | | `True` | Use batch transaction for loading |

#### Examples

```bash
# Load a bundle into the running server
fhir server load ./data.json

# Load to a specific server
fhir server load ./data.json --url http://fhir.example.com

# Load resources individually (no batch)
fhir server load ./data.json --no-batch
```

### fhir server stats

Show statistics for a running FHIR server.

```bash
fhir server stats [OPTIONS]
```

#### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--url` | `-u` | `http://localhost:8080` | FHIR server base URL |

#### Example

```bash
fhir server stats

# Output:
# FHIR Server Statistics
# URL: http://localhost:8080
#
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
# ┃ Resource Type     ┃ Count ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
# │ Condition         │   342 │
# │ Encounter         │   650 │
# │ MedicationRequest │   215 │
# │ Observation       │  1847 │
# │ Organization      │   100 │
# │ Patient           │   100 │
# │ Practitioner      │   100 │
# │ Procedure         │   156 │
# │ ────────────────  │ ───── │
# │ Total             │  3510 │
# └───────────────────┴───────┘
```

### fhir server info

Show server capability statement information.

```bash
fhir server info [OPTIONS]
```

#### Example

```bash
fhir server info

# Output:
# FHIR Server Information
#
#   Name:         FHIR R4 Server
#   Publisher:    fhirkit
#   FHIR Version: 4.0.1
#   Status:       active
#
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
# ┃ Type              ┃ Interactions          ┃ Search Params┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
# │ Patient           │ read, search, create  │           13 │
# │ Condition         │ read, search, create  │            9 │
# │ Observation       │ read, search, create  │            9 │
# │ ...               │ ...                   │          ... │
# └───────────────────┴───────────────────────┴──────────────┘
```

---

## REST API Reference

The FHIR server implements the FHIR R4 REST API specification.

### Base URL

```
http://localhost:8080
```

### Content Types

All endpoints accept and return `application/fhir+json`.

### Capability Statement

```http
GET /metadata
```

Returns the CapabilityStatement describing server capabilities.

```bash
curl http://localhost:8080/baseR4/metadata
```

### CRUD Operations

#### Create Resource

```http
POST /{ResourceType}
Content-Type: application/fhir+json

{resource body}
```

Returns `201 Created` with `Location` header.

```bash
curl -X POST http://localhost:8080/baseR4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "name": [{"family": "Smith", "given": ["John"]}],
    "gender": "male"
  }'
```

#### Read Resource

```http
GET /{ResourceType}/{id}
```

Returns the resource or `404 Not Found`.

```bash
curl http://localhost:8080/baseR4/Patient/patient-001
```

#### Update Resource

```http
PUT /{ResourceType}/{id}
Content-Type: application/fhir+json

{resource body}
```

Updates existing resource or creates with specific ID.

```bash
curl -X PUT http://localhost:8080/baseR4/Patient/patient-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "id": "patient-001",
    "name": [{"family": "Smith", "given": ["John", "William"]}],
    "gender": "male"
  }'
```

#### Delete Resource

```http
DELETE /{ResourceType}/{id}
```

Returns `204 No Content` on success.

```bash
curl -X DELETE http://localhost:8080/baseR4/Patient/patient-001
```

### Search Operations

```http
GET /{ResourceType}?param1=value1&param2=value2
```

#### Common Search Parameters

Available for all resource types:

| Parameter | Type | Description |
|-----------|------|-------------|
| `_id` | token | Resource ID |
| `_count` | number | Results per page (default: 100, max: 1000) |
| `_offset` | number | Pagination offset |
| `_sort` | string | Sort field (prefix with `-` for descending) |

#### Search Parameter Types

| Type | Format | Example |
|------|--------|---------|
| `token` | `[system|]code` | `code=http://loinc.org|8480-6` |
| `string` | text (starts-with) | `name=Smith` |
| `reference` | `[Type/]id` | `patient=Patient/123` |
| `date` | `[prefix]YYYY-MM-DD` | `birthdate=ge1990-01-01` |
| `uri` | exact match | `url=http://example.com/vs` |

#### Date Prefixes

| Prefix | Meaning |
|--------|---------|
| `eq` | Equals (default) |
| `ne` | Not equals |
| `gt` | Greater than |
| `lt` | Less than |
| `ge` | Greater or equal |
| `le` | Less or equal |

#### Search Examples

```bash
# Find patients named Smith
curl "http://localhost:8080/baseR4/Patient?name=Smith"

# Find female patients
curl "http://localhost:8080/baseR4/Patient?gender=female"

# Find patients born after 1990
curl "http://localhost:8080/baseR4/Patient?birthdate=ge1990-01-01"

# Find conditions for a patient
curl "http://localhost:8080/baseR4/Condition?patient=Patient/patient-001"

# Find observations by LOINC code
curl "http://localhost:8080/baseR4/Observation?code=http://loinc.org|8480-6"

# Combined search with pagination
curl "http://localhost:8080/baseR4/Observation?patient=Patient/001&_count=50&_offset=100"
```

### Resource-Specific Search Parameters

#### Patient

| Parameter | Type | Description |
|-----------|------|-------------|
| `identifier` | token | Patient identifier |
| `name` | string | Any part of name |
| `family` | string | Family name |
| `given` | string | Given name |
| `gender` | token | Gender code |
| `birthdate` | date | Birth date |
| `address` | string | Any part of address |
| `address-city` | string | City |
| `address-state` | string | State |
| `address-postalcode` | string | Postal code |
| `telecom` | token | Contact point value |
| `active` | token | Active status |

#### Condition

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient` | reference | Patient reference |
| `subject` | reference | Subject reference |
| `code` | token | Condition code |
| `clinical-status` | token | Clinical status |
| `verification-status` | token | Verification status |
| `category` | token | Category |
| `onset-date` | date | Onset date |
| `severity` | token | Severity |

#### Observation

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient` | reference | Patient reference |
| `subject` | reference | Subject reference |
| `code` | token | Observation code |
| `category` | token | Category |
| `status` | token | Status |
| `date` | date | Effective date |
| `value-quantity` | quantity | Value |
| `encounter` | reference | Encounter reference |

#### MedicationRequest

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient` | reference | Patient reference |
| `code` | token | Medication code |
| `status` | token | Status |
| `intent` | token | Intent |
| `authoredon` | date | Authored date |
| `requester` | reference | Requester reference |
| `encounter` | reference | Encounter reference |

#### Encounter

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient` | reference | Patient reference |
| `status` | token | Status |
| `class` | token | Encounter class |
| `type` | token | Encounter type |
| `date` | date | Period start |
| `participant` | reference | Participant reference |
| `service-provider` | reference | Service provider |

#### Procedure

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient` | reference | Patient reference |
| `code` | token | Procedure code |
| `status` | token | Status |
| `date` | date | Performed date |
| `category` | token | Category |
| `performer` | reference | Performer reference |
| `encounter` | reference | Encounter reference |

### History Operations

#### Instance History

```http
GET /{ResourceType}/{id}/_history
```

Returns all versions of a resource.

```bash
curl http://localhost:8080/baseR4/Patient/patient-001/_history
```

#### Version Read

```http
GET /{ResourceType}/{id}/_history/{versionId}
```

Returns a specific version.

```bash
curl http://localhost:8080/baseR4/Patient/patient-001/_history/2
```

### Batch Operations

```http
POST /
Content-Type: application/fhir+json

{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [...]
}
```

Process multiple operations in a single request.

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Bundle",
    "type": "batch",
    "entry": [
      {
        "resource": {"resourceType": "Patient", "name": [{"family": "Test"}]},
        "request": {"method": "POST", "url": "Patient"}
      },
      {
        "request": {"method": "GET", "url": "Patient/patient-001"}
      }
    ]
  }'
```

### Conditional Operations

FHIR conditional operations allow creating, updating, and deleting resources based on search criteria instead of resource IDs. Conditional read enables efficient caching.

#### Conditional Read (Caching)

Use conditional read headers to avoid transferring unchanged resources:

**If-None-Match** - Compare ETags (resource versions):

```bash
# First, get the resource and note the ETag
curl -i http://localhost:8080/baseR4/Patient/123
# Response headers include: ETag: W/"1"

# Later, check if resource changed
curl -i -H 'If-None-Match: W/"1"' http://localhost:8080/baseR4/Patient/123
# Returns 304 Not Modified if unchanged, 200 with body if changed
```

**If-Modified-Since** - Compare timestamps:

```bash
curl -i -H 'If-Modified-Since: Mon, 16 Dec 2024 00:00:00 GMT' \
  http://localhost:8080/baseR4/Patient/123
# Returns 304 if not modified since that date
```

| Header | Value | Result |
|--------|-------|--------|
| If-None-Match | `W/"version"` | 304 if ETag matches current version |
| If-None-Match | `*` | 304 if resource exists |
| If-Modified-Since | HTTP date | 304 if not modified since date |
| (none) | - | 200 with full resource |

**Multiple ETags:**

```bash
curl -i -H 'If-None-Match: W/"1", W/"2", W/"3"' \
  http://localhost:8080/baseR4/Patient/123
# Returns 304 if current version matches any listed ETag
```

#### Conditional Create

Prevent duplicate resources using the `If-None-Exist` header:

```http
POST /{ResourceType}
If-None-Exist: identifier=MRN123
Content-Type: application/fhir+json

{resource body}
```

| Result | Status | Description |
|--------|--------|-------------|
| No match | 201 | Resource created |
| 1 match | 200 | Existing resource returned (no change) |
| >1 match | 412 | Precondition Failed |

```bash
curl -X POST http://localhost:8080/baseR4/Patient \
  -H "Content-Type: application/fhir+json" \
  -H "If-None-Exist: identifier=http://hospital.org|MRN123" \
  -d '{
    "resourceType": "Patient",
    "identifier": [{"system": "http://hospital.org", "value": "MRN123"}],
    "name": [{"family": "Smith"}]
  }'
```

#### Conditional Update

Update a resource by search criteria instead of ID:

```http
PUT /{ResourceType}?search-params
Content-Type: application/fhir+json

{resource body}
```

| Result | Status | Description |
|--------|--------|-------------|
| No match | 201 | Resource created |
| 1 match | 200 | Resource updated |
| >1 match | 412 | Precondition Failed |

```bash
curl -X PUT "http://localhost:8080/baseR4/Patient?identifier=http://hospital.org|MRN123" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "identifier": [{"system": "http://hospital.org", "value": "MRN123"}],
    "name": [{"family": "Smith", "given": ["John"]}]
  }'
```

#### Conditional Delete

Delete resources matching search criteria:

```http
DELETE /{ResourceType}?search-params
```

Deletes all matching resources and returns `204 No Content`.

```bash
# Delete all cancelled observations
curl -X DELETE "http://localhost:8080/baseR4/Observation?status=cancelled"

# Delete conditions for a specific patient
curl -X DELETE "http://localhost:8080/baseR4/Condition?patient=Patient/123"
```

**Note**: Conditional delete requires at least one search parameter to prevent accidental deletion of all resources.

### Terminology Operations

#### ValueSet $expand

```http
GET /ValueSet/$expand?url={valueSetUrl}
GET /ValueSet/{id}/$expand
POST /ValueSet/$expand
```

Expand a ValueSet to list all codes.

```bash
# By URL
curl "http://localhost:8080/baseR4/ValueSet/\$expand?url=http://example.com/vs/conditions"

# By ID
curl http://localhost:8080/baseR4/ValueSet/vs-001/\$expand

# With filter
curl "http://localhost:8080/baseR4/ValueSet/\$expand?url=http://example.com/vs&filter=diabetes"
```

#### CodeSystem $lookup

```http
GET /CodeSystem/$lookup?system={systemUrl}&code={code}
POST /CodeSystem/$lookup
```

Look up information about a code.

```bash
curl "http://localhost:8080/baseR4/CodeSystem/\$lookup?system=http://snomed.info/sct&code=44054006"
```

#### ValueSet $validate-code

```http
GET /ValueSet/$validate-code?url={valueSetUrl}&code={code}
POST /ValueSet/$validate-code
```

Validate that a code is in a ValueSet.

```bash
curl "http://localhost:8080/baseR4/ValueSet/\$validate-code?url=http://example.com/vs&code=12345"
```

---

## Synthetic Data Generation

### Supported Resource Types

The server supports **37 FHIR R4 resource types** organized by category:

#### Administrative Resources
| Resource Type | Description |
|---------------|-------------|
| Patient | Demographics, identifiers, contacts, emergency contacts |
| Practitioner | Healthcare providers with NPI, qualifications |
| PractitionerRole | Practitioner roles within organizations |
| Organization | Healthcare organizations with identifiers |
| Location | Physical locations with hierarchy support |
| RelatedPerson | Patient contacts and relationships |

#### Clinical Resources
| Resource Type | Description |
|---------------|-------------|
| Encounter | Patient visits (ambulatory, emergency, inpatient, virtual) |
| Condition | Medical diagnoses with clinical status |
| Observation | Vitals and lab results with reference ranges |
| Procedure | Medical procedures with codes |
| DiagnosticReport | Lab and imaging reports linked to Observations |
| AllergyIntolerance | Allergies with reactions and severity |
| Immunization | Vaccination records with codes |

#### Medication Resources
| Resource Type | Description |
|---------------|-------------|
| Medication | Medication definitions |
| MedicationRequest | Prescriptions with dosing instructions |

#### Care Management Resources
| Resource Type | Description |
|---------------|-------------|
| CarePlan | Care plans with activities and goals |
| CareTeam | Care team members and roles |
| Goal | Patient health goals |
| Task | Workflow tasks |

#### Scheduling Resources
| Resource Type | Description |
|---------------|-------------|
| Schedule | Provider schedules |
| Slot | Available appointment slots |
| Appointment | Booked appointments |

#### Financial Resources
| Resource Type | Description |
|---------------|-------------|
| Coverage | Insurance coverage information |
| Claim | Healthcare claims with line items |
| ExplanationOfBenefit | EOB with adjudication details |

#### Device Resources
| Resource Type | Description |
|---------------|-------------|
| Device | Medical devices with UDI |

#### Document Resources
| Resource Type | Description |
|---------------|-------------|
| ServiceRequest | Orders and referrals |
| DocumentReference | Clinical documents and attachments |

#### Forms & Consent Resources
| Resource Type | Description |
|---------------|-------------|
| Questionnaire | Form definitions (PHQ-9, GAD-7, intake forms) |
| QuestionnaireResponse | Completed form responses |
| Consent | Privacy and research consent records |

#### Quality Measure Resources
| Resource Type | Description |
|---------------|-------------|
| Library | CQL libraries with embedded content |
| Measure | Quality measure definitions |
| MeasureReport | Measure evaluation results |

#### Terminology Resources
| Resource Type | Description |
|---------------|-------------|
| ValueSet | Code value sets |
| CodeSystem | Code system definitions |

#### Group Resources
| Resource Type | Description |
|---------------|-------------|
| Group | Patient cohorts and populations |

### Clinical Code Systems

#### SNOMED CT Conditions

The generator includes 50+ common conditions:

| Code | Display |
|------|---------|
| 44054006 | Diabetes mellitus |
| 38341003 | Hypertensive disorder |
| 195967001 | Asthma |
| 55822004 | Hyperlipidemia |
| 414916001 | Obesity |
| 35489007 | Depression |
| 197480006 | Anxiety disorder |
| 13645005 | COPD |
| 396275006 | Osteoarthritis |
| ... | + 40 more |

#### LOINC Vital Signs

| Code | Display | Unit | Normal Range |
|------|---------|------|--------------|
| 8310-5 | Body temperature | Cel | 36.1-37.2 |
| 8867-4 | Heart rate | /min | 60-100 |
| 8480-6 | Systolic blood pressure | mm[Hg] | 90-120 |
| 8462-4 | Diastolic blood pressure | mm[Hg] | 60-80 |
| 2708-6 | Oxygen saturation | % | 95-100 |
| 39156-5 | BMI | kg/m2 | 18.5-24.9 |
| 9279-1 | Respiratory rate | /min | 12-20 |

#### LOINC Laboratory Tests

| Code | Display | Unit | Normal Range |
|------|---------|------|--------------|
| 2345-7 | Glucose | mg/dL | 70-100 |
| 4548-4 | HbA1c | % | 4.0-5.6 |
| 2160-0 | Creatinine | mg/dL | 0.7-1.3 |
| 33914-3 | eGFR | mL/min/1.73m2 | >60 |
| 2093-3 | Total cholesterol | mg/dL | <200 |
| 2089-1 | LDL cholesterol | mg/dL | <100 |
| 2085-9 | HDL cholesterol | mg/dL | >40 |
| 2571-8 | Triglycerides | mg/dL | <150 |

#### RxNorm Medications

The generator includes 100+ common medications:

- **Diabetes**: Metformin, insulin, glipizide
- **Cardiovascular**: Lisinopril, amlodipine, atorvastatin, metoprolol
- **GI**: Omeprazole, pantoprazole
- **Pain**: Ibuprofen, acetaminophen
- **Respiratory**: Albuterol, fluticasone
- **And many more...**

### Data Realism

The generator creates realistic clinical scenarios:

- **Weighted distributions**: Common conditions appear more frequently
- **Realistic vital ranges**: Values within normal/abnormal ranges
- **Temporal relationships**: Encounters happen over time
- **Status consistency**: Active conditions, completed encounters
- **Reference integrity**: All references resolve correctly

### Reproducibility

Use `--seed` for deterministic data generation:

```bash
# These commands produce identical data
fhir serve --patients 100 --seed 42
fhir server generate ./data.json --patients 100 --seed 42
```

This is useful for:
- Automated testing with known data
- Reproducing bugs
- Consistent demos

---

## Preloading Data

### CQL Libraries

Preload CQL files as Library resources:

```bash
fhir serve --preload-cql ./cql-libraries
```

Directory structure:
```
cql-libraries/
├── DiabetesManagement.cql
├── CardiacRisk.cql
└── common/
    └── FHIRHelpers.cql
```

Each CQL file is converted to a FHIR Library resource and can be retrieved:

```bash
curl http://localhost:8080/baseR4/Library?name=DiabetesManagement
```

### ValueSets and CodeSystems

Preload terminology resources:

```bash
fhir serve --preload-valuesets ./terminology
```

Supports:
- Individual JSON files
- FHIR Bundles containing multiple resources
- Nested directories

```
terminology/
├── diabetes-codes.json
├── vital-signs.json
└── bundles/
    └── icd10-bundle.json
```

### Existing FHIR Data

Preload FHIR resources from a file:

```bash
fhir serve --preload-data ./patients-bundle.json
```

Supports:
- Single resources
- FHIR Bundles

---

## Python API

### FHIRStore Class

```python
from fhirkit.server.storage import FHIRStore

# Create store
store = FHIRStore()

# CRUD operations
patient = {
    "resourceType": "Patient",
    "name": [{"family": "Smith", "given": ["John"]}]
}

# Create - assigns ID and meta
created = store.create(patient)
print(created["id"])  # e.g., "abc123"
print(created["meta"]["versionId"])  # "1"

# Read
patient = store.read("Patient", "abc123")

# Update - increments version
patient["name"][0]["given"].append("William")
updated = store.update("Patient", "abc123", patient)
print(updated["meta"]["versionId"])  # "2"

# Delete
deleted = store.delete("Patient", "abc123")

# Search
resources, total = store.search(
    resource_type="Patient",
    params={"name": "Smith"},
    _count=50,
    _offset=0
)

# History
versions = store.history("Patient", "abc123")
```

### PatientRecordGenerator

```python
from fhirkit.server.generator import PatientRecordGenerator

# Create generator with seed for reproducibility
generator = PatientRecordGenerator(seed=42)

# Generate a single patient record with all related resources
resources = generator.generate_patient_record(
    num_conditions=(2, 6),      # 2-6 conditions per patient
    num_encounters=(3, 10),     # 3-10 encounters
    num_observations_per_encounter=(2, 5),
    num_medications=(1, 5),
    num_procedures=(0, 3)
)

print(f"Generated {len(resources)} resources")
# Generated 45 resources (Patient, Practitioner, Organization,
# Encounters, Conditions, Observations, etc.)

# Generate a population
all_resources = generator.generate_population(num_patients=100)
print(f"Total: {len(all_resources)} resources")
```

### Individual Resource Generators

```python
from fhirkit.server.generator import (
    PatientGenerator,
    ConditionGenerator,
    ObservationGenerator,
    MedicationRequestGenerator,
    PractitionerGenerator,
    OrganizationGenerator,
    EncounterGenerator,
    ProcedureGenerator,
)

# Create generators
patient_gen = PatientGenerator(seed=42)
condition_gen = ConditionGenerator(seed=42)

# Generate resources
patient = patient_gen.generate()
patient_ref = f"Patient/{patient['id']}"

condition = condition_gen.generate(patient_ref=patient_ref)
print(condition["code"]["coding"][0]["display"])
# e.g., "Diabetes mellitus"
```

### Creating Custom Server

```python
from fhirkit.server.api import create_app
from fhirkit.server.config import FHIRServerSettings
from fhirkit.server.storage import FHIRStore

# Custom settings
settings = FHIRServerSettings(
    host="0.0.0.0",
    port=8080,
    patients=50,
    seed=42,
    enable_docs=True,
    enable_cors=True,
    cors_origins=["http://localhost:3000"],
)

# Create store and pre-populate
store = FHIRStore()

# Create FastAPI app
app = create_app(settings=settings, store=store)

# Run with uvicorn
import uvicorn
uvicorn.run(app, host=settings.host, port=settings.port)
```

---

## Configuration

### Environment Variables

All settings can be configured via environment variables with the `FHIR_SERVER_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `FHIR_SERVER_HOST` | `0.0.0.0` | Host to bind to |
| `FHIR_SERVER_PORT` | `8080` | Port to bind to |
| `FHIR_SERVER_PATIENTS` | `0` | Synthetic patients |
| `FHIR_SERVER_SEED` | None | Random seed |
| `FHIR_SERVER_PRELOAD_CQL` | None | CQL directory |
| `FHIR_SERVER_PRELOAD_VALUESETS` | None | Terminology directory |
| `FHIR_SERVER_ENABLE_CORS` | `True` | Enable CORS |
| `FHIR_SERVER_CORS_ORIGINS` | `["*"]` | CORS allowed origins |
| `FHIR_SERVER_ENABLE_DOCS` | `True` | Enable Swagger UI |
| `FHIR_SERVER_LOG_LEVEL` | `INFO` | Logging level |
| `FHIR_SERVER_DEFAULT_PAGE_SIZE` | `100` | Default search results |
| `FHIR_SERVER_MAX_PAGE_SIZE` | `1000` | Maximum search results |

### Using .env File

Create a `.env` file:

```env
FHIR_SERVER_PORT=9000
FHIR_SERVER_PATIENTS=100
FHIR_SERVER_SEED=42
FHIR_SERVER_LOG_LEVEL=DEBUG
```

Then start the server:

```bash
fhir serve
```

### FHIRServerSettings Class

```python
from fhirkit.server.config import FHIRServerSettings

settings = FHIRServerSettings(
    # Server
    server_name="My FHIR Server",
    host="0.0.0.0",
    port=8080,
    base_path="",

    # Data generation
    patients=100,
    seed=42,

    # Preloading
    preload_cql="/path/to/cql",
    preload_valuesets="/path/to/valuesets",
    preload_data="/path/to/bundle.json",

    # Features
    enable_terminology=True,
    enable_docs=True,
    enable_cors=True,
    cors_origins=["*"],

    # Logging
    log_level="INFO",
    log_requests=True,

    # Limits
    default_page_size=100,
    max_page_size=1000,
)
```

---

## Examples

### Testing CQL Against Synthetic Data

```bash
# Start server with synthetic data
fhir serve --patients 100 --seed 42 &

# Run CQL evaluation against the server
fhir cql eval "
  define DiabetesPatients:
    [Condition: Code 'http://snomed.info/sct|44054006']
" --data http://localhost:8080
```

### Integration with CDS Hooks

```bash
# Start FHIR server with data
fhir serve --patients 50 --port 8080 &

# Start CDS Hooks server pointing to FHIR server
fhir cds serve --config ./cds-config.yaml --fhir-url http://localhost:8080
```

### Generating Test Data for CI/CD

```bash
# Generate reproducible test data
fhir server generate ./test-data.json --patients 20 --seed 12345

# Use in tests
pytest --fhir-data=./test-data.json
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .
RUN pip install fhir-cql

EXPOSE 8080
CMD ["fhir", "server", "serve", "--patients", "100"]
```

```bash
docker build -t fhir-server .
docker run -p 8080:8080 fhir-server
```

---

## Troubleshooting

### Common Issues

#### Server won't start

```bash
# Check if port is in use
lsof -i :8080

# Use different port
fhir serve --port 9000
```

#### No data generated

```bash
# Ensure --patients is specified
fhir serve --patients 100  # Generates data
fhir serve                 # Empty server
```

#### Search returns no results

```bash
# Check server statistics
fhir server stats

# Verify search parameter format
# Correct:
curl "http://localhost:8080/baseR4/Patient?name=Smith"

# Incorrect (missing quote escaping):
curl http://localhost:8080/baseR4/Patient?name=Smith  # May fail in some shells
```

### Performance Considerations

- **Memory**: Each patient generates ~35 resources. 1000 patients ≈ 35,000 resources in memory
- **Startup time**: Large patient counts (1000+) may take a few seconds to generate
- **Search**: In-memory search scales linearly with resource count

For large datasets, consider:
- Using `--preload-data` with pre-generated data
- Generating data to files and loading on demand
- Using pagination (`_count`, `_offset`) for large result sets

---

## API Documentation

The server provides built-in API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

To disable documentation:

```bash
fhir serve --patients 100
# Set via environment
FHIR_SERVER_ENABLE_DOCS=false fhir serve
```
