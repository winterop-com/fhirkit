# Substance

## Overview

A Substance represents a homogeneous material with a definite chemical composition. In healthcare contexts, substances are commonly used to represent ingredients in medications, allergens, or materials used in procedures.

This resource describes the composition and properties of substances that may be referenced by other clinical resources like AllergyIntolerance or Medication.

**Common use cases:**
- Medication ingredients
- Allergen identification
- Laboratory reagents
- Material tracking
- Chemical compounds

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/substance.html](https://hl7.org/fhir/R4/substance.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, inactive, entered-in-error |
| `category` | CodeableConcept[] | Substance category |
| `code` | CodeableConcept | Substance code (required) |
| `description` | string | Textual description |
| `instance` | BackboneElement[] | Specific instances |
| `ingredient` | BackboneElement[] | Composition information |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=substance-001` |
| `identifier` | token | Business identifier | `identifier=SUB-12345` |
| `status` | token | Substance status | `status=active` |
| `category` | token | Category code | `category=drug` |
| `code` | token | Substance code | `code=387458008` |

## Examples

### Create a Substance

```bash
curl -X POST http://localhost:8080/baseR4/Substance \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Substance",
    "identifier": [{
      "system": "http://hospital.example.org/substances",
      "value": "SUB-001"
    }],
    "status": "active",
    "category": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/substance-category",
        "code": "drug",
        "display": "Drug or Medicament"
      }]
    }],
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "387458008",
        "display": "Aspirin"
      }],
      "text": "Aspirin"
    },
    "description": "Acetylsalicylic acid"
  }'
```

### Search Substances

```bash
# By code
curl "http://localhost:8080/baseR4/Substance?code=387458008"

# By category
curl "http://localhost:8080/baseR4/Substance?category=drug"

# By status
curl "http://localhost:8080/baseR4/Substance?status=active"
```

## Generator Usage

```python
from fhirkit.server.generator import SubstanceGenerator

generator = SubstanceGenerator(seed=42)

# Generate a random substance
substance = generator.generate()

# Generate batch
substances = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| active | Substance is active |
| inactive | Substance is inactive |
| entered-in-error | Entered in error |

## Category Codes

| Code | Description |
|------|-------------|
| allergen | Allergen |
| biological | Biological substance |
| body | Body substance |
| chemical | Chemical |
| drug | Drug or Medicament |
| food | Dietary substance |
| material | Material |

## Related Resources

- [Medication](./medication.md) - Medications containing substances
- [AllergyIntolerance](./allergy-intolerance.md) - Allergies to substances
