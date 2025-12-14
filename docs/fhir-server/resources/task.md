# Task

## Overview

The Task resource describes an activity to be performed. Tasks are used for workflow management, tracking work items, and coordinating clinical activities.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/task.html](https://hl7.org/fhir/R4/task.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `basedOn` | Reference(ServiceRequest)[] | Based on request |
| `groupIdentifier` | Identifier | Group identifier |
| `partOf` | Reference(Task)[] | Parent task |
| `status` | code | draft, requested, received, accepted, rejected, ready, cancelled, in-progress, on-hold, failed, completed, entered-in-error |
| `statusReason` | CodeableConcept | Why current status |
| `businessStatus` | CodeableConcept | Business status |
| `intent` | code | unknown, proposal, plan, order, etc. |
| `priority` | code | routine, urgent, asap, stat |
| `code` | CodeableConcept | Task type |
| `description` | string | Task description |
| `focus` | Reference | What task is about |
| `for` | Reference(Patient) | Beneficiary |
| `encounter` | Reference(Encounter) | Encounter context |
| `executionPeriod` | Period | Execution time period |
| `authoredOn` | dateTime | When created |
| `lastModified` | dateTime | Last modified |
| `requester` | Reference | Who requested |
| `owner` | Reference | Responsible party |
| `reasonCode` | CodeableConcept | Why task exists |
| `note` | Annotation[] | Comments |
| `restriction` | BackboneElement | Constraints |
| `input` | BackboneElement[] | Task inputs |
| `output` | BackboneElement[] | Task outputs |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=task-001` |
| `identifier` | token | Business identifier | `identifier=TASK-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `status` | token | Task status | `status=in-progress` |
| `intent` | token | Task intent | `intent=order` |
| `code` | token | Task type | `code=fulfill` |
| `owner` | reference | Task owner | `owner=Practitioner/456` |
| `requester` | reference | Requester | `requester=Practitioner/789` |
| `focus` | reference | Focus resource | `focus=ServiceRequest/123` |
| `based-on` | reference | Based on | `based-on=ServiceRequest/456` |
| `encounter` | reference | Encounter | `encounter=Encounter/789` |
| `priority` | token | Priority | `priority=urgent` |
| `authored-on` | date | Created date | `authored-on=2024-01-15` |
| `modified` | date | Modified date | `modified=ge2024-01-15` |
| `period` | date | Execution period | `period=ge2024-01-15` |
| `business-status` | token | Business status | `business-status=awaiting-results` |

## Examples

### Create a Task

```bash
curl -X POST http://localhost:8080/baseR4/Task \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Task",
    "status": "requested",
    "intent": "order",
    "priority": "routine",
    "code": {
      "coding": [{
        "system": "http://hl7.org/fhir/CodeSystem/task-code",
        "code": "fulfill",
        "display": "Fulfill the focal request"
      }]
    },
    "description": "Complete lab work order for diabetes follow-up",
    "focus": {
      "reference": "ServiceRequest/service-request-001"
    },
    "for": {
      "reference": "Patient/patient-001",
      "display": "John Smith"
    },
    "authoredOn": "2024-01-15T10:00:00Z",
    "requester": {
      "reference": "Practitioner/practitioner-001",
      "display": "Dr. Jane Smith"
    },
    "owner": {
      "reference": "Organization/lab-001",
      "display": "Hospital Laboratory"
    },
    "restriction": {
      "repetitions": 1,
      "period": {
        "start": "2024-01-15",
        "end": "2024-01-22"
      }
    }
  }'
```

### Search Tasks

```bash
# By patient
curl "http://localhost:8080/baseR4/Task?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Task?status=in-progress"

# By owner
curl "http://localhost:8080/baseR4/Task?owner=Practitioner/456"

# Urgent tasks
curl "http://localhost:8080/baseR4/Task?priority=urgent"

# Combined: patient's pending tasks
curl "http://localhost:8080/baseR4/Task?patient=Patient/123&status=requested,in-progress"
```

### Patient Compartment

```bash
# Get all tasks for a patient
curl "http://localhost:8080/baseR4/Patient/123/Task"
```

## Status Codes

| Code | Display | Description |
|------|---------|-------------|
| draft | Draft | Initial state |
| requested | Requested | Ready to be acted on |
| received | Received | Owner has acknowledged |
| accepted | Accepted | Owner has agreed to perform |
| rejected | Rejected | Owner declined |
| ready | Ready | Ready to be performed |
| cancelled | Cancelled | No longer needed |
| in-progress | In Progress | Currently being performed |
| on-hold | On Hold | Temporarily suspended |
| failed | Failed | Could not complete |
| completed | Completed | Successfully finished |
| entered-in-error | Entered in Error | Data entry error |

## Intent Codes

| Code | Display |
|------|---------|
| unknown | Unknown |
| proposal | Proposal |
| plan | Plan |
| order | Order |
| original-order | Original Order |
| reflex-order | Reflex Order |
| filler-order | Filler Order |
| instance-order | Instance Order |
| option | Option |

## Task Codes

| Code | Display |
|------|---------|
| approve | Activate/Approve |
| fulfill | Fulfill |
| abort | Mark as Error |
| replace | Replace |
| change | Change |
| suspend | Suspend |
| resume | Resume |
