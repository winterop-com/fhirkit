# VisionPrescription

## Overview

A VisionPrescription represents a prescription for glasses or contact lenses. It contains the optical specifications needed to fulfill a vision correction order, including sphere, cylinder, axis, and other parameters.

This resource is used by optometrists and ophthalmologists to communicate prescription details to dispensing opticians or optical retailers.

**Common use cases:**
- Eyeglass prescriptions
- Contact lens prescriptions
- Vision correction orders
- Optical dispensing

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/visionprescription.html](https://hl7.org/fhir/R4/visionprescription.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, cancelled, draft, entered-in-error |
| `created` | dateTime | When prescription was created |
| `patient` | Reference(Patient) | Patient for the prescription |
| `encounter` | Reference(Encounter) | Related encounter |
| `dateWritten` | dateTime | When prescription was written |
| `prescriber` | Reference(Practitioner) | Prescribing practitioner |
| `lensSpecification` | BackboneElement[] | Lens specifications |
| `lensSpecification.eye` | code | right, left |
| `lensSpecification.sphere` | decimal | Sphere power |
| `lensSpecification.cylinder` | decimal | Cylinder power |
| `lensSpecification.axis` | integer | Axis in degrees |
| `lensSpecification.add` | decimal | Addition power |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=rx-001` |
| `identifier` | token | Business identifier | `identifier=RX-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `status` | token | Prescription status | `status=active` |
| `datewritten` | date | Date written | `datewritten=2024-01-15` |
| `prescriber` | reference | Prescriber reference | `prescriber=Practitioner/456` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/enc-001` |

## Examples

### Create a VisionPrescription

```bash
curl -X POST http://localhost:8080/baseR4/VisionPrescription \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "VisionPrescription",
    "identifier": [{
      "system": "http://optometry.example.org/prescriptions",
      "value": "RX-2024-001"
    }],
    "status": "active",
    "created": "2024-01-15T10:00:00Z",
    "patient": {"reference": "Patient/123"},
    "dateWritten": "2024-01-15",
    "prescriber": {"reference": "Practitioner/optometrist-001"},
    "lensSpecification": [
      {
        "product": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/ex-visionprescriptionproduct",
            "code": "lens",
            "display": "Lens"
          }]
        },
        "eye": "right",
        "sphere": -2.00,
        "cylinder": -0.50,
        "axis": 180,
        "add": 1.75
      },
      {
        "product": {
          "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/ex-visionprescriptionproduct",
            "code": "lens",
            "display": "Lens"
          }]
        },
        "eye": "left",
        "sphere": -1.75,
        "cylinder": -0.75,
        "axis": 175,
        "add": 1.75
      }
    ]
  }'
```

### Search VisionPrescriptions

```bash
# By patient
curl "http://localhost:8080/baseR4/VisionPrescription?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/VisionPrescription?status=active"

# By prescriber
curl "http://localhost:8080/baseR4/VisionPrescription?prescriber=Practitioner/optometrist-001"

# By date
curl "http://localhost:8080/baseR4/VisionPrescription?datewritten=ge2024-01-01"
```

## Generator Usage

```python
from fhirkit.server.generator import VisionPrescriptionGenerator

generator = VisionPrescriptionGenerator(seed=42)

# Generate a random vision prescription
prescription = generator.generate()

# Generate for specific patient
patient_rx = generator.generate(
    patient_reference="Patient/123",
    prescriber_reference="Practitioner/456"
)

# Generate batch
prescriptions = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| active | Prescription is active |
| cancelled | Prescription was cancelled |
| draft | Prescription is a draft |
| entered-in-error | Entered in error |

## Eye Codes

| Code | Description |
|------|-------------|
| right | Right eye |
| left | Left eye |

## Related Resources

- [Patient](./patient.md) - Patient receiving prescription
- [Practitioner](./practitioner.md) - Prescribing provider
- [Encounter](./encounter.md) - Related encounter
