# GuidanceResponse

## Overview

A GuidanceResponse represents the response to a clinical decision support (CDS) request. It contains the results of evaluating a knowledge artifact such as a CDS rule, clinical protocol, or order set against a specific patient context.

The resource captures the outcome of invoking a guidance module, including any recommendations, warnings, or required data requests. It serves as the mechanism for CDS services to communicate their findings back to requesting systems.

**Common use cases:**
- Drug-drug interaction alerts
- Clinical protocol recommendations
- Order set suggestions
- Contraindication warnings
- Dosage verification responses

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/guidanceresponse.html](https://hl7.org/fhir/R4/guidanceresponse.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `requestIdentifier` | Identifier | Identifier of the originating request |
| `moduleUri` | uri | URI of the guidance module |
| `moduleCanonical` | canonical | Canonical reference to Library or PlanDefinition |
| `moduleCodeableConcept` | CodeableConcept | Code representing the guidance module |
| `status` | code | success, data-requested, data-required, in-progress, failure, entered-in-error |
| `subject` | Reference(Patient) | Patient the guidance is for |
| `encounter` | Reference(Encounter) | Encounter context |
| `occurrenceDateTime` | dateTime | When guidance was invoked |
| `performer` | Reference(Device) | Device performing the evaluation |
| `reasonCode` | CodeableConcept[] | Reason codes for the guidance |
| `note` | Annotation[] | Additional notes |
| `outputParameters` | Reference(Parameters) | Output parameters |
| `result` | Reference(CarePlan|RequestGroup) | Resulting actions |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=response-001` |
| `identifier` | token | Business identifier | `identifier=req-12345` |
| `request` | token | Request identifier | `request=cds-request-001` |
| `subject` | reference | Patient reference | `subject=Patient/123` |
| `patient` | reference | Patient reference (alias) | `patient=Patient/123` |
| `status` | token | Response status | `status=success` |

## Examples

### Create a GuidanceResponse

```bash
curl -X POST http://localhost:8080/baseR4/GuidanceResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "GuidanceResponse",
    "requestIdentifier": {
      "system": "http://example.org/request-ids",
      "value": "cds-request-001"
    },
    "moduleUri": "http://example.org/guidance/drug-interaction-check",
    "status": "success",
    "subject": {
      "reference": "Patient/123"
    },
    "occurrenceDateTime": "2024-01-15T10:30:00Z",
    "performer": {
      "reference": "Device/cds-engine-001",
      "display": "CDS Decision Engine"
    },
    "reasonCode": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
        "code": "drug-drug-interaction",
        "display": "Drug-Drug Interaction"
      }],
      "text": "Potential interaction between warfarin and aspirin"
    }],
    "result": {
      "reference": "RequestGroup/recommendations-001"
    }
  }'
```

### Search GuidanceResponses

```bash
# By patient
curl "http://localhost:8080/baseR4/GuidanceResponse?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/GuidanceResponse?status=success"

# By request identifier
curl "http://localhost:8080/baseR4/GuidanceResponse?request=cds-request-001"

# Combined: successful responses for a patient
curl "http://localhost:8080/baseR4/GuidanceResponse?patient=Patient/123&status=success"
```

### Read a GuidanceResponse

```bash
curl "http://localhost:8080/baseR4/GuidanceResponse/response-001"
```

### Delete a GuidanceResponse

```bash
curl -X DELETE "http://localhost:8080/baseR4/GuidanceResponse/response-001"
```

## Generator Usage

The `GuidanceResponseGenerator` creates synthetic GuidanceResponse resources simulating CDS system responses.

```python
from fhirkit.server.generator import GuidanceResponseGenerator

generator = GuidanceResponseGenerator(seed=42)

# Generate a random guidance response
response = generator.generate()

# Generate a successful response
success_response = generator.generate(status="success")

# Generate response for a specific patient
patient_response = generator.generate_for_patient(
    patient_id="patient-123",
    module_uri="http://example.org/guidance/diabetes-check",
    status="success"
)

# Generate response with specific reason
interaction_response = generator.generate(
    status="success",
    subject_reference="Patient/123",
    reason_codes=[{
        "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
        "code": "drug-drug-interaction",
        "display": "Drug-Drug Interaction"
    }]
)

# Generate batch
responses = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| success | Evaluation completed successfully |
| data-requested | Additional data is being requested |
| data-required | Additional data is required to complete |
| in-progress | Evaluation is in progress |
| failure | Evaluation failed |
| entered-in-error | Response was entered in error |

## Reason Codes

| Code | Display | Description |
|------|---------|-------------|
| drug-drug-interaction | Drug-Drug Interaction | Potential drug interaction detected |
| dosage-concern | Dosage Concern | Concern about dosage |
| contraindication | Contraindication | Clinical contraindication |
| duplicate-therapy | Duplicate Therapy | Duplicate therapy detected |

## Related Resources

- [Library](./library.md) - Logic library referenced by the module
- [PlanDefinition](./plan-definition.md) - Plan definition referenced by the module
- [RequestGroup](./request-group.md) - Resulting recommendations
- [Parameters](./parameters.md) - Output parameters
