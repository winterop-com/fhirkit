# ActivityDefinition

## Overview

An ActivityDefinition is a shareable, consumable description of some activity to be performed. It allows for the definition of activities independent of any specific patient, practitioner, or performance context.

The resource functions as a reusable template for constructing specific request resources like ServiceRequest and MedicationRequest. ActivityDefinitions can be used to specify actions within workflows, order sets, protocols, or as part of activity catalogs.

**Key distinction from related resources:**
- **ActivityDefinition** = abstract conceptual description of an action (template)
- **Task** = tracks a specific instance as it moves through workflow steps
- **Event resources** = indicate an action has been performed
- **Request resources** = indicate actual intent to carry out a particular action

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/activitydefinition.html](https://hl7.org/fhir/R4/activitydefinition.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `url` | uri | Canonical identifier for this activity definition |
| `name` | string | Computer-friendly name |
| `title` | string | Human-friendly title |
| `status` | code | draft, active, retired, unknown |
| `kind` | code | Kind of resource to create (e.g., MedicationRequest, ServiceRequest) |
| `intent` | code | Proposal, plan, directive, order, original-order |
| `priority` | code | routine, urgent, asap, stat |
| `date` | date | Date last changed |
| `publisher` | string | Name of the publisher |
| `description` | string | Natural language description |
| `code` | CodeableConcept | Activity code (e.g., SNOMED CT procedure codes) |
| `topic` | CodeableConcept[] | Treatment, education, assessment topics |
| `productCodeableConcept` | CodeableConcept | Product for medication definitions |
| `dosage` | Dosage[] | Dosage instructions for medications |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=activity-001` |
| `url` | uri | Canonical URL | `url=http://example.org/fhir/ActivityDefinition/bp-check` |
| `name` | string | Computer-friendly name | `name=BPCheck` |
| `title` | string | Human-friendly title | `title=Blood%20Pressure%20Check` |
| `status` | token | Publication status | `status=active` |
| `version` | token | Version identifier | `version=1.0.0` |
| `date` | date | Date last changed | `date=gt2024-01-01` |
| `publisher` | string | Publisher name | `publisher=ACME%20Health` |
| `kind` | token | Kind of resource | `kind=ServiceRequest` |
| `context-type` | token | Use context type | `context-type=workflow` |
| `topic` | token | Topic code | `topic=treatment` |

## Examples

### Create an ActivityDefinition

```bash
curl -X POST http://localhost:8080/baseR4/ActivityDefinition \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ActivityDefinition",
    "url": "http://example.org/fhir/ActivityDefinition/blood-pressure-check",
    "name": "BloodPressureCheck",
    "title": "Blood Pressure Check Protocol",
    "status": "active",
    "kind": "ServiceRequest",
    "intent": "order",
    "priority": "routine",
    "date": "2024-01-15",
    "publisher": "ACME Health Systems",
    "description": "Standard blood pressure measurement procedure",
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "75367002",
        "display": "Blood pressure taking"
      }],
      "text": "Blood pressure taking"
    },
    "topic": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/definition-topic",
        "code": "assessment",
        "display": "Assessment"
      }]
    }]
  }'
```

### Search ActivityDefinitions

```bash
# By status
curl "http://localhost:8080/baseR4/ActivityDefinition?status=active"

# By kind
curl "http://localhost:8080/baseR4/ActivityDefinition?kind=MedicationRequest"

# By topic
curl "http://localhost:8080/baseR4/ActivityDefinition?topic=treatment"

# By publisher
curl "http://localhost:8080/baseR4/ActivityDefinition?publisher=ACME"

# Combined: active medication activities
curl "http://localhost:8080/baseR4/ActivityDefinition?status=active&kind=MedicationRequest"
```

### Read an ActivityDefinition

```bash
curl "http://localhost:8080/baseR4/ActivityDefinition/activity-001"
```

### Update an ActivityDefinition

```bash
curl -X PUT http://localhost:8080/baseR4/ActivityDefinition/activity-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ActivityDefinition",
    "id": "activity-001",
    "status": "retired",
    ...
  }'
```

### Delete an ActivityDefinition

```bash
curl -X DELETE "http://localhost:8080/baseR4/ActivityDefinition/activity-001"
```

## Generator Usage

The `ActivityDefinitionGenerator` creates synthetic ActivityDefinition resources with realistic clinical activity codes and workflow configurations.

```python
from fhirkit.server.generator import ActivityDefinitionGenerator

generator = ActivityDefinitionGenerator(seed=42)

# Generate a random activity definition
activity = generator.generate()

# Generate with specific kind
service_request_activity = generator.generate(kind="ServiceRequest")

# Generate with specific status and intent
order_activity = generator.generate(
    status="active",
    intent="order",
    priority="urgent"
)

# Generate for medication orders
med_activity = generator.generate_for_medication(
    medication_code={
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "197591",
        "display": "Aspirin 81 MG"
    },
    dosage_instruction="Take 1 tablet daily"
)

# Generate batch
activities = generator.generate_batch(count=10)
```

## Kind Codes

| Code | Description |
|------|-------------|
| Appointment | Creates Appointment resources |
| CommunicationRequest | Creates CommunicationRequest resources |
| DeviceRequest | Creates DeviceRequest resources |
| MedicationRequest | Creates MedicationRequest resources |
| NutritionOrder | Creates NutritionOrder resources |
| Task | Creates Task resources |
| ServiceRequest | Creates ServiceRequest resources |
| VisionPrescription | Creates VisionPrescription resources |

## Intent Codes

| Code | Description |
|------|-------------|
| proposal | A suggestion or recommendation |
| plan | An intended action as part of a plan |
| directive | A directive to perform the action |
| order | An authoritative instruction |
| original-order | The original order from which others may derive |

## Priority Codes

| Code | Description |
|------|-------------|
| routine | Normal priority |
| urgent | Urgent priority |
| asap | As soon as possible |
| stat | Immediate priority |

## Related Resources

- [PlanDefinition](./plan-definition.md) - Groups multiple ActivityDefinitions into a protocol
- [ServiceRequest](./service-request.md) - Instance of an activity request
- [MedicationRequest](./medication-request.md) - Instance for medication orders
- [Task](./task.md) - Tracks workflow execution
