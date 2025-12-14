# Goal

## Overview

The Goal resource describes a desired state of health for a patient. It represents an intended objective of care, which can be achieved through activities and is used to track health outcomes over time.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/goal.html](https://hl7.org/fhir/R4/goal.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `lifecycleStatus` | code | proposed, planned, accepted, active, on-hold, completed, cancelled, etc. |
| `achievementStatus` | CodeableConcept | in-progress, improving, worsening, achieved, not-achieved, etc. |
| `priority` | CodeableConcept | high-priority, medium-priority, low-priority |
| `description` | CodeableConcept | What goal is being pursued (SNOMED CT) |
| `subject` | Reference(Patient) | Who the goal is for |
| `startDate` | date | When work towards goal started |
| `target` | BackboneElement[] | Target outcome with measure and due date |
| `expressedBy` | Reference(Patient\|Practitioner) | Who set the goal |
| `note` | Annotation[] | Comments about the goal |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `lifecycle-status` | token | Lifecycle status | `lifecycle-status=active` |
| `achievement-status` | token | Achievement status | `achievement-status=in-progress` |
| `category` | token | Category | `category=dietary` |
| `start-date` | date | Start date | `start-date=ge2024-01-01` |
| `target-date` | date | Target due date | `target-date=le2024-12-31` |

## Examples

### Create a Goal

```bash
curl -X POST http://localhost:8080/baseR4/Goal \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Goal",
    "lifecycleStatus": "active",
    "achievementStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/goal-achievement",
        "code": "in-progress",
        "display": "In Progress"
      }]
    },
    "priority": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/goal-priority",
        "code": "high-priority",
        "display": "High Priority"
      }]
    },
    "description": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "289169006",
        "display": "Weight loss"
      }],
      "text": "Weight loss"
    },
    "subject": {"reference": "Patient/patient-001"},
    "startDate": "2024-01-01",
    "target": [{
      "measure": {
        "coding": [{
          "system": "http://snomed.info/sct",
          "code": "27113001",
          "display": "Body weight"
        }]
      },
      "detailQuantity": {
        "value": 75,
        "unit": "kg",
        "system": "http://unitsofmeasure.org",
        "code": "kg"
      },
      "dueDate": "2024-06-01"
    }]
  }'
```

### Search Goals

```bash
# By patient
curl "http://localhost:8080/baseR4/Goal?patient=Patient/123"

# Active goals
curl "http://localhost:8080/baseR4/Goal?lifecycle-status=active"

# By achievement status
curl "http://localhost:8080/baseR4/Goal?achievement-status=achieved"

# Combined
curl "http://localhost:8080/baseR4/Goal?patient=Patient/123&lifecycle-status=active"
```

## Generator

The `GoalGenerator` creates synthetic Goal resources with:

- SNOMED CT goal descriptions
- HL7 achievement status codes
- Goal priority levels
- Quantitative targets with measures and due dates

### Usage

```python
from fhirkit.server.generator import GoalGenerator

generator = GoalGenerator(seed=42)

goal = generator.generate(
    patient_ref="Patient/123",
    expressed_by_ref="Practitioner/456"
)
```

## Clinical Codes

### Goal Descriptions (SNOMED CT)

| Code | Display |
|------|---------|
| 289169006 | Weight loss |
| 135840009 | Blood pressure control |
| 698472009 | Blood glucose control |
| 229065009 | Regular exercise |
| 225323000 | Smoking cessation |
| 226029000 | Healthy diet |
| 392039005 | Medication adherence |

### Achievement Status

| Code | Display |
|------|---------|
| in-progress | In Progress |
| improving | Improving |
| worsening | Worsening |
| achieved | Achieved |
| sustaining | Sustaining |
| not-achieved | Not Achieved |
