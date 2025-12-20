# InsurancePlan

## Overview

An InsurancePlan represents an insurance product offered by an insurer. It describes the benefits, costs, and coverage details of a specific insurance plan that individuals or groups can enroll in.

This resource is used to describe insurance products, including their coverage types, cost sharing details, and network information.

**Common use cases:**
- Insurance product catalogs
- Benefit summaries
- Plan comparison
- Enrollment options
- Network definitions

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/insuranceplan.html](https://hl7.org/fhir/R4/insuranceplan.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | draft, active, retired, unknown |
| `type` | CodeableConcept[] | Type of plan (medical, dental, vision, etc.) |
| `name` | string | Plan name |
| `alias` | string[] | Alternate names |
| `period` | Period | When plan is effective |
| `ownedBy` | Reference(Organization) | Plan owner |
| `administeredBy` | Reference(Organization) | Plan administrator |
| `coverageArea` | Reference(Location)[] | Geographic coverage area |
| `contact` | BackboneElement[] | Contact information |
| `coverage` | BackboneElement[] | Coverage details |
| `plan` | BackboneElement[] | Plan details |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=plan-001` |
| `identifier` | token | Business identifier | `identifier=PLAN-12345` |
| `name` | string | Plan name | `name=Gold%20Plan` |
| `status` | token | Plan status | `status=active` |
| `type` | token | Plan type | `type=medical` |
| `owned-by` | reference | Owner organization | `owned-by=Organization/insurer-001` |
| `administered-by` | reference | Administrator | `administered-by=Organization/admin-001` |

## Examples

### Create an InsurancePlan

```bash
curl -X POST http://localhost:8080/baseR4/InsurancePlan \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "InsurancePlan",
    "identifier": [{
      "system": "http://insurer.example.org/plans",
      "value": "PLAN-2024-GOLD"
    }],
    "status": "active",
    "type": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/insurance-plan-type",
        "code": "medical",
        "display": "Medical"
      }]
    }],
    "name": "Gold Medical Plan 2024",
    "alias": ["Gold Plan", "Premium Medical"],
    "period": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "ownedBy": {"reference": "Organization/insurer-001"},
    "administeredBy": {"reference": "Organization/admin-001"}
  }'
```

### Search InsurancePlans

```bash
# By status
curl "http://localhost:8080/baseR4/InsurancePlan?status=active"

# By name
curl "http://localhost:8080/baseR4/InsurancePlan?name=Gold"

# By type
curl "http://localhost:8080/baseR4/InsurancePlan?type=medical"

# By owner
curl "http://localhost:8080/baseR4/InsurancePlan?owned-by=Organization/insurer-001"
```

## Generator Usage

```python
from fhirkit.server.generator import InsurancePlanGenerator

generator = InsurancePlanGenerator(seed=42)

# Generate a random insurance plan
plan = generator.generate()

# Generate active medical plan
medical_plan = generator.generate(
    name="Silver Medical Plan",
    status="active"
)

# Generate batch
plans = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| draft | Plan is in draft |
| active | Plan is currently active |
| retired | Plan is no longer offered |
| unknown | Status is unknown |

## Plan Type Codes

| Code | Description |
|------|-------------|
| medical | Medical insurance |
| dental | Dental insurance |
| vision | Vision insurance |
| pharmacy | Pharmacy benefits |
| mental | Mental health coverage |
| substance | Substance abuse coverage |

## Related Resources

- [Coverage](./coverage.md) - Patient coverage under this plan
- [Organization](./organization.md) - Plan owner/administrator
- [EnrollmentRequest](./enrollment-request.md) - Enrollment in plan
