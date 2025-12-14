# CDS Hooks Guide

This comprehensive guide covers how to build CQL-based Clinical Decision Support services using the CDS Hooks integration. By the end of this guide, you'll understand how to create, configure, test, and deploy CDS services that integrate with Electronic Health Record (EHR) systems.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Tutorial: Building Your First CDS Service](#tutorial-building-your-first-cds-service)
4. [Tutorial: Medication Safety Service](#tutorial-medication-safety-service)
5. [Configuration Reference](#configuration-reference)
6. [CLI Commands](#cli-commands)
7. [Advanced Topics](#advanced-topics)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Introduction

### What is CDS Hooks?

[CDS Hooks](https://cds-hooks.hl7.org/) is an HL7 standard for integrating Clinical Decision Support (CDS) into Electronic Health Record (EHR) workflows. It provides a standardized way for external CDS services to offer real-time clinical recommendations to healthcare providers at the point of care.

**Key concepts:**

- **Hooks**: Defined points in clinical workflows where CDS can be triggered (e.g., when a patient chart is opened, when a medication is ordered)
- **Services**: External applications that respond to hooks with clinical recommendations
- **Cards**: Visual displays of recommendations presented to clinicians
- **Prefetch**: A mechanism for EHRs to send relevant patient data with the request, avoiding extra round-trips

### Why CDS Hooks + CQL?

Clinical Quality Language (CQL) is a powerful expression language for defining clinical logic. By combining CDS Hooks with CQL, you can:

1. **Write reusable clinical logic** - CQL definitions can be shared across quality measures, alerts, and decision support
2. **Leverage standard terminologies** - CQL supports SNOMED CT, ICD-10, LOINC, RxNorm, and other standard code systems
3. **Express complex conditions** - CQL handles temporal relationships, intervals, and null propagation naturally
4. **Test independently** - CQL logic can be validated without an EHR connection

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         EHR System                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Patient View │  │ Order Entry  │  │ Prescribing  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────┬────────┴────────┬────────┘                   │
│                  │                 │                            │
│          (hook triggers)   (hook triggers)                      │
└──────────────────┼─────────────────┼────────────────────────────┘
                   │                 │
                   ▼                 ▼
              HTTP POST         HTTP POST
              + prefetch        + prefetch
                   │                 │
┌──────────────────┼─────────────────┼────────────────────────────┐
│                  │   CDS Hooks Server                           │
│                  ▼                 ▼                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Service Router (FastAPI)                    │   │
│  │   GET /cds-services           - Discovery                │   │
│  │   POST /cds-services/{id}     - Service Invocation       │   │
│  │   POST /cds-services/{id}/feedback - Feedback            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Service Registry (YAML Config)              │   │
│  │   - Maps service IDs to CQL libraries                   │   │
│  │   - Defines prefetch templates                          │   │
│  │   - Configures card generation                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                CQL Execution Engine                      │   │
│  │   - Parses and compiles CQL libraries                   │   │
│  │   - Evaluates definitions against prefetch data         │   │
│  │   - Returns typed results                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Card Builder                              │   │
│  │   - Evaluates card conditions                           │   │
│  │   - Renders Jinja2 templates                            │   │
│  │   - Builds CDS Hooks response                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
                    JSON Response
                    with Cards
```

---

## Quick Start

Get a CDS Hooks server running in under 5 minutes.

### Step 1: Install Dependencies

```bash
uv sync
```

### Step 2: Create a Minimal Configuration

Create `cds_services.yaml`:

```yaml
services:
  - id: hello-world
    hook: patient-view
    title: Hello World CDS
    description: A simple demonstration service

    cqlLibrary: examples/cql/01_hello_world.cql
    evaluateDefinitions:
      - Greeting

    prefetch:
      patient: Patient/{{context.patientId}}

    cards:
      - indicator: info
        summary: "Hello from CDS Hooks!"
        detail: "This card was generated by evaluating CQL."
        source: Demo CDS Service
```

### Step 3: Start the Server

```bash
fhir cds serve --config cds_services.yaml
```

You should see:

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

### Step 4: Test the Discovery Endpoint

```bash
curl http://localhost:8080/cds-services | python -m json.tool
```

Response:

```json
{
  "services": [
    {
      "hook": "patient-view",
      "id": "hello-world",
      "title": "Hello World CDS",
      "description": "A simple demonstration service",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}"
      }
    }
  ]
}
```

### Step 5: Invoke the Service

```bash
curl -X POST http://localhost:8080/cds-services/hello-world \
  -H "Content-Type: application/json" \
  -d '{
    "hook": "patient-view",
    "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
    "context": {
      "userId": "Practitioner/123",
      "patientId": "456"
    },
    "prefetch": {
      "patient": {
        "resourceType": "Patient",
        "id": "456",
        "name": [{"given": ["John"], "family": "Smith"}]
      }
    }
  }' | python -m json.tool
```

You'll receive a response with cards:

```json
{
  "cards": [
    {
      "uuid": "a1b2c3d4-...",
      "summary": "Hello from CDS Hooks!",
      "detail": "This card was generated by evaluating CQL.",
      "indicator": "info",
      "source": {
        "label": "Demo CDS Service"
      }
    }
  ]
}
```

---

## Tutorial: Building Your First CDS Service

This tutorial walks you through creating a CDS service from scratch. We'll build an age-based reminder service that alerts clinicians when a patient is due for specific screenings based on their age.

### Part 1: Understanding the Requirements

Our service will:
- Trigger on `patient-view` (when a clinician opens a patient's chart)
- Check the patient's age
- Display an info card if the patient is 50+ years old reminding about colorectal cancer screening
- Display a warning card if the patient is 65+ years old with additional screening reminders

### Part 2: Writing the CQL Logic

First, let's create the CQL library that contains our clinical logic.

Create `examples/cql/age_screening.cql`:

```cql
library AgeScreening version '1.0.0'

using FHIR version '4.0.1'

// Define the patient context - all expressions will be evaluated
// in the context of a single patient
context Patient

// Calculate the patient's age in years
define "PatientAge":
  AgeInYears()

// Check if patient is 50 or older
define "Is50OrOlder":
  PatientAge >= 50

// Check if patient is 65 or older
define "Is65OrOlder":
  PatientAge >= 65

// Determine which screenings are due based on age
define "ColorectalScreeningDue":
  Is50OrOlder

define "MedicareScreeningsDue":
  Is65OrOlder

// Summary message for the card
define "ScreeningSummary":
  if Is65OrOlder then
    'Patient is ' & ToString(PatientAge) & ' years old - Medicare screenings recommended'
  else if Is50OrOlder then
    'Patient is ' & ToString(PatientAge) & ' years old - Consider colorectal screening'
  else
    null
```

Test the CQL to make sure it compiles:

```bash
fhir cql check examples/cql/age_screening.cql
```

### Part 3: Creating the Service Configuration

Now we'll create the service configuration that maps our CQL to a CDS Hook.

Create or update `cds_services.yaml`:

```yaml
services:
  # ... other services ...

  - id: age-based-screening
    hook: patient-view
    title: Age-Based Screening Reminders
    description: |
      Provides reminders for age-appropriate health screenings including
      colorectal cancer screening (50+) and Medicare wellness visits (65+).

    # Path to our CQL library
    cqlLibrary: examples/cql/age_screening.cql

    # CQL definitions to evaluate - these will be available in card templates
    evaluateDefinitions:
      - PatientAge
      - Is50OrOlder
      - Is65OrOlder
      - ColorectalScreeningDue
      - MedicareScreeningsDue
      - ScreeningSummary

    # Tell the EHR what data we need
    prefetch:
      patient: Patient/{{context.patientId}}

    # Card templates - these define what gets shown to the clinician
    cards:
      # First card: Medicare screenings for 65+
      - condition: MedicareScreeningsDue
        indicator: warning
        summary: "{{ScreeningSummary}}"
        detail: |
          ## Recommended Screenings

          Based on the patient's age ({{PatientAge}} years), the following
          preventive services are recommended:

          - **Annual Wellness Visit** - Medicare covers one per year
          - **Colorectal Cancer Screening** - Various options available
          - **Bone Density Test** - Recommended for women 65+
          - **Cardiovascular Disease Screening** - Annual lipid panel
          - **Depression Screening** - Annual screening recommended

          Review patient's screening history and discuss options.
        source: Preventive Care CDS
        sourceUrl: https://www.medicare.gov/coverage/preventive-screening-services
        suggestions:
          - label: Order Annual Wellness Visit
            isRecommended: true
            actions:
              - type: create
                description: Create order for Annual Wellness Visit
        links:
          - label: Medicare Preventive Services
            url: https://www.medicare.gov/coverage/preventive-screening-services
            type: absolute

      # Second card: Colorectal screening for 50-64
      - condition: ColorectalScreeningDue and not MedicareScreeningsDue
        indicator: info
        summary: "{{ScreeningSummary}}"
        detail: |
          ## Colorectal Cancer Screening

          Patient is {{PatientAge}} years old and due for colorectal cancer
          screening if not recently completed.

          **Options:**
          - Colonoscopy (every 10 years)
          - FIT test (annually)
          - FIT-DNA test (every 3 years)
          - Flexible sigmoidoscopy (every 5 years)

          Discuss options with the patient based on their preferences
          and risk factors.
        source: Preventive Care CDS
        links:
          - label: USPSTF Colorectal Cancer Screening Guidelines
            url: https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/colorectal-cancer-screening
            type: absolute
```

### Part 4: Testing the Service

First, validate the configuration:

```bash
fhir cds validate cds_services.yaml
```

List the configured services:

```bash
fhir cds list --config cds_services.yaml
```

Start the server:

```bash
fhir cds serve --config cds_services.yaml
```

Now test with different patient ages. Create a test patient file `test_patient_70.json`:

```json
{
  "resourceType": "Patient",
  "id": "test-70",
  "birthDate": "1954-06-15",
  "name": [{"given": ["Alice"], "family": "Johnson"}],
  "gender": "female"
}
```

Test the service using the CLI:

```bash
fhir cds test age-based-screening --patient test_patient_70.json
```

Or test via curl:

```bash
curl -X POST http://localhost:8080/cds-services/age-based-screening \
  -H "Content-Type: application/json" \
  -d '{
    "hook": "patient-view",
    "hookInstance": "12345678-1234-1234-1234-123456789abc",
    "context": {
      "userId": "Practitioner/1",
      "patientId": "test-70"
    },
    "prefetch": {
      "patient": {
        "resourceType": "Patient",
        "id": "test-70",
        "birthDate": "1954-06-15",
        "name": [{"given": ["Alice"], "family": "Johnson"}],
        "gender": "female"
      }
    }
  }' | python -m json.tool
```

### Part 5: Understanding the Response

For a 70-year-old patient, you'll receive a warning card because `MedicareScreeningsDue` is true:

```json
{
  "cards": [
    {
      "uuid": "...",
      "summary": "Patient is 70 years old - Medicare screenings recommended",
      "detail": "## Recommended Screenings\n\nBased on the patient's age...",
      "indicator": "warning",
      "source": {
        "label": "Preventive Care CDS",
        "url": "https://www.medicare.gov/coverage/preventive-screening-services"
      },
      "suggestions": [
        {
          "label": "Order Annual Wellness Visit",
          "isRecommended": true,
          "actions": [...]
        }
      ],
      "links": [
        {
          "label": "Medicare Preventive Services",
          "url": "https://www.medicare.gov/coverage/preventive-screening-services",
          "type": "absolute"
        }
      ]
    }
  ]
}
```

For a 55-year-old patient, you'll receive the info card about colorectal screening.

For a 40-year-old patient, you'll receive no cards (empty array) because neither condition is met.

---

## Tutorial: Medication Safety Service

This advanced tutorial shows how to build a medication safety service that checks for drug interactions and contraindications when a clinician signs medication orders.

### Part 1: Understanding the order-sign Hook

The `order-sign` hook fires when a clinician is about to sign one or more orders. The context includes:
- `patientId` - The patient receiving the orders
- `userId` - The ordering clinician
- `draftOrders` - Bundle of orders being signed

This is a critical decision point where CDS can prevent medication errors.

### Part 2: The CQL Logic

For medication safety, we need to:
1. Get the patient's current medications
2. Get the medications being ordered
3. Check for interactions between them
4. Check for contraindications based on patient conditions

Here's a simplified version (the full implementation would use a drug interaction database):

```cql
library MedicationSafety version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1'

context Patient

// Get active medications
define "ActiveMedications":
  [MedicationRequest] MR
    where MR.status = 'active'

// Get active conditions
define "ActiveConditions":
  [Condition] C
    where C.clinicalStatus ~ 'active'

// Check for specific high-risk combinations (simplified example)
// In production, this would use a drug interaction database
define "WarfarinOrdered":
  exists (
    [MedicationRequest] MR
      where MR.medication.coding.code contains 'warfarin'
  )

define "NSAIDActive":
  exists (
    ActiveMedications MR
      where MR.medication.coding.code in { 'ibuprofen', 'naproxen', 'aspirin' }
  )

define "HasWarfarinNSAIDInteraction":
  WarfarinOrdered and NSAIDActive

// Check for renal impairment
define "HasRenalImpairment":
  exists (
    ActiveConditions C
      where C.code ~ 'Chronic kidney disease'
  )

// Metformin contraindication in severe renal impairment
define "MetforminOrdered":
  exists (
    [MedicationRequest] MR
      where MR.medication.coding.code contains 'metformin'
  )

define "MetforminContraindicated":
  MetforminOrdered and HasRenalImpairment

// Summary flags
define "HasDrugInteractions":
  HasWarfarinNSAIDInteraction

define "HasContraindications":
  MetforminContraindicated

define "HasAnyAlerts":
  HasDrugInteractions or HasContraindications

// Count for display
define "InteractionCount":
  (if HasWarfarinNSAIDInteraction then 1 else 0)

define "ContraindicationCount":
  (if MetforminContraindicated then 1 else 0)
```

### Part 3: Service Configuration

```yaml
services:
  - id: medication-safety
    hook: order-sign
    title: Medication Safety Alerts
    description: |
      Evaluates medication orders for potential drug-drug interactions,
      drug-disease contraindications, and dosing concerns. Alerts are
      displayed before orders are signed to allow for clinical review.

    cqlLibrary: examples/cql/medication_safety.cql

    evaluateDefinitions:
      - ActiveMedications
      - HasDrugInteractions
      - HasContraindications
      - HasAnyAlerts
      - HasWarfarinNSAIDInteraction
      - MetforminContraindicated
      - InteractionCount
      - ContraindicationCount

    prefetch:
      patient: Patient/{{context.patientId}}
      medications: MedicationRequest?patient={{context.patientId}}&status=active
      conditions: Condition?patient={{context.patientId}}&clinical-status=active

    cards:
      # Critical alert for drug interactions
      - condition: HasWarfarinNSAIDInteraction
        indicator: critical
        summary: "CRITICAL: Warfarin-NSAID Interaction"
        detail: |
          ## High-Risk Drug Interaction

          **Warfarin + NSAID = Increased Bleeding Risk**

          The patient is currently taking an NSAID and warfarin is being ordered.
          This combination significantly increases the risk of:
          - Gastrointestinal bleeding
          - Intracranial hemorrhage
          - Other major bleeding events

          ### Recommendations

          1. **Avoid combination** if possible
          2. If NSAID is necessary, use lowest effective dose for shortest duration
          3. Consider adding a proton pump inhibitor for GI protection
          4. Monitor INR more frequently
          5. Educate patient about bleeding signs

          ### Evidence

          Multiple studies show 3-6x increased risk of GI bleeding with this combination.
        source: Drug Interaction Database
        sourceUrl: https://www.drugs.com/drug-interactions/warfarin.html
        suggestions:
          - label: Review and modify orders
            isRecommended: true
            actions:
              - type: update
                description: Review NSAID therapy and consider alternatives
          - label: Add PPI for GI protection
            actions:
              - type: create
                description: Add proton pump inhibitor order
        links:
          - label: Warfarin Interaction Details
            url: https://www.drugs.com/drug-interactions/warfarin.html
            type: absolute

      # Warning for contraindications
      - condition: MetforminContraindicated
        indicator: warning
        summary: "Metformin contraindicated - Renal impairment present"
        detail: |
          ## Drug-Disease Contraindication

          **Metformin + Chronic Kidney Disease**

          The patient has documented renal impairment. Metformin use in patients
          with reduced kidney function increases the risk of lactic acidosis.

          ### Current Guidelines

          - **eGFR < 30**: Contraindicated
          - **eGFR 30-45**: Use with caution, reduced dose
          - **eGFR > 45**: Generally safe

          ### Action Required

          1. Verify current eGFR
          2. If eGFR < 30, consider alternative diabetes medications
          3. If eGFR 30-45, reduce metformin dose and monitor
        source: Drug Safety Database
        suggestions:
          - label: Check renal function
            isRecommended: true
            actions:
              - type: create
                description: Order comprehensive metabolic panel

      # General alert when any issues found
      - condition: HasAnyAlerts and not HasWarfarinNSAIDInteraction and not MetforminContraindicated
        indicator: info
        summary: "{{InteractionCount}} interaction(s), {{ContraindicationCount}} contraindication(s) identified"
        source: Medication Safety CDS
```

### Part 4: Testing with Realistic Data

Create a test scenario with a patient who has active medications:

`test_patient_meds.json`:
```json
{
  "resourceType": "Patient",
  "id": "pat-456",
  "birthDate": "1960-03-20",
  "name": [{"given": ["Robert"], "family": "Williams"}]
}
```

Test the service by simulating an order-sign request:

```bash
curl -X POST http://localhost:8080/cds-services/medication-safety \
  -H "Content-Type: application/json" \
  -d '{
    "hook": "order-sign",
    "hookInstance": "abc-123-def-456",
    "context": {
      "userId": "Practitioner/dr-smith",
      "patientId": "pat-456",
      "draftOrders": {
        "resourceType": "Bundle",
        "entry": [
          {
            "resource": {
              "resourceType": "MedicationRequest",
              "status": "draft",
              "medicationCodeableConcept": {
                "coding": [{"code": "warfarin", "display": "Warfarin"}]
              }
            }
          }
        ]
      }
    },
    "prefetch": {
      "patient": {
        "resourceType": "Patient",
        "id": "pat-456"
      },
      "medications": {
        "resourceType": "Bundle",
        "entry": [
          {
            "resource": {
              "resourceType": "MedicationRequest",
              "status": "active",
              "medicationCodeableConcept": {
                "coding": [{"code": "ibuprofen", "display": "Ibuprofen 400mg"}]
              }
            }
          }
        ]
      },
      "conditions": {
        "resourceType": "Bundle",
        "entry": []
      }
    }
  }'
