# ServiceRequest

## Overview

The ServiceRequest resource represents a request for a service to be performed. This includes diagnostic investigations, treatments, and other clinical interventions such as laboratory tests, imaging studies, referrals, and procedures.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/servicerequest.html](https://hl7.org/fhir/R4/servicerequest.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | draft, active, on-hold, revoked, completed, entered-in-error, unknown |
| `intent` | code | proposal, plan, directive, order, original-order, reflex-order, etc. |
| `priority` | code | routine, urgent, asap, stat |
| `category` | CodeableConcept[] | Classification of service (laboratory, imaging, etc.) |
| `code` | CodeableConcept | What is being requested (SNOMED CT) |
| `subject` | Reference(Patient) | Who the request is for |
| `encounter` | Reference(Encounter) | Encounter in context of |
| `authoredOn` | dateTime | When the request was created |
| `requester` | Reference(Practitioner) | Who is ordering |
| `performer` | Reference(Practitioner)[] | Who should perform |
| `reasonCode` | CodeableConcept[] | Why the service is requested |
| `note` | Annotation[] | Additional notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Service code | `code=http://snomed.info/sct\|26604007` |
| `category` | token | Category | `category=laboratory` |
| `status` | token | Status | `status=active` |
| `intent` | token | Intent | `intent=order` |
| `priority` | token | Priority | `priority=stat` |
| `authored` | date | Authored date | `authored=2024-06-15` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/456` |
| `requester` | reference | Requester reference | `requester=Practitioner/789` |
| `performer` | reference | Performer reference | `performer=Practitioner/789` |

## Examples

### Create a ServiceRequest

```bash
curl -X POST http://localhost:8080/baseR4/ServiceRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ServiceRequest",
    "status": "active",
    "intent": "order",
    "priority": "routine",
    "category": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "108252007",
        "display": "Laboratory procedure"
      }]
    }],
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "26604007",
        "display": "Complete blood count"
      }],
      "text": "Complete blood count"
    },
    "subject": {"reference": "Patient/patient-001"},
    "authoredOn": "2024-06-15T10:30:00Z",
    "requester": {"reference": "Practitioner/practitioner-001"}
  }'
```

### Search ServiceRequests

```bash
# By patient
curl "http://localhost:8080/baseR4/ServiceRequest?patient=Patient/123"

# By category (laboratory orders)
curl "http://localhost:8080/baseR4/ServiceRequest?category=laboratory"

# Active orders
curl "http://localhost:8080/baseR4/ServiceRequest?status=active"

# STAT orders
curl "http://localhost:8080/baseR4/ServiceRequest?priority=stat"

# Combined
curl "http://localhost:8080/baseR4/ServiceRequest?patient=Patient/123&status=active&intent=order"
```

## Generator

The `ServiceRequestGenerator` creates synthetic ServiceRequest resources with:

- SNOMED CT order codes for lab, imaging, and referrals
- Weighted priority distributions (70% routine)
- Status and intent codes
- Reason codes and clinical notes

### Usage

```python
from fhirkit.server.generator import ServiceRequestGenerator

generator = ServiceRequestGenerator(seed=42)

# Generate any service request
request = generator.generate(
    patient_ref="Patient/123",
    requester_ref="Practitioner/456"
)

# Generate specific types
lab_order = generator.generate_lab_order(patient_ref="Patient/123")
imaging_order = generator.generate_imaging_order(patient_ref="Patient/123")
referral = generator.generate_referral(patient_ref="Patient/123")
```

## Clinical Codes

### Order Codes (SNOMED CT)

| Code | Display | Category |
|------|---------|----------|
| 26604007 | Complete blood count | laboratory |
| 166312007 | Blood chemistry | laboratory |
| 43396009 | Hemoglobin A1c | laboratory |
| 77477000 | CT scan | imaging |
| 113091000 | MRI | imaging |
| 168537006 | X-ray | imaging |
| 3457005 | Patient referral | referral |
| 229070002 | Physical therapy | rehabilitation |

### Priority Codes

| Code | Description |
|------|-------------|
| routine | Routine - standard processing |
| urgent | Within 24 hours |
| asap | As soon as possible |
| stat | Immediately - emergency |
