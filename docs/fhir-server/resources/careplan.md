# CarePlan

## Overview

The CarePlan resource represents a care coordination document that describes the intention of how one or more practitioners intend to deliver care for a patient. It includes planned activities, goals, and the healthcare team involved in the patient's care.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/careplan.html](https://hl7.org/fhir/R4/careplan.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | draft, active, on-hold, revoked, completed, entered-in-error, unknown |
| `intent` | code | proposal, plan, order, option |
| `category` | CodeableConcept[] | Type of plan (US Core: assess-plan) |
| `title` | string | Human-friendly name for the plan |
| `description` | string | Summary of nature of plan |
| `subject` | Reference(Patient) | Who the care plan is for |
| `encounter` | Reference(Encounter) | Created in context of |
| `period` | Period | Time period plan covers |
| `created` | dateTime | Date record was first created |
| `author` | Reference(Practitioner) | Who created the plan |
| `addresses` | Reference(Condition)[] | Health issues this plan addresses |
| `activity` | BackboneElement[] | Action to occur as part of plan |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `status` | token | Status | `status=active` |
| `intent` | token | Intent | `intent=plan` |
| `category` | token | Category | `category=assess-plan` |
| `date` | date | Period start | `date=ge2024-01-01` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/456` |
| `condition` | reference | Condition addressed | `condition=Condition/789` |

## Examples

### Create a CarePlan

```bash
curl -X POST http://localhost:8080/baseR4/CarePlan \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CarePlan",
    "status": "active",
    "intent": "plan",
    "category": [{
      "coding": [{
        "system": "http://hl7.org/fhir/us/core/CodeSystem/careplan-category",
        "code": "assess-plan",
        "display": "Assessment and Plan of Treatment"
      }]
    }],
    "title": "Diabetes Management Plan",
    "description": "Comprehensive care plan for diabetes management",
    "subject": {"reference": "Patient/patient-001"},
    "period": {"start": "2024-01-01"},
    "activity": [{
      "detail": {
        "status": "in-progress",
        "code": {
          "coding": [{
            "system": "http://snomed.info/sct",
            "code": "698358001",
            "display": "Blood glucose monitoring"
          }]
        }
      }
    }]
  }'
```

### Search CarePlans

```bash
# By patient
curl "http://localhost:8080/baseR4/CarePlan?patient=Patient/123"

# Active care plans
curl "http://localhost:8080/baseR4/CarePlan?status=active"

# By category
curl "http://localhost:8080/baseR4/CarePlan?category=assess-plan"

# Combined
curl "http://localhost:8080/baseR4/CarePlan?patient=Patient/123&status=active"
```

## Generator

The `CarePlanGenerator` creates synthetic CarePlan resources with:

- US Core category codes
- SNOMED CT activity codes for interventions
- Realistic care plan titles and descriptions
- Multiple activities per care plan (2-5)

### Usage

```python
from fhir_cql.server.generator import CarePlanGenerator

generator = CarePlanGenerator(seed=42)

careplan = generator.generate(
    patient_ref="Patient/123",
    encounter_ref="Encounter/456",
    author_ref="Practitioner/789",
    condition_refs=["Condition/cond-1"]
)
```

## Clinical Codes

### Activities (SNOMED CT)

| Code | Display |
|------|---------|
| 698358001 | Blood glucose monitoring |
| 226029000 | Dietary modification |
| 229065009 | Exercise therapy |
| 710081004 | Medication therapy management |
| 229070002 | Physical therapy |
| 225323000 | Smoking cessation therapy |
| 429159005 | Weight management |