```

This will return a critical card warning about the warfarin-NSAID interaction.

---

## Configuration Reference

### Service Configuration

Each service in `cds_services.yaml` supports these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (alphanumeric, hyphens, underscores) |
| `hook` | string | Yes | CDS Hook type (see supported hooks below) |
| `title` | string | Yes | Human-readable title (shown in discovery) |
| `description` | string | Yes | Detailed description |
| `cqlLibrary` | string | Yes | Path to CQL library file |
| `evaluateDefinitions` | list | Yes | CQL definitions to evaluate |
| `prefetch` | object | No | Prefetch templates |
| `cards` | list | No | Card generation templates |
| `enabled` | boolean | No | Whether service is active (default: true) |
| `usageRequirements` | string | No | Human-readable usage note |

### Supported Hooks

| Hook | When It Fires | Typical Use Cases |
|------|---------------|-------------------|
| `patient-view` | Patient chart opened | Reminders, alerts, care gaps |
| `order-select` | Orders being selected | Formulary checks, alternatives |
| `order-sign` | Orders being signed | Drug interactions, contraindications |
| `appointment-book` | Scheduling appointment | Pre-visit planning |
| `encounter-start` | Encounter begins | Admission protocols |
| `encounter-discharge` | Patient discharged | Discharge planning |

### Prefetch Templates

Prefetch templates tell the EHR what FHIR data to include in the request:

```yaml
prefetch:
  # Simple resource reference
  patient: Patient/{{context.patientId}}

  # FHIR search query
  medications: MedicationRequest?patient={{context.patientId}}&status=active

  # Multiple search parameters
  conditions: Condition?patient={{context.patientId}}&clinical-status=active

  # Include related resources
  encounters: Encounter?patient={{context.patientId}}&_include=Encounter:practitioner
