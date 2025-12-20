# PlanDefinition

## Overview

A PlanDefinition represents a pre-defined group of actions to be taken in particular circumstances. It is used to define clinical protocols, order sets, ECA rules (Event-Condition-Action), and workflow definitions.

PlanDefinitions orchestrate multiple activities by grouping related ActivityDefinitions and specifying their relationships, triggers, and conditions. They serve as reusable templates for clinical decision support and care planning.

**Common use cases:**
- Clinical protocols (e.g., diabetes management)
- Order sets (e.g., admission orders)
- Clinical decision support rules
- Care pathway definitions
- Workflow orchestration

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/plandefinition.html](https://hl7.org/fhir/R4/plandefinition.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `url` | uri | Canonical identifier for this plan definition |
| `name` | string | Computer-friendly name |
| `title` | string | Human-friendly title |
| `status` | code | draft, active, retired, unknown |
| `type` | CodeableConcept | Type of plan (order-set, clinical-protocol, eca-rule, workflow-definition) |
| `date` | date | Date last changed |
| `publisher` | string | Name of the publisher |
| `description` | string | Natural language description |
| `subjectCodeableConcept` | CodeableConcept | Type of subject (e.g., Patient) |
| `action` | BackboneElement[] | Actions to perform |
| `action.title` | string | Title of the action |
| `action.description` | string | Description of the action |
| `action.trigger` | TriggerDefinition[] | When the action should be triggered |
| `action.definitionCanonical` | canonical | Reference to ActivityDefinition |
| `action.relatedAction` | BackboneElement[] | Relationships to other actions |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=plan-001` |
| `url` | uri | Canonical URL | `url=http://example.org/fhir/PlanDefinition/diabetes-care` |
| `name` | string | Computer-friendly name | `name=DiabetesCare` |
| `title` | string | Human-friendly title | `title=Diabetes%20Care%20Protocol` |
| `status` | token | Publication status | `status=active` |
| `version` | token | Version identifier | `version=2.0.0` |
| `date` | date | Date last changed | `date=gt2024-01-01` |
| `publisher` | string | Publisher name | `publisher=ACME%20Health` |
| `type` | token | Type of plan | `type=order-set` |
| `context-type` | token | Use context type | `context-type=workflow` |
| `definition` | reference | ActivityDefinition reference | `definition=ActivityDefinition/bp-check` |

## Examples

### Create a PlanDefinition

```bash
curl -X POST http://localhost:8080/baseR4/PlanDefinition \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "PlanDefinition",
    "url": "http://example.org/fhir/PlanDefinition/diabetes-care-protocol",
    "name": "DiabetesCareProtocol",
    "title": "Diabetes Care Protocol",
    "status": "active",
    "date": "2024-01-15",
    "publisher": "ACME Health Systems",
    "description": "Standard protocol for diabetes patient care",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
        "code": "clinical-protocol",
        "display": "Clinical Protocol"
      }]
    },
    "subjectCodeableConcept": {
      "coding": [{
        "system": "http://hl7.org/fhir/resource-types",
        "code": "Patient"
      }]
    },
    "action": [
      {
        "title": "Initial Assessment",
        "description": "Perform initial diabetes assessment",
        "definitionCanonical": "http://example.org/fhir/ActivityDefinition/diabetes-assessment"
      },
      {
        "title": "Lab Orders",
        "description": "Order HbA1c and fasting glucose",
        "definitionCanonical": "http://example.org/fhir/ActivityDefinition/diabetes-labs"
      }
    ]
  }'
```

### Search PlanDefinitions

```bash
# By status
curl "http://localhost:8080/baseR4/PlanDefinition?status=active"

# By type
curl "http://localhost:8080/baseR4/PlanDefinition?type=order-set"

# By publisher
curl "http://localhost:8080/baseR4/PlanDefinition?publisher=ACME"

# Combined: active clinical protocols
curl "http://localhost:8080/baseR4/PlanDefinition?status=active&type=clinical-protocol"
```

### Read a PlanDefinition

```bash
curl "http://localhost:8080/baseR4/PlanDefinition/plan-001"
```

### Update a PlanDefinition

```bash
curl -X PUT http://localhost:8080/baseR4/PlanDefinition/plan-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "PlanDefinition",
    "id": "plan-001",
    "status": "retired",
    ...
  }'
```

### Delete a PlanDefinition

```bash
curl -X DELETE "http://localhost:8080/baseR4/PlanDefinition/plan-001"
```

## Generator Usage

The `PlanDefinitionGenerator` creates synthetic PlanDefinition resources with realistic clinical protocol configurations.

```python
from fhirkit.server.generator import PlanDefinitionGenerator

generator = PlanDefinitionGenerator(seed=42)

# Generate a random plan definition
plan = generator.generate()

# Generate with specific type
protocol = generator.generate(
    title="Hypertension Management",
    plan_type={
        "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
        "code": "clinical-protocol",
        "display": "Clinical Protocol"
    }
)

# Generate an order set with specific activities
order_set = generator.generate_order_set(
    title="Admission Orders",
    activity_definitions=[
        "http://example.org/fhir/ActivityDefinition/vitals",
        "http://example.org/fhir/ActivityDefinition/labs",
        "http://example.org/fhir/ActivityDefinition/meds"
    ]
)

# Generate batch
plans = generator.generate_batch(count=10)
```

## Plan Type Codes

| Code | Display | Description |
|------|---------|-------------|
| order-set | Order Set | A group of orders |
| clinical-protocol | Clinical Protocol | A clinical guideline |
| eca-rule | ECA Rule | Event-Condition-Action rule for CDS |
| workflow-definition | Workflow Definition | Workflow or process definition |

## Action Trigger Types

| Type | Description |
|------|-------------|
| named-event | Trigger on named event |
| periodic | Trigger periodically |
| data-changed | Trigger when data changes |
| data-added | Trigger when data is added |
| data-modified | Trigger when data is modified |
| data-removed | Trigger when data is removed |
| data-accessed | Trigger when data is accessed |

## Related Resources

- [ActivityDefinition](./activity-definition.md) - Individual activities within the plan
- [CarePlan](./care-plan.md) - Instance of a care plan for a patient
- [RequestGroup](./request-group.md) - Group of requests from plan execution
- [Library](./library.md) - Logic referenced by the plan
