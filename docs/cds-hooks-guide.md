# CDS Hooks Guide

This guide covers how to use the CDS Hooks integration to expose CQL-based clinical decision support services.

## Introduction

### What is CDS Hooks?

[CDS Hooks](https://cds-hooks.hl7.org/) is an HL7 standard for integrating Clinical Decision Support (CDS) into Electronic Health Record (EHR) workflows. It defines:

- **Hooks**: Trigger points in clinical workflows (e.g., `patient-view`, `order-sign`)
- **Services**: CDS logic that responds to hooks with decision support
- **Cards**: Visual recommendations returned to clinicians
- **Prefetch**: Templates for data the service needs from the EHR

### How This Integration Works

This implementation lets you:
1. Write clinical logic in CQL (Clinical Quality Language)
2. Configure services that map CQL definitions to CDS Hooks
3. Run a server that EHR systems can integrate with
4. Return decision support cards based on CQL evaluation results

```
EHR System                     CDS Hooks Server
    │                               │
    │  POST /cds-services/med-safety │
    │  {hook, context, prefetch}    │
    │ ─────────────────────────────>│
    │                               │  ┌─────────────┐
    │                               │──│ CQL Engine  │
    │                               │  └─────────────┘
    │      {cards: [...]}           │
    │ <─────────────────────────────│
    │                               │
```

## Quick Start

### 1. Install Dependencies

The CDS Hooks module requires additional dependencies. If you haven't already:

```bash
uv sync
```

### 2. Create a Configuration File

Create `cds_services.yaml` in your project root:

```yaml
services:
  - id: hello-world
    hook: patient-view
    title: Hello World CDS
    description: A simple CDS service example

    cqlLibrary: examples/cql/01_hello_world.cql
    evaluateDefinitions:
      - Greeting

    prefetch:
      patient: Patient/{{context.patientId}}

    cards:
      - condition: Greeting
        indicator: info
        summary: "Hello from CDS Hooks!"
        detail: "CQL returned: {{Greeting}}"
        source: Hello World CDS
```

### 3. Start the Server

```bash
fhir cds serve --config cds_services.yaml
```

Output:
```
Starting CDS Hooks server
  Host: 0.0.0.0
  Port: 8080
  Config: cds_services.yaml

Endpoints:
  Discovery: http://0.0.0.0:8080/cds-services
  API Docs:  http://0.0.0.0:8080/docs
  Health:    http://0.0.0.0:8080/health
```

### 4. Test the Discovery Endpoint

```bash
curl http://localhost:8080/cds-services
```

Response:
```json
{
  "services": [
    {
      "hook": "patient-view",
      "id": "hello-world",
      "title": "Hello World CDS",
      "description": "A simple CDS service example",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}"
      }
    }
  ]
}
```

### 5. Invoke the Service

```bash
curl -X POST http://localhost:8080/cds-services/hello-world \
  -H "Content-Type: application/json" \
  -d '{
    "hook": "patient-view",
    "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
    "context": {
      "userId": "Practitioner/123",
      "patientId": "Patient/456"
    },
    "prefetch": {
      "patient": {
        "resourceType": "Patient",
        "id": "456",
        "name": [{"given": ["John"], "family": "Smith"}]
      }
    }
  }'
```

## Configuration Reference

### Service Configuration

Each service in `cds_services.yaml` has the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique service identifier (alphanumeric, hyphens, underscores) |
| `hook` | Yes | CDS Hook type: `patient-view`, `order-select`, `order-sign`, etc. |
| `title` | Yes | Human-readable service title |
| `description` | Yes | Service description |
| `cqlLibrary` | Yes | Path to the CQL library file |
| `evaluateDefinitions` | Yes | List of CQL definitions to evaluate |
| `prefetch` | No | Prefetch templates (see below) |
| `cards` | No | Card templates for generating responses |
| `enabled` | No | Whether the service is active (default: true) |
| `usageRequirements` | No | Human-readable usage requirements |

### Prefetch Templates

Prefetch templates tell the EHR what data to send with the request:

```yaml
prefetch:
  patient: Patient/{{context.patientId}}
  medications: MedicationRequest?patient={{context.patientId}}&status=active
  conditions: Condition?patient={{context.patientId}}&clinical-status=active
```

The `{{context.patientId}}` placeholder is replaced with the actual patient ID.

### Card Templates

Cards define how CQL results become decision support:

```yaml
cards:
  - condition: HasDrugInteractions
    indicator: warning
    summary: "{{ActiveDrugInteractions|length}} drug interaction(s) detected"
    detail: |
      ## Drug Interactions

      {% for interaction in interactions %}
      - {{interaction}}
      {% endfor %}
    source: Medication Safety CDS
    sourceUrl: https://example.org/med-safety
    suggestions:
      - label: Review interactions
        isRecommended: true
        actions:
          - type: create
            description: Create drug review task
    links:
      - label: Drug Interaction Reference
        url: https://example.org/interactions
        type: absolute
```

#### Card Fields

| Field | Required | Description |
|-------|----------|-------------|
| `condition` | No | CQL definition that must be truthy to show the card |
| `indicator` | Yes | `info`, `warning`, or `critical` |
| `summary` | Yes | One-line summary (max 140 chars, supports templates) |
| `detail` | No | Markdown detail (supports Jinja2 templates) |
| `source` | Yes | Source label |
| `sourceUrl` | No | Source URL |
| `suggestions` | No | Suggested actions |
| `links` | No | External links |

#### Template Variables

Templates can use any CQL definition result:

- `{{DefinitionName}}` - Direct value
- `{{DefinitionName|length}}` - List length
- `{% for item in list %}...{% endfor %}` - Iteration
- `{% if condition %}...{% endif %}` - Conditionals

## CLI Commands

### Start Server

```bash
fhir cds serve [OPTIONS]
```

Options:
- `--host, -h`: Host to bind to (default: 0.0.0.0)
- `--port, -p`: Port to bind to (default: 8080)
- `--config, -c`: Services config file (default: cds_services.yaml)
- `--reload, -r`: Enable auto-reload for development
- `--cql-path`: Base path for CQL library files

### Validate Configuration

```bash
fhir cds validate cds_services.yaml
```

### List Services

```bash
fhir cds list --config cds_services.yaml
```

### Test a Service

```bash
fhir cds test medication-safety --patient patient.json
```

## Example Services

### Medication Safety Alerts

Checks for drug interactions and contraindications when orders are signed:

```yaml
- id: medication-safety-alerts
  hook: order-sign
  title: Medication Safety Alerts
  description: Evaluates medication orders for safety issues

  cqlLibrary: examples/cql/24_medication_safety.cql
  evaluateDefinitions:
    - HasDrugInteractions
    - ActiveDrugInteractions
    - RenalDosingAlerts
    - BeersListAlert

  prefetch:
    patient: Patient/{{context.patientId}}
    medications: MedicationRequest?patient={{context.patientId}}&status=active
    conditions: Condition?patient={{context.patientId}}&clinical-status=active

  cards:
    - condition: HasDrugInteractions
      indicator: warning
      summary: "Drug Interaction Alert"
      source: Medication Safety CDS
```

### Cardiovascular Risk Assessment

Calculates CHA2DS2-VASc score for atrial fibrillation patients:

```yaml
- id: cardiovascular-risk
  hook: patient-view
  title: Cardiovascular Risk Assessment
  description: Calculates stroke risk for AFib patients

  cqlLibrary: examples/cql/23_risk_scores.cql
  evaluateDefinitions:
    - HasAtrialFibrillation
    - CHA2DS2VAScScore
    - AnticoagulationRecommended

  cards:
    - condition: AnticoagulationRecommended
      indicator: warning
      summary: "Stroke Risk: Anticoagulation recommended"
      source: Clinical Risk Calculator
```

### Immunization Recommendations

Reviews vaccination status and recommends due immunizations:

```yaml
- id: immunization-recommendations
  hook: patient-view
  title: Immunization Recommendations
  description: Reviews vaccination history

  cqlLibrary: examples/cql/21_immunizations.cql
  evaluateDefinitions:
    - NumberOfVaccinesDue
    - FluVaccineRecommended
    - COVIDBoosterRecommended

  cards:
    - condition: NumberOfVaccinesDue > 0
      indicator: info
      summary: "{{NumberOfVaccinesDue}} vaccination(s) due"
      source: Immunization Registry
```

## CDS Hooks Specification

### Supported Hooks

| Hook | Trigger Point |
|------|---------------|
| `patient-view` | When patient chart is opened |
| `order-select` | When orders are being selected |
| `order-sign` | When orders are being signed |
| `appointment-book` | When appointment is being booked |
| `encounter-start` | When encounter begins |
| `encounter-discharge` | When patient is discharged |

### Request Format

```json
{
  "hook": "patient-view",
  "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
  "fhirServer": "https://ehr.example.org/fhir",
  "context": {
    "userId": "Practitioner/123",
    "patientId": "Patient/456"
  },
  "prefetch": {
    "patient": { "resourceType": "Patient", "id": "456" }
  }
}
```

### Response Format

```json
{
  "cards": [
    {
      "uuid": "card-123",
      "summary": "Drug interaction detected",
      "detail": "Detailed markdown content...",
      "indicator": "warning",
      "source": {
        "label": "Medication Safety CDS"
      },
      "suggestions": [...],
      "links": [...]
    }
  ]
}
```

## Deployment

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8080

CMD ["uv", "run", "fhir", "cds", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

### Environment Variables

Configure the server using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CDS_HOOKS_HOST` | Server host | 0.0.0.0 |
| `CDS_HOOKS_PORT` | Server port | 8080 |
| `CDS_HOOKS_SERVICES_CONFIG_PATH` | Config file path | cds_services.yaml |
| `CDS_HOOKS_CQL_LIBRARY_PATH` | CQL library base path | (current dir) |
| `CDS_HOOKS_ENABLE_CORS` | Enable CORS | true |
| `CDS_HOOKS_ALLOWED_ORIGINS` | CORS origins | ["*"] |
| `CDS_HOOKS_LOG_LEVEL` | Log level | INFO |

### Health Check

The server exposes a health check endpoint:

```bash
curl http://localhost:8080/health
# {"status": "healthy"}
```

## Troubleshooting

### Service Not Found

If you get a 404 error when calling a service:
1. Check the service ID matches exactly
2. Verify the config file is loaded: `fhir cds list`
3. Ensure `enabled: true` (or not set)

### CQL Library Not Found

If CQL evaluation fails:
1. Check the `cqlLibrary` path is correct
2. Use `--cql-path` to set the base directory
3. Verify the CQL file exists and is valid: `fhir cql check <file>`

### Empty Cards Response

If no cards are returned:
1. Check card conditions are met by CQL results
2. Use `fhir cds test <service-id>` to see CQL results
3. Verify prefetch data contains expected resources

### Template Errors

If card text shows template syntax:
1. Check Jinja2 syntax is correct
2. Verify variable names match CQL definition names
3. Use simple `{{variable}}` substitution as fallback

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cds-services` | Discovery - list available services |
| POST | `/cds-services/{id}` | Invoke a CDS service |
| POST | `/cds-services/{id}/feedback` | Submit feedback on cards |
| GET | `/health` | Health check |
| GET | `/docs` | OpenAPI documentation |

### Python API

You can also use the CDS Hooks module programmatically:

```python
from fhir_cql.cds_hooks import create_app, CDSHooksSettings

# Create custom settings
settings = CDSHooksSettings(
    services_config_path="my_services.yaml",
    cql_library_path="cql/",
)

# Create FastAPI app
app = create_app(settings)

# Run with uvicorn
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
```

## Further Reading

- [CDS Hooks Specification](https://cds-hooks.hl7.org/2.0/)
- [CQL Specification](https://cql.hl7.org/)
- [SMART on FHIR](https://smarthealthit.org/)
- [HL7 FHIR](https://hl7.org/fhir/)
