# Group

## Overview

The Group resource represents a defined group of entities, typically patients. Groups can be used for CQL measure evaluation, research cohorts, care teams, or any collection of related resources.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/group.html](https://hl7.org/fhir/R4/group.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `active` | boolean | Whether group is active |
| `type` | code | person, animal, practitioner, device, medication, substance |
| `actual` | boolean | Actual vs definitional |
| `code` | CodeableConcept | Kind of group members |
| `name` | string | Label for group |
| `quantity` | unsignedInt | Number of members |
| `managingEntity` | Reference | Entity managing the group |
| `characteristic` | BackboneElement[] | Inclusion/exclusion criteria |
| `member` | BackboneElement[] | Members of the group |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=group-001` |
| `identifier` | token | Business identifier | `identifier=GRP-12345` |
| `type` | token | Group type | `type=person` |
| `actual` | token | Actual vs definitional | `actual=true` |
| `code` | token | Kind of members | `code=diabetes-cohort` |
| `name` | string | Group name | `name=Diabetes Patients` |
| `managing-entity` | reference | Managing organization | `managing-entity=Organization/123` |
| `member` | reference | Group member | `member=Patient/456` |
| `characteristic` | composite | Characteristic criteria | `characteristic=gender$female` |
| `characteristic-value` | token | Characteristic value | `characteristic-value=female` |
| `exclude` | token | Exclusion criteria | `exclude=false` |

## Examples

### Create a Group

```bash
curl -X POST http://localhost:8080/baseR4/Group \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Group",
    "active": true,
    "type": "person",
    "actual": true,
    "code": {
      "coding": [{
        "system": "http://example.org/group-types",
        "code": "diabetes-cohort",
        "display": "Diabetes Patient Cohort"
      }]
    },
    "name": "Type 2 Diabetes Patients",
    "quantity": 150,
    "managingEntity": {
      "reference": "Organization/organization-001"
    },
    "characteristic": [{
      "code": {
        "coding": [{
          "system": "http://snomed.info/sct",
          "code": "44054006",
          "display": "Diabetes mellitus type 2"
        }]
      },
      "valueBoolean": true,
      "exclude": false
    }],
    "member": [
      {
        "entity": {"reference": "Patient/patient-001"},
        "period": {"start": "2024-01-01"}
      },
      {
        "entity": {"reference": "Patient/patient-002"},
        "period": {"start": "2024-01-01"}
      }
    ]
  }'
```

### Create a Definitional Group

```bash
curl -X POST http://localhost:8080/baseR4/Group \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Group",
    "active": true,
    "type": "person",
    "actual": false,
    "name": "Adults Over 65",
    "characteristic": [
      {
        "code": {
          "coding": [{
            "system": "http://hl7.org/fhir/administrative-gender",
            "code": "age"
          }]
        },
        "valueRange": {
          "low": {"value": 65, "unit": "years"}
        },
        "exclude": false
      }
    ]
  }'
```

### Search Groups

```bash
# By type
curl "http://localhost:8080/baseR4/Group?type=person"

# By name
curl "http://localhost:8080/baseR4/Group?name=Diabetes"

# Actual groups only
curl "http://localhost:8080/baseR4/Group?actual=true"

# By member
curl "http://localhost:8080/baseR4/Group?member=Patient/123"

# By managing entity
curl "http://localhost:8080/baseR4/Group?managing-entity=Organization/456"
```

## Group Types

| Code | Display | Description |
|------|---------|-------------|
| person | Person | Group of people (patients) |
| animal | Animal | Group of animals |
| practitioner | Practitioner | Group of practitioners |
| device | Device | Group of devices |
| medication | Medication | Group of medications |
| substance | Substance | Group of substances |

## Use Cases

### CQL Measure Evaluation

Groups are commonly used to define patient populations for CQL measure evaluation:

```json
{
  "resourceType": "MeasureReport",
  "measure": "Measure/diabetes-control",
  "subject": {
    "reference": "Group/diabetes-cohort"
  }
}
```

### Research Cohorts

Define inclusion/exclusion criteria for research studies:

```json
{
  "characteristic": [
    {
      "code": {"text": "Age"},
      "valueRange": {"low": {"value": 18}, "high": {"value": 65}},
      "exclude": false
    },
    {
      "code": {"text": "Pregnancy"},
      "valueBoolean": true,
      "exclude": true
    }
  ]
}
```
