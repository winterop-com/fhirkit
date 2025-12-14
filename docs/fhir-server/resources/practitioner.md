# Practitioner

## Overview

The Practitioner resource represents a healthcare provider who delivers care to patients. This includes physicians, nurses, therapists, and other clinical staff involved in patient care.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/practitioner.html](https://hl7.org/fhir/R4/practitioner.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | NPI, DEA, license numbers |
| `active` | boolean | Whether currently practicing |
| `name` | HumanName[] | Provider name |
| `telecom` | ContactPoint[] | Contact information |
| `address` | Address[] | Practice addresses |
| `gender` | code | male, female, other, unknown |
| `birthDate` | date | Date of birth |
| `photo` | Attachment[] | Provider photos |
| `qualification` | BackboneElement[] | Certifications and degrees |
| `communication` | CodeableConcept[] | Languages spoken |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=practitioner-001` |
| `identifier` | token | NPI or other identifier | `identifier=NPI\|1234567890` |
| `name` | string | Search by name | `name=Smith` |
| `family` | string | Family name | `family=Smith` |
| `given` | string | Given name | `given=Jane` |
| `active` | token | Active status | `active=true` |

## Examples

### Create a Practitioner

```bash
curl -X POST http://localhost:8080/baseR4/Practitioner \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Practitioner",
    "identifier": [
      {
        "system": "http://hl7.org/fhir/sid/us-npi",
        "value": "1234567890"
      },
      {
        "system": "http://example.org/license",
        "value": "MD-12345"
      }
    ],
    "active": true,
    "name": [{
      "use": "official",
      "family": "Smith",
      "given": ["Jane"],
      "prefix": ["Dr."]
    }],
    "gender": "female",
    "telecom": [
      {"system": "phone", "value": "555-123-4567", "use": "work"},
      {"system": "email", "value": "dr.smith@hospital.org"}
    ],
    "address": [{
      "use": "work",
      "line": ["123 Medical Center Drive"],
      "city": "Boston",
      "state": "MA",
      "postalCode": "02115"
    }],
    "qualification": [{
      "identifier": [{
        "system": "http://example.org/qualifications",
        "value": "MD-2010"
      }],
      "code": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
          "code": "MD",
          "display": "Doctor of Medicine"
        }]
      },
      "period": {"start": "2010-06-01"},
      "issuer": {"display": "Harvard Medical School"}
    }]
  }'
```

### Search Practitioners

```bash
# By name
curl "http://localhost:8080/baseR4/Practitioner?name=Smith"

# By NPI
curl "http://localhost:8080/baseR4/Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|1234567890"

# Active practitioners
curl "http://localhost:8080/baseR4/Practitioner?active=true"

# By family name
curl "http://localhost:8080/baseR4/Practitioner?family=Smith"
```

### With _revinclude

```bash
# Include PractitionerRoles
curl "http://localhost:8080/baseR4/Practitioner?_revinclude=PractitionerRole:practitioner"
```

## Generator

The `PractitionerGenerator` creates synthetic Practitioner resources with:

- Realistic names with appropriate prefixes (Dr., etc.)
- NPI identifiers
- Medical qualifications and specialties
- Contact information

### Usage

```python
from fhirkit.server.generator import PractitionerGenerator

generator = PractitionerGenerator(seed=42)

# Generate a random practitioner
practitioner = generator.generate()

# Generate batch
practitioners = generator.generate_batch(count=20)
```
