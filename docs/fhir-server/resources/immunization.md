# Immunization

## Overview

The Immunization resource describes the event of a patient being administered a vaccine or a record of an immunization as reported by a patient or another party. It captures the vaccine administered, when it was given, who administered it, and other relevant details.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/immunization.html](https://hl7.org/fhir/R4/immunization.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | completed, entered-in-error, not-done |
| `statusReason` | CodeableConcept | Reason immunization was not performed |
| `vaccineCode` | CodeableConcept | Vaccine product administered (CVX code) |
| `patient` | Reference(Patient) | Who was immunized |
| `encounter` | Reference(Encounter) | Encounter immunization was part of |
| `occurrenceDateTime` | dateTime | When the immunization occurred |
| `primarySource` | boolean | Whether data is from the person who administered |
| `site` | CodeableConcept | Body site vaccine was administered (SNOMED CT) |
| `route` | CodeableConcept | How vaccine entered body (IM, SC, etc.) |
| `lotNumber` | string | Vaccine lot number |
| `expirationDate` | date | Vaccine expiration date |
| `performer` | BackboneElement[] | Who performed the immunization |
| `doseQuantity` | Quantity | Amount of vaccine administered |
| `note` | Annotation[] | Additional immunization notes |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `vaccine-code` | token | Vaccine code | `vaccine-code=http://hl7.org/fhir/sid/cvx\|208` |
| `status` | token | Status | `status=completed` |
| `date` | date | Occurrence date | `date=ge2024-01-01` |
| `lot-number` | string | Lot number | `lot-number=AB1234-56` |
| `performer` | reference | Performer reference | `performer=Practitioner/456` |
| `site` | token | Injection site | `site=http://snomed.info/sct\|368208006` |
| `route` | token | Administration route | `route=IM` |

## Examples

### Create an Immunization

```bash
curl -X POST http://localhost:8080/baseR4/Immunization \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Immunization",
    "status": "completed",
    "vaccineCode": {
      "coding": [{
        "system": "http://hl7.org/fhir/sid/cvx",
        "code": "208",
        "display": "COVID-19, mRNA, Pfizer-BioNTech"
      }],
      "text": "COVID-19, mRNA, Pfizer-BioNTech"
    },
    "patient": {"reference": "Patient/patient-001"},
    "occurrenceDateTime": "2024-06-15T10:30:00Z",
    "primarySource": true,
    "site": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "368208006",
        "display": "Left upper arm structure"
      }]
    },
    "route": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration",
        "code": "IM",
        "display": "Injection, intramuscular"
      }]
    },
    "lotNumber": "EL9262",
    "expirationDate": "2025-06-30",
    "performer": [{
      "function": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v2-0443",
          "code": "AP",
          "display": "Administering Provider"
        }]
      },
      "actor": {"reference": "Practitioner/practitioner-001"}
    }],
    "doseQuantity": {
      "value": 0.5,
      "unit": "mL",
      "system": "http://unitsofmeasure.org",
      "code": "mL"
    }
  }'
```

### Search Immunizations

```bash
# By patient
curl "http://localhost:8080/baseR4/Immunization?patient=Patient/123"

# By vaccine code (COVID-19 vaccines)
curl "http://localhost:8080/baseR4/Immunization?vaccine-code=http://hl7.org/fhir/sid/cvx|208"

# By status
curl "http://localhost:8080/baseR4/Immunization?status=completed"

# By date range (immunizations in 2024)
curl "http://localhost:8080/baseR4/Immunization?date=ge2024-01-01&date=le2024-12-31"

# By lot number
curl "http://localhost:8080/baseR4/Immunization?lot-number=EL9262"

# Combined: patient's flu shots
curl "http://localhost:8080/baseR4/Immunization?patient=Patient/123&vaccine-code=http://hl7.org/fhir/sid/cvx|158"
```

### With _include

```bash
# Include the patient
curl "http://localhost:8080/baseR4/Immunization?patient=123&_include=Immunization:patient"

# Include the performer
curl "http://localhost:8080/baseR4/Immunization?_include=Immunization:performer"
```

### Patient Compartment Search

```bash
# Get all immunizations for a patient via compartment
curl "http://localhost:8080/baseR4/Patient/123/Immunization"

# With status filter
curl "http://localhost:8080/baseR4/Patient/123/Immunization?status=completed"
```

## Generator

The `ImmunizationGenerator` creates synthetic Immunization resources with:

- CVX vaccine codes for common vaccines (flu, COVID-19, pneumococcal, etc.)
- SNOMED CT injection site codes
- HL7 route of administration codes
- Realistic lot numbers and expiration dates
- Weighted status distributions (95% completed)

### Usage

```python
from fhirkit.server.generator import ImmunizationGenerator

generator = ImmunizationGenerator(seed=42)

# Generate a random immunization
immunization = generator.generate(
    patient_ref="Patient/123",
    performer_ref="Practitioner/456"
)

# Generate specific vaccine types
flu_shot = generator.generate_flu_shot(
    patient_ref="Patient/123",
    performer_ref="Practitioner/456"
)

covid_vaccine = generator.generate_covid_vaccination(
    patient_ref="Patient/123",
    performer_ref="Practitioner/456"
)

# Generate batch
immunizations = generator.generate_batch(
    count=10,
    patient_ref="Patient/123"
)
```

## Clinical Codes

Loaded from `fixtures/immunization_codes.json`:

### Vaccine Codes (CVX)

| Code | Display |
|------|---------|
| 158 | Influenza, injectable, quadrivalent |
| 208 | COVID-19, mRNA, Pfizer-BioNTech |
| 207 | COVID-19, mRNA, Moderna |
| 133 | Pneumococcal conjugate PCV13 |
| 216 | Pneumococcal conjugate PCV20 |
| 03 | MMR (Measles, Mumps, Rubella) |
| 121 | Zoster (Shingrix) |
| 45 | Hepatitis B, adult |
| 165 | HPV, 9-valent (Gardasil 9) |
| 115 | Tdap (Tetanus, Diphtheria, Pertussis) |
| 114 | Meningococcal MCV4 |

### Injection Sites (SNOMED CT)

| Code | Display |
|------|---------|
| 368208006 | Left upper arm structure |
| 368209003 | Right upper arm structure |
| 61396006 | Left thigh structure |
| 11207009 | Right thigh structure |

### Routes of Administration

| Code | Display |
|------|---------|
| IM | Injection, intramuscular |
| SC | Injection, subcutaneous |
| ID | Injection, intradermal |
| NASINHL | Inhalation, nasal |

### Status Codes

| Code | Description |
|------|-------------|
| completed | Immunization was administered |
| entered-in-error | Entry was made in error |
| not-done | Immunization was not administered |

### Status Reasons (for not-done)

| Code | Display |
|------|---------|
| IMMUNE | Immunity |
| MEDPREC | Medical precaution |
| OSTOCK | Product out of stock |
| PATOBJ | Patient objection |
| VACEFF | Vaccine efficacy concerns |