```

**Supported placeholders:**
- `{{context.patientId}}` - Patient ID from context
- `{{context.userId}}` - User ID from context
- `{{context.encounterId}}` - Encounter ID (when applicable)

### Card Templates

Card templates control how CQL results become visual recommendations:

```yaml
cards:
  - condition: HasAlerts
    indicator: warning
    summary: "Short summary text"
    detail: |
      Detailed **markdown** content with {{variables}}.
    source: Source Name
    sourceUrl: https://example.org
    suggestions:
      - label: Suggestion text
        isRecommended: true
        actions:
          - type: create
            description: Action description
            resource: { ... }
    links:
      - label: Link text
        url: https://example.org
        type: absolute
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `condition` | string | No | CQL definition or expression that must be truthy |
| `indicator` | string | Yes | `info`, `warning`, or `critical` |
| `summary` | string | Yes | One-line summary (max 140 chars) |
| `detail` | string | No | Markdown detail content |
| `source` | string | Yes | Source label |
| `sourceUrl` | string | No | Source URL |
| `suggestions` | list | No | Suggested actions |
| `links` | list | No | External links |

### Condition Expressions

Card conditions support:

```yaml
# Simple definition reference (truthy check)
condition: HasAlerts

# Comparison operators
condition: AlertCount > 0
condition: RiskScore >= 10

# Boolean operators
condition: HasInteractions and HasContraindications
condition: IsHighRisk or IsModerateRisk
condition: not IsLowRisk

# Combined expressions
condition: HasAlerts and AlertCount > 0
```

