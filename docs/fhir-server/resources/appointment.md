# Appointment

## Overview

The Appointment resource represents a scheduled event for a patient with healthcare providers. Appointments are used to book time slots for patient visits, procedures, and other healthcare activities.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/appointment.html](https://hl7.org/fhir/R4/appointment.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | proposed, pending, booked, arrived, fulfilled, cancelled, noshow, entered-in-error, checked-in, waitlist |
| `cancelationReason` | CodeableConcept | Why cancelled |
| `serviceCategory` | CodeableConcept[] | Service category |
| `serviceType` | CodeableConcept[] | Type of service |
| `specialty` | CodeableConcept[] | Medical specialty |
| `appointmentType` | CodeableConcept | Type of appointment |
| `reasonCode` | CodeableConcept[] | Reason for appointment |
| `reasonReference` | Reference[] | Condition/Procedure justification |
| `priority` | unsignedInt | Priority (0-9) |
| `description` | string | Appointment description |
| `supportingInformation` | Reference[] | Additional information |
| `start` | instant | Start time |
| `end` | instant | End time |
| `minutesDuration` | positiveInt | Duration in minutes |
| `slot` | Reference(Slot)[] | Slots used |
| `created` | dateTime | When created |
| `comment` | string | Comments |
| `patientInstruction` | string | Instructions for patient |
| `basedOn` | Reference(ServiceRequest)[] | Based on order |
| `participant` | BackboneElement[] | Participants |
| `requestedPeriod` | Period[] | Requested time periods |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=apt-001` |
| `identifier` | token | Business identifier | `identifier=APT-12345` |
| `patient` | reference | Patient participant | `patient=Patient/123` |
| `actor` | reference | Any participant | `actor=Practitioner/456` |
| `status` | token | Appointment status | `status=booked` |
| `date` | date | Appointment date | `date=2024-01-15` |
| `start` | date | Start time | `start=ge2024-01-15` |
| `end` | date | End time | `end=le2024-01-15` |
| `service-category` | token | Service category | `service-category=17` |
| `service-type` | token | Service type | `service-type=124` |
| `specialty` | token | Specialty | `specialty=394814009` |
| `appointment-type` | token | Appointment type | `appointment-type=ROUTINE` |
| `reason-code` | token | Reason code | `reason-code=185389009` |
| `slot` | reference | Slot used | `slot=Slot/123` |
| `location` | reference | Location | `location=Location/456` |
| `practitioner` | reference | Practitioner | `practitioner=Practitioner/789` |

## Examples

### Create an Appointment

```bash
curl -X POST http://localhost:8080/baseR4/Appointment \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Appointment",
    "status": "booked",
    "serviceCategory": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/service-category",
        "code": "17",
        "display": "General Practice"
      }]
    }],
    "appointmentType": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
        "code": "FOLLOWUP",
        "display": "Follow-up visit"
      }]
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "185389009",
        "display": "Follow-up visit"
      }]
    }],
    "priority": 5,
    "description": "Follow-up appointment for diabetes management",
    "start": "2024-01-15T09:00:00Z",
    "end": "2024-01-15T09:30:00Z",
    "minutesDuration": 30,
    "created": "2024-01-10T14:30:00Z",
    "patientInstruction": "Please bring your blood pressure log",
    "participant": [
      {
        "actor": {
          "reference": "Patient/patient-001",
          "display": "John Smith"
        },
        "required": "required",
        "status": "accepted"
      },
      {
        "actor": {
          "reference": "Practitioner/practitioner-001",
          "display": "Dr. Jane Smith"
        },
        "required": "required",
        "status": "accepted"
      },
      {
        "actor": {
          "reference": "Location/location-001",
          "display": "Main Clinic"
        },
        "required": "required",
        "status": "accepted"
      }
    ]
  }'
```

### Search Appointments

```bash
# By patient
curl "http://localhost:8080/baseR4/Appointment?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Appointment?status=booked"

# By date
curl "http://localhost:8080/baseR4/Appointment?date=2024-01-15"

# By practitioner
curl "http://localhost:8080/baseR4/Appointment?practitioner=Practitioner/456"

# Upcoming appointments
curl "http://localhost:8080/baseR4/Appointment?date=ge2024-01-15&status=booked"
```

### Patient Compartment

```bash
# Get all appointments for a patient
curl "http://localhost:8080/baseR4/Patient/123/Appointment"

# Booked appointments only
curl "http://localhost:8080/baseR4/Patient/123/Appointment?status=booked"
```

## Status Codes

| Code | Display | Description |
|------|---------|-------------|
| proposed | Proposed | Tentative, not confirmed |
| pending | Pending | Awaiting confirmation |
| booked | Booked | Confirmed |
| arrived | Arrived | Patient has arrived |
| fulfilled | Fulfilled | Completed |
| cancelled | Cancelled | Was cancelled |
| noshow | No Show | Patient did not show |
| entered-in-error | Entered in Error | Data entry error |
| checked-in | Checked In | Patient checked in |
| waitlist | Waitlist | On waiting list |

## Appointment Types (v2-0276)

| Code | Display |
|------|---------|
| CHECKUP | Checkup |
| EMERGENCY | Emergency |
| FOLLOWUP | Follow-up |
| ROUTINE | Routine |
| WALKIN | Walk-in |
