# Patient

## Overview

The Patient resource represents an individual receiving healthcare services. It is the foundation of clinical data in FHIR and contains demographic and administrative information about the person.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/patient.html](https://hl7.org/fhir/R4/patient.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Medical record numbers, SSN, etc. |
| `active` | boolean | Whether patient record is active |
| `name` | HumanName[] | Patient's legal and preferred names |
| `telecom` | ContactPoint[] | Phone numbers, email addresses |
| `gender` | code | male, female, other, unknown |
| `birthDate` | date | Date of birth |
| `deceased[x]` | boolean or dateTime | Indicates if patient is deceased |
| `address` | Address[] | Home, work, or temporary addresses |
| `maritalStatus` | CodeableConcept | Marital status |
| `multipleBirth[x]` | boolean or integer | Multiple birth indicator |
| `photo` | Attachment[] | Patient photos |
| `contact` | BackboneElement[] | Emergency contacts |
| `communication` | BackboneElement[] | Languages spoken |
| `generalPractitioner` | Reference(Practitioner)[] | Primary care providers |
| `managingOrganization` | Reference(Organization) | Organization managing the record |
| `link` | BackboneElement[] | Links to other patient records |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=patient-001` |
| `identifier` | token | MRN or other identifier | `identifier=MRN\|12345` |
| `name` | string | Search by name | `name=Smith` |
| `family` | string | Family name | `family=Smith` |
| `given` | string | Given name | `given=John` |
| `gender` | token | Gender | `gender=male` |
| `birthdate` | date | Date of birth | `birthdate=1980-05-15` |
| `address` | string | Any address field | `address=Boston` |
| `address-city` | string | City | `address-city=Boston` |
| `address-state` | string | State | `address-state=MA` |
| `address-postalcode` | string | Postal code | `address-postalcode=02115` |
| `telecom` | token | Phone or email | `telecom=555-1234` |
| `active` | token | Active status | `active=true` |

## Examples

### Create a Patient

```bash
curl -X POST http://localhost:8080/baseR4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "identifier": [{
      "system": "http://hospital.example.org/mrn",
      "value": "MRN-12345"
    }],
    "active": true,
    "name": [{
      "use": "official",
      "family": "Smith",
      "given": ["John", "Michael"]
    }],
    "gender": "male",
    "birthDate": "1980-05-15",
    "address": [{
      "use": "home",
      "line": ["123 Main Street"],
      "city": "Boston",
      "state": "MA",
      "postalCode": "02115"
    }],
    "telecom": [
      {"system": "phone", "value": "555-123-4567", "use": "home"},
      {"system": "email", "value": "john.smith@email.com"}
    ]
  }'
```

### Search Patients

```bash
# By name
curl "http://localhost:8080/baseR4/Patient?name=Smith"

# By gender
curl "http://localhost:8080/baseR4/Patient?gender=male"

# By birth date
curl "http://localhost:8080/baseR4/Patient?birthdate=1980-05-15"

# By city
curl "http://localhost:8080/baseR4/Patient?address-city=Boston"

# Combined: male patients named Smith in Boston
curl "http://localhost:8080/baseR4/Patient?name=Smith&gender=male&address-city=Boston"
```

### With _include

```bash
# Include general practitioner
curl "http://localhost:8080/baseR4/Patient?_include=Patient:general-practitioner"

# Include managing organization
curl "http://localhost:8080/baseR4/Patient?_include=Patient:organization"
```

### Patient Compartment

The Patient compartment provides access to all resources associated with a patient:

```bash
# Get everything for a patient
curl "http://localhost:8080/baseR4/Patient/123/$everything"

# Get patient's observations
curl "http://localhost:8080/baseR4/Patient/123/Observation"

# Get patient's conditions
curl "http://localhost:8080/baseR4/Patient/123/Condition"
```

## Generator

The `PatientGenerator` creates synthetic Patient resources with:

- Realistic names from name databases
- Weighted gender distribution
- Age-appropriate birth dates
- US-based addresses
- Phone numbers and email addresses

### Usage

```python
from fhirkit.server.generator import PatientGenerator

generator = PatientGenerator(seed=42)

# Generate a random patient
patient = generator.generate()

# Generate with specific gender
male_patient = generator.generate(gender="male")

# Generate batch
patients = generator.generate_batch(count=100)
```

## Gender Codes

| Code | Display |
|------|---------|
| male | Male |
| female | Female |
| other | Other |
| unknown | Unknown |

## Marital Status Codes

| Code | Display |
|------|---------|
| A | Annulled |
| D | Divorced |
| I | Interlocutory |
| L | Legally Separated |
| M | Married |
| P | Polygamous |
| S | Never Married |
| T | Domestic Partner |
| U | Unmarried |
| W | Widowed |