### Template Variables

Use Jinja2 syntax in `summary` and `detail` fields:

```yaml
# Simple variable substitution
summary: "{{PatientName}} has {{AlertCount}} alerts"

# Filters
summary: "{{Alerts|length}} alert(s) found"

# Conditionals
detail: |
  {% if IsHighRisk %}
  ## High Risk Warning
  {% endif %}

# Loops
detail: |
  ## Active Medications
  {% for med in ActiveMedications %}
  - {{med.display}}
  {% endfor %}

# Default values
summary: "Score: {{RiskScore|default('N/A')}}"
```

---

## CLI Commands

### `fhir cds serve`

Start the CDS Hooks server.

```bash
fhir cds serve [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host, -h` | 0.0.0.0 | Host to bind to |
| `--port, -p` | 8080 | Port to bind to |
| `--config, -c` | cds_services.yaml | Configuration file |
| `--reload, -r` | false | Enable auto-reload (development) |
| `--cql-path` | "" | Base path for CQL files |

Examples:

```bash
# Development with auto-reload
fhir cds serve --reload --port 8000

# Production
fhir cds serve --host 0.0.0.0 --port 80 --config /etc/cds/services.yaml
```

### `fhir cds validate`

Validate a configuration file.

```bash
fhir cds validate CONFIG_FILE
```

