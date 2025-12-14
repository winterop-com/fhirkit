# Slot

## Overview

The Slot resource represents a time slot within a Schedule that can be booked for an appointment. Slots define the availability of a resource for booking.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/slot.html](https://hl7.org/fhir/R4/slot.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `serviceCategory` | CodeableConcept[] | Service category |
| `serviceType` | CodeableConcept[] | Type of service |
| `specialty` | CodeableConcept[] | Medical specialty |
| `appointmentType` | CodeableConcept | Type of appointment |
| `schedule` | Reference(Schedule) | Parent schedule |
| `status` | code | busy, free, busy-unavailable, busy-tentative, entered-in-error |
| `start` | instant | Start time |
| `end` | instant | End time |
| `overbooked` | boolean | Allow overbooking |
| `comment` | string | Comments |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=slot-001` |
| `identifier` | token | Business identifier | `identifier=SLOT-12345` |
| `schedule` | reference | Parent schedule | `schedule=Schedule/123` |
| `status` | token | Slot status | `status=free` |
| `start` | date | Start time | `start=2024-01-15` |
| `end` | date | End time | `end=le2024-01-15` |
| `service-category` | token | Service category | `service-category=17` |
| `service-type` | token | Service type | `service-type=124` |
| `specialty` | token | Specialty | `specialty=394814009` |
| `appointment-type` | token | Appointment type | `appointment-type=ROUTINE` |

## Examples

### Create a Slot

```bash
curl -X POST http://localhost:8080/baseR4/Slot \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Slot",
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
    "appointmentType": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
        "code": "ROUTINE",
        "display": "Routine appointment"
      }]
    },
    "schedule": {
      "reference": "Schedule/schedule-001"
    },
    "status": "free",
    "start": "2024-01-15T09:00:00Z",
    "end": "2024-01-15T09:30:00Z",
    "overbooked": false,
    "comment": "30-minute appointment slot"
  }'
```

### Search Slots

```bash
# By schedule
curl "http://localhost:8080/baseR4/Slot?schedule=Schedule/123"

# Free slots
curl "http://localhost:8080/baseR4/Slot?status=free"

# By date
curl "http://localhost:8080/baseR4/Slot?start=2024-01-15"

# Free slots for a date
curl "http://localhost:8080/baseR4/Slot?status=free&start=2024-01-15"
```

### With _include

```bash
# Include schedule
curl "http://localhost:8080/baseR4/Slot?_include=Slot:schedule"
```

## Status Codes

| Code | Display | Description |
|------|---------|-------------|
| busy | Busy | Slot is booked |
| free | Free | Available for booking |
| busy-unavailable | Busy (Unavailable) | Unavailable for booking |
| busy-tentative | Busy (Tentative) | Tentatively booked |
| entered-in-error | Entered in Error | Data entry error |
