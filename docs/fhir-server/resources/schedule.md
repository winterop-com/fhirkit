# Schedule

## Overview

The Schedule resource represents a container for Slot resources, defining the availability of a practitioner, location, or other resource for booking appointments.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/schedule.html](https://hl7.org/fhir/R4/schedule.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `active` | boolean | Whether schedule is active |
| `serviceCategory` | CodeableConcept[] | Service category |
| `serviceType` | CodeableConcept[] | Type of service |
| `specialty` | CodeableConcept[] | Medical specialty |
| `actor` | Reference[] | Resource(s) this schedule applies to |
| `planningHorizon` | Period | Planning time period |
| `comment` | string | Comments |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=sch-001` |
| `identifier` | token | Business identifier | `identifier=SCH-12345` |
| `actor` | reference | Actor reference | `actor=Practitioner/123` |
| `active` | token | Active status | `active=true` |
| `date` | date | Planning horizon date | `date=ge2024-01-01` |
| `service-category` | token | Service category | `service-category=17` |
| `service-type` | token | Service type | `service-type=124` |
| `specialty` | token | Specialty | `specialty=394814009` |

## Examples

### Create a Schedule

```bash
curl -X POST http://localhost:8080/baseR4/Schedule \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Schedule",
    "active": true,
    "serviceCategory": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/service-category",
        "code": "17",
        "display": "General Practice"
      }]
    }],
    "serviceType": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/service-type",
        "code": "124",
        "display": "General Practice"
      }]
    }],
    "specialty": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "394814009",
        "display": "General practice"
      }]
    }],
    "actor": [
      {
        "reference": "Practitioner/practitioner-001",
        "display": "Dr. Jane Smith"
      },
      {
        "reference": "Location/location-001",
        "display": "Main Clinic"
      }
    ],
    "planningHorizon": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "comment": "Regular clinic schedule for Dr. Smith"
  }'
```

### Search Schedules

```bash
# By actor
curl "http://localhost:8080/baseR4/Schedule?actor=Practitioner/123"

# Active schedules
curl "http://localhost:8080/baseR4/Schedule?active=true"

# By specialty
curl "http://localhost:8080/baseR4/Schedule?specialty=394814009"

# By date range
curl "http://localhost:8080/baseR4/Schedule?date=ge2024-01-01"
```

### With _revinclude

```bash
# Include slots
curl "http://localhost:8080/baseR4/Schedule?_revinclude=Slot:schedule"
```
