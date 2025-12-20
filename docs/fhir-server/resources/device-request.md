# DeviceRequest

## Overview

A DeviceRequest represents a request for the use of a medical device for a patient. This includes requests for durable medical equipment (DME), implantable devices, diagnostic devices, and therapeutic devices.

The resource is used when a provider orders a device for a patient, whether for home use, implantation, or use during an encounter. It captures the requested device, the patient, priority, and relevant clinical context.

**Common use cases:**
- Ordering durable medical equipment (wheelchairs, oxygen concentrators)
- Requesting implantable devices (pacemakers, cochlear implants)
- Ordering home monitoring devices (blood pressure monitors, glucose meters)
- Requesting therapeutic devices (CPAP machines)
- Hospital equipment requests (hospital beds, infusion pumps)

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/devicerequest.html](https://hl7.org/fhir/R4/devicerequest.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | draft, active, on-hold, revoked, completed, entered-in-error, unknown |
| `intent` | code | proposal, plan, directive, order, original-order, reflex-order, filler-order, instance-order, option |
| `priority` | code | routine, urgent, asap, stat |
| `codeCodeableConcept` | CodeableConcept | Device type code |
| `codeReference` | Reference(Device) | Reference to specific Device |
| `subject` | Reference(Patient) | Patient who will use the device |
| `encounter` | Reference(Encounter) | Encounter context |
| `occurrenceDateTime` | dateTime | When device is needed |
| `occurrencePeriod` | Period | Period when device is needed |
| `authoredOn` | dateTime | When request was created |
| `requester` | Reference(Practitioner) | Who made the request |
| `performer` | Reference(Practitioner|Organization) | Who will fulfill |
| `reasonCode` | CodeableConcept[] | Reason for the request |
| `reasonReference` | Reference(Condition)[] | Condition justifying request |
| `note` | Annotation[] | Additional notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=request-001` |
| `identifier` | token | Business identifier | `identifier=DME-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference (alias) | `subject=Patient/123` |
| `status` | token | Request status | `status=active` |
| `intent` | token | Request intent | `intent=order` |
| `code` | token | Device code | `code=14106009` |
| `authored-on` | date | When authored | `authored-on=2024-01-15` |
| `requester` | reference | Requester reference | `requester=Practitioner/456` |
| `performer` | reference | Performer reference | `performer=Organization/789` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/enc-001` |
| `event-date` | date | Occurrence date | `event-date=gt2024-01-01` |
| `device` | reference | Device reference | `device=Device/dev-001` |
| `group-identifier` | token | Group identifier | `group-identifier=batch-001` |

## Examples

### Create a DeviceRequest

```bash
curl -X POST http://localhost:8080/baseR4/DeviceRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "DeviceRequest",
    "identifier": [{
      "system": "http://hospital.example.org/dme-orders",
      "value": "DME-2024-001"
    }],
    "status": "active",
    "intent": "order",
    "priority": "routine",
    "codeCodeableConcept": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "702172008",
        "display": "Home blood pressure monitor"
      }],
      "text": "Home blood pressure monitor"
    },
    "subject": {
      "reference": "Patient/123",
      "display": "John Smith"
    },
    "authoredOn": "2024-01-15T10:30:00Z",
    "requester": {
      "reference": "Practitioner/456",
      "display": "Dr. Jane Doe"
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "38341003",
        "display": "Hypertensive disorder"
      }]
    }],
    "occurrenceDateTime": "2024-01-20"
  }'
```

### Search DeviceRequests

```bash
# By patient
curl "http://localhost:8080/baseR4/DeviceRequest?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/DeviceRequest?status=active"

# By device code
curl "http://localhost:8080/baseR4/DeviceRequest?code=702172008"

# By intent
curl "http://localhost:8080/baseR4/DeviceRequest?intent=order"

# By requester
curl "http://localhost:8080/baseR4/DeviceRequest?requester=Practitioner/456"

# Combined: active orders for a patient
curl "http://localhost:8080/baseR4/DeviceRequest?patient=Patient/123&status=active&intent=order"

# By date range
curl "http://localhost:8080/baseR4/DeviceRequest?authored-on=ge2024-01-01&authored-on=le2024-12-31"
```

### Read a DeviceRequest

```bash
curl "http://localhost:8080/baseR4/DeviceRequest/request-001"
```

### Update a DeviceRequest

```bash
curl -X PUT http://localhost:8080/baseR4/DeviceRequest/request-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "DeviceRequest",
    "id": "request-001",
    "status": "completed",
    ...
  }'
```

### Delete a DeviceRequest

```bash
curl -X DELETE "http://localhost:8080/baseR4/DeviceRequest/request-001"
```

## Generator Usage

The `DeviceRequestGenerator` creates synthetic DeviceRequest resources with realistic device types and clinical contexts.

```python
from fhirkit.server.generator import DeviceRequestGenerator

generator = DeviceRequestGenerator(seed=42)

# Generate a random device request
request = generator.generate()

# Generate with specific status and intent
order = generator.generate(
    status="active",
    intent="order",
    priority="urgent"
)

# Generate request for a specific patient
patient_request = generator.generate_for_patient(
    patient_id="patient-123",
    device_code={
        "system": "http://snomed.info/sct",
        "code": "702172008",
        "display": "Home blood pressure monitor"
    },
    requester_id="practitioner-456"
)

# Generate with specific device type
pacemaker_request = generator.generate(
    device_code={
        "system": "http://snomed.info/sct",
        "code": "14106009",
        "display": "Cardiac pacemaker"
    },
    subject_reference="Patient/123",
    priority="stat"
)

# Generate batch
requests = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| draft | Request is not yet active |
| active | Request is active and valid |
| on-hold | Request is temporarily suspended |
| revoked | Request has been cancelled |
| completed | Request has been fulfilled |
| entered-in-error | Request was entered in error |
| unknown | Status is unknown |

## Intent Codes

| Code | Description |
|------|-------------|
| proposal | A suggestion |
| plan | An intended action |
| directive | A directive to perform |
| order | An authoritative instruction |
| original-order | Original order from which others derive |
| reflex-order | Order triggered by another order |
| filler-order | Order created by fulfiller |
| instance-order | Instance of an order |
| option | An optional action |

## Common Device Types

| SNOMED CT Code | Display |
|----------------|---------|
| 14106009 | Cardiac pacemaker |
| 43252007 | Cochlear implant |
| 303619003 | Continuous positive airway pressure unit (CPAP) |
| 702172008 | Home blood pressure monitor |
| 469591008 | Hospital bed |
| 23562009 | Glucose meter |
| 37874008 | Oxygen concentrator |
| 261956002 | Wheelchair |

## Related Resources

- [Device](./device.md) - The actual device being requested
- [DeviceDefinition](./device-definition.md) - Definition of the device type
- [Patient](./patient.md) - Patient who will use the device
- [Encounter](./encounter.md) - Encounter context for the request
- [Practitioner](./practitioner.md) - Requester of the device
