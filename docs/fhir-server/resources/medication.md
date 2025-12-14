# Medication

## Overview

The Medication resource represents a medication that can be prescribed, dispensed, or administered. It acts as a catalog-style resource providing details about medication products including their ingredients, dose forms, and manufacturer information.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/medication.html](https://hl7.org/fhir/R4/medication.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | active, inactive, entered-in-error |
| `code` | CodeableConcept | Medication code (RxNorm) |
| `form` | CodeableConcept | Dose form (tablet, capsule, etc.) |
| `manufacturer` | Reference(Organization) | Drug manufacturer |
| `ingredient` | BackboneElement[] | Active and inactive ingredients |
| `batch` | BackboneElement | Lot number and expiration date |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `code` | token | Medication code | `code=http://www.nlm.nih.gov/research/umls/rxnorm\|310965` |
| `status` | token | Status | `status=active` |
| `form` | token | Dose form | `form=http://snomed.info/sct\|385055001` |
| `manufacturer` | reference | Manufacturer reference | `manufacturer=Organization/pharma-1` |
| `lot-number` | string | Batch lot number | `lot-number=AB1234-56` |
| `expiration-date` | date | Expiration date | `expiration-date=ge2025-01-01` |

## Examples

### Create a Medication

```bash
curl -X POST http://localhost:8080/baseR4/Medication \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Medication",
    "status": "active",
    "code": {
      "coding": [{
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "310965",
        "display": "Lisinopril 10 MG Oral Tablet"
      }],
      "text": "Lisinopril 10 mg tablet"
    },
    "form": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "385055001",
        "display": "Tablet"
      }],
      "text": "Tablet"
    },
    "ingredient": [{
      "itemCodeableConcept": {
        "coding": [{
          "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
          "code": "29046",
          "display": "Lisinopril"
        }]
      },
      "isActive": true,
      "strength": {
        "numerator": {
          "value": 10,
          "unit": "mg",
          "system": "http://unitsofmeasure.org",
          "code": "mg"
        },
        "denominator": {
          "value": 1,
          "unit": "tablet"
        }
      }
    }],
    "batch": {
      "lotNumber": "AB1234-56",
      "expirationDate": "2026-06-30"
    }
  }'
```

### Search Medications

```bash
# By code (RxNorm)
curl "http://localhost:8080/baseR4/Medication?code=http://www.nlm.nih.gov/research/umls/rxnorm|310965"

# Active medications
curl "http://localhost:8080/baseR4/Medication?status=active"

# By form (tablets)
curl "http://localhost:8080/baseR4/Medication?form=http://snomed.info/sct|385055001"

# By lot number
curl "http://localhost:8080/baseR4/Medication?lot-number=AB1234-56"

# By expiration (not expired)
curl "http://localhost:8080/baseR4/Medication?expiration-date=ge2025-01-01"
```

## Generator

The `MedicationGenerator` creates synthetic Medication resources with:

- RxNorm medication codes (reuses existing medications fixture)
- SNOMED CT dose form codes
- Ingredient strengths
- Batch/lot information with expiration dates

### Usage

```python
from fhir_cql.server.generator import MedicationGenerator

generator = MedicationGenerator(seed=42)

# Generate any medication
medication = generator.generate(
    manufacturer_ref="Organization/pharma-1"
)

# Generate specific forms
tablet = generator.generate_tablet()
injection = generator.generate_injection()

# Generate batch
medications = generator.generate_batch(count=10)
```

## Clinical Codes

### Dose Forms (SNOMED CT)

| Code | Display |
|------|---------|
| 385055001 | Tablet |
| 385049006 | Capsule |
| 385023001 | Oral solution |
| 385219001 | Injection solution |
| 385101003 | Ointment |
| 385089002 | Cream |
| 421720008 | Spray |
| 385181001 | Patch |

### Common Strengths

| Value | Unit |
|-------|------|
| 5 | mg |
| 10 | mg |
| 25 | mg |
| 50 | mg |
| 100 | mg |
| 250 | mg |
| 500 | mg |

### Status Codes

| Code | Description |
|------|-------------|
| active | Medication is available for use |
| inactive | Medication is no longer in use |
| entered-in-error | Entry was made in error |