Example:

```bash
fhir cds validate cds_services.yaml
```

### `fhir cds list`

List configured services.

```bash
fhir cds list [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--config, -c` | cds_services.yaml | Configuration file |

### `fhir cds test`

Test a service with sample data.

```bash
fhir cds test SERVICE_ID [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--config, -c` | cds_services.yaml | Configuration file |
| `--patient, -p` | None | Patient JSON file |

Example:

```bash
fhir cds test medication-safety --patient test_patient.json
```

---

## Advanced Topics

### Custom Data Sources

By default, CQL evaluation uses the prefetch data. You can extend this by creating custom data sources:

```python
from fhirkit.engine.cql.datasource import DataSource

class FHIRServerDataSource(DataSource):
    """Data source that fetches from a FHIR server."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def retrieve(self, resource_type: str, **params):
        # Implement FHIR search
        pass
```

### Caching CQL Libraries

The executor caches compiled CQL libraries. Clear the cache when libraries change:

```python
from fhirkit.cds_hooks.service.executor import CDSExecutor

executor = CDSExecutor(settings)
executor.clear_cache()  # Clear all
executor.clear_cache("medication-safety")  # Clear specific service
```

### Custom Card Builders

Extend the card builder for custom logic:

```python
from fhirkit.cds_hooks.service.card_builder import CardBuilder

class CustomCardBuilder(CardBuilder):
    def _build_template_context(self, results):
        context = super()._build_template_context(results)
        # Add custom context variables
        context['institution'] = 'Example Hospital'
        return context
```

