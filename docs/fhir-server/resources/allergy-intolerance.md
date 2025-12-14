# AllergyIntolerance

## Overview

The AllergyIntolerance resource records a patient's allergies and intolerances to substances. This is a critical safety resource that captures information about adverse reactions that may occur upon exposure to specific substances, enabling clinical decision support and preventing harmful exposures.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/allergyintolerance.html](https://hl7.org/fhir/R4/allergyintolerance.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `clinicalStatus` | CodeableConcept | active, inactive, resolved |
| `verificationStatus` | CodeableConcept | unconfirmed, presumed, confirmed, refuted, entered-in-error |
| `type` | code | allergy or intolerance |
| `category` | code[] | food, medication, environment, biologic |
| `criticality` | code | low, high, unable-to-assess |
| `code` | CodeableConcept | The allergen (SNOMED CT code) |
| `patient` | Reference(Patient) | Patient who has the allergy |
| `encounter` | Reference(Encounter) | Encounter when recorded |
| `onsetDateTime` | dateTime | When allergy was first identified |
| `recordedDate` | dateTime | When recorded in the system |
| `recorder` | Reference(Practitioner) | Who recorded the allergy |
| `asserter` | Reference(Patient\|Practitioner) | Source of the information |
| `reaction` | BackboneElement[] | Reaction manifestations and severity |
| `note` | Annotation[] | Additional clinical notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `code` | token | Allergen code | `code=http://snomed.info/sct\|91936005` |
| `clinical-status` | token | Clinical status | `clinical-status=active` |
| `verification-status` | token | Verification status | `verification-status=confirmed` |
| `category` | token | Category | `category=medication` |
| `criticality` | token | Criticality level | `criticality=high` |
| `type` | token | Type | `type=allergy` |
| `onset` | date | Onset date | `onset=ge2020-01-01` |
| `date` | date | Recorded date | `date=2024-06-15` |
| `recorder` | reference | Recorder reference | `recorder=Practitioner/456` |
| `asserter` | reference | Asserter reference | `asserter=Patient/123` |

## Examples

### Create an AllergyIntolerance

```bash
curl -X POST http://localhost:8080/baseR4/AllergyIntolerance \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "AllergyIntolerance",
    "clinicalStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
        "code": "active",
        "display": "Active"
      }]
    },
    "verificationStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
        "code": "confirmed",
        "display": "Confirmed"
      }]
    },
    "type": "allergy",
    "category": ["medication"],
    "criticality": "high",
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "91936005",
        "display": "Penicillin allergy"
      }],
      "text": "Penicillin allergy"
    },
    "patient": {"reference": "Patient/patient-001"},
    "onsetDateTime": "2015-03-01",
    "recordedDate": "2024-06-15T10:30:00Z",
    "reaction": [{
      "manifestation": [{
        "coding": [{
          "system": "http://snomed.info/sct",
          "code": "39579001",
          "display": "Anaphylaxis"
        }]
      }],
      "severity": "severe"
    }],
    "note": [{
      "text": "Patient has history of anaphylactic reaction to penicillin. Epinephrine auto-injector prescribed."
    }]
  }'
```

### Search AllergyIntolerances

```bash
# By patient
curl "http://localhost:8080/baseR4/AllergyIntolerance?patient=Patient/123"

# By category (medication allergies)
curl "http://localhost:8080/baseR4/AllergyIntolerance?category=medication"

# By criticality (high-risk allergies)
curl "http://localhost:8080/baseR4/AllergyIntolerance?criticality=high"

# Active allergies only
curl "http://localhost:8080/baseR4/AllergyIntolerance?clinical-status=active"

# Confirmed medication allergies
curl "http://localhost:8080/baseR4/AllergyIntolerance?category=medication&verification-status=confirmed"

# Combined: patient's active high-criticality allergies
curl "http://localhost:8080/baseR4/AllergyIntolerance?patient=Patient/123&clinical-status=active&criticality=high"
```

### With _include

```bash
# Include the patient
curl "http://localhost:8080/baseR4/AllergyIntolerance?patient=123&_include=AllergyIntolerance:patient"

# Include the recorder
curl "http://localhost:8080/baseR4/AllergyIntolerance?_include=AllergyIntolerance:recorder"
```

### Patient Compartment Search

```bash
# Get all allergies for a patient via compartment
curl "http://localhost:8080/baseR4/Patient/123/AllergyIntolerance"

# With criticality filter
curl "http://localhost:8080/baseR4/Patient/123/AllergyIntolerance?criticality=high"
```

## Generator

The `AllergyIntoleranceGenerator` creates synthetic AllergyIntolerance resources with:

- Realistic SNOMED CT allergen codes for medications, foods, and environmental allergens
- Weighted category distribution (40% medication, 35% food, 25% environment)
- Appropriate criticality levels with associated reactions
- SNOMED CT reaction manifestation codes with severity
- Clinical notes for high-criticality allergies

### Usage

```python
from fhir_cql.server.generator import AllergyIntoleranceGenerator

generator = AllergyIntoleranceGenerator(seed=42)

# Generate a random allergy
allergy = generator.generate(
    patient_ref="Patient/123",
    recorder_ref="Practitioner/456"
)

# Generate specific category
med_allergy = generator.generate_medication_allergy(
    patient_ref="Patient/123"
)

food_allergy = generator.generate_food_allergy(
    patient_ref="Patient/123"
)

env_allergy = generator.generate_environmental_allergy(
    patient_ref="Patient/123"
)

# Generate batch
allergies = generator.generate_batch(
    count=5,
    patient_ref="Patient/123"
)
```

## Clinical Codes

Loaded from `fixtures/allergy_codes.json`:

### Medication Allergens (SNOMED CT)

| Code | Display |
|------|---------|
| 91936005 | Penicillin allergy |
| 294505008 | Amoxicillin allergy |
| 294532003 | Sulfonamide allergy |
| 293586001 | Aspirin allergy |
| 294306009 | Ibuprofen allergy |

### Food Allergens (SNOMED CT)

| Code | Display |
|------|---------|
| 91935009 | Allergy to peanuts |
| 91934008 | Allergy to tree nuts |
| 91930004 | Allergy to eggs |
| 91932007 | Allergy to shellfish |
| 91937001 | Allergy to soy |
| 425525006 | Allergy to dairy products |

### Environmental Allergens (SNOMED CT)

| Code | Display |
|------|---------|
| 418689008 | Allergy to grass pollen |
| 419474003 | Allergy to tree pollen |
| 232350006 | House dust mite allergy |
| 232346004 | Cat dander allergy |
| 441634002 | Allergy to latex |

### Reaction Manifestations (SNOMED CT)

| Code | Display | Typical Severity |
|------|---------|------------------|
| 39579001 | Anaphylaxis | severe |
| 271807003 | Skin rash | mild |
| 126485001 | Urticaria | mild |
| 267036007 | Dyspnea | moderate |
| 271757001 | Facial swelling | severe |
| 418363000 | Throat tightness | severe |

### Clinical Status Codes

| Code | Display |
|------|---------|
| active | Active |
| inactive | Inactive |
| resolved | Resolved |

### Criticality Levels

| Code | Description |
|------|-------------|
| low | Low risk of life-threatening reaction |
| high | High risk of life-threatening reaction |
| unable-to-assess | Unable to assess criticality |