### Feedback Handling

CDS Hooks supports feedback to track which cards were accepted/rejected:

```bash
curl -X POST http://localhost:8080/cds-services/medication-safety/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "card": "card-uuid",
    "outcome": "accepted",
    "acceptedSuggestions": ["suggestion-uuid"]
  }'
```

---

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY generated/ ./generated/
COPY examples/ ./examples/

# Install dependencies
RUN uv sync --frozen

# Copy configuration
COPY cds_services.yaml ./

EXPOSE 8080

# Run the server
CMD ["uv", "run", "fhir", "cds", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:

```bash
docker build -t cds-hooks-server .
docker run -p 8080:8080 cds-hooks-server
```

### Docker Compose

```yaml
version: '3.8'

services:
  cds-hooks:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./cds_services.yaml:/app/cds_services.yaml:ro
      - ./cql:/app/cql:ro
    environment:
      - CDS_HOOKS_LOG_LEVEL=INFO
      - CDS_HOOKS_ENABLE_CORS=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cds-hooks-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cds-hooks
  template:
    metadata:
      labels:
        app: cds-hooks
    spec:
      containers:
      - name: cds-hooks
        image: your-registry/cds-hooks-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: CDS_HOOKS_LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: cds-hooks-service
spec:
  selector:
    app: cds-hooks
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CDS_HOOKS_HOST` | Server host | 0.0.0.0 |
| `CDS_HOOKS_PORT` | Server port | 8080 |
| `CDS_HOOKS_SERVICES_CONFIG_PATH` | Config file path | cds_services.yaml |
| `CDS_HOOKS_CQL_LIBRARY_PATH` | CQL library base path | (current dir) |
| `CDS_HOOKS_ENABLE_CORS` | Enable CORS | true |
| `CDS_HOOKS_ALLOWED_ORIGINS` | CORS allowed origins | ["*"] |
| `CDS_HOOKS_LOG_LEVEL` | Logging level | INFO |
| `CDS_HOOKS_LOG_REQUESTS` | Log incoming requests | true |
| `CDS_HOOKS_MAX_CARDS_PER_RESPONSE` | Max cards returned | 10 |
| `CDS_HOOKS_EVALUATION_TIMEOUT_SECONDS` | CQL timeout | 30 |

### Health Monitoring

The server exposes health endpoints:

```bash
# Basic health check
curl http://localhost:8080/health
# Returns: {"status": "healthy"}

# OpenAPI documentation
curl http://localhost:8080/docs
```

---

## Troubleshooting

### Service Not Found (404)

**Symptoms:** `GET /cds-services` returns empty list or `POST /cds-services/{id}` returns 404.

**Solutions:**
1. Verify the service ID matches exactly (case-sensitive)
2. Check if the service is enabled: `enabled: true`
3. Validate the config file: `fhir cds validate cds_services.yaml`
4. Check server logs for loading errors

### CQL Library Not Found

**Symptoms:** Error message about missing CQL file.

**Solutions:**
1. Check the `cqlLibrary` path is correct and file exists
2. Use `--cql-path` to set the base directory
3. Verify file permissions
4. Test the CQL file independently: `fhir cql check path/to/file.cql`

### Empty Cards Response

**Symptoms:** Service returns `{"cards": []}` when you expect cards.

**Solutions:**
1. Check card conditions - they may not be met
2. Use `fhir cds test <service-id>` to see raw CQL results
3. Verify prefetch data contains expected resources
4. Test with explicit `condition: true` to confirm card generation works

### Template Rendering Errors

**Symptoms:** Card text shows raw template syntax like `{{variable}}`.

**Solutions:**
1. Verify variable names match CQL definition names exactly
2. Check Jinja2 syntax is correct
3. Use simpler templates as a fallback
4. Check server logs for template errors

### CQL Evaluation Errors

**Symptoms:** CQL definitions return error objects.

**Solutions:**
1. Test CQL independently: `fhir cql check file.cql`
2. Verify FHIR data structure matches CQL expectations
3. Check for null handling in CQL expressions
4. Review CQL logs for specific error messages

### Performance Issues

**Symptoms:** Slow response times.

**Solutions:**
1. Reduce number of `evaluateDefinitions`
2. Optimize CQL queries (avoid expensive operations)
3. Increase `CDS_HOOKS_EVALUATION_TIMEOUT_SECONDS`
4. Enable CQL library caching (default)
5. Scale horizontally with multiple server instances

---

## API Reference

### Discovery Endpoint

```
GET /cds-services
```

Returns available CDS services for EHR integration.

**Response:**

```json
{
  "services": [
    {
      "hook": "patient-view",
      "id": "service-id",
      "title": "Service Title",
      "description": "Service description",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}"
      }
    }
  ]
}
```

### Service Invocation

```
POST /cds-services/{service-id}
```

Invoke a CDS service with patient context.

**Request:**

```json
{
  "hook": "patient-view",
  "hookInstance": "uuid",
  "fhirServer": "https://ehr.example.org/fhir",
  "fhirAuthorization": {
    "access_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "patient/*.read",
    "subject": "user-id"
  },
  "context": {
    "userId": "Practitioner/123",
    "patientId": "Patient/456"
  },
  "prefetch": {
    "patient": { "resourceType": "Patient", "id": "456" }
  }
}
```

**Response:**

```json
{
  "cards": [
    {
      "uuid": "card-uuid",
      "summary": "Card summary",
      "detail": "Detailed markdown...",
      "indicator": "warning",
      "source": {
        "label": "Source Name",
        "url": "https://source.url"
      },
      "suggestions": [
        {
          "label": "Suggestion label",
          "uuid": "suggestion-uuid",
          "isRecommended": true,
          "actions": [
            {
              "type": "create",
              "description": "Action description",
              "resource": { ... }
            }
          ]
        }
      ],
      "links": [
        {
          "label": "Link text",
          "url": "https://link.url",
          "type": "absolute"
        }
      ]
    }
  ]
}
```

### Feedback Endpoint

```
POST /cds-services/{service-id}/feedback
```

Submit feedback about card interactions.

**Request:**

```json
{
  "card": "card-uuid",
  "outcome": "accepted",
  "acceptedSuggestions": ["suggestion-uuid"],
  "overrideReason": {
    "reason": {
      "coding": [{"code": "contraindication"}]
    },
    "userComment": "Patient has documented allergy"
  }
}
```

### Health Check

```
GET /health
```

Returns server health status.

**Response:**

```json
{
  "status": "healthy"
}
```

### Python API

Use the CDS Hooks module programmatically:

```python
from fhirkit.cds_hooks import create_app, CDSHooksSettings

# Custom settings
settings = CDSHooksSettings(
    services_config_path="my_services.yaml",
    cql_library_path="cql/",
    enable_cors=True,
    allowed_origins=["https://ehr.example.org"],
)

# Create FastAPI app
app = create_app(settings)

# Run with uvicorn
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## Further Reading

- [CDS Hooks 2.0 Specification](https://cds-hooks.hl7.org/2.0/) - Official specification
- [CQL Specification](https://cql.hl7.org/) - Clinical Quality Language
- [SMART on FHIR](https://smarthealthit.org/) - Related authorization standard
- [HL7 FHIR R4](https://hl7.org/fhir/R4/) - FHIR specification
- [FHIR Clinical Reasoning](https://hl7.org/fhir/clinicalreasoning-module.html) - CQL in FHIR context
