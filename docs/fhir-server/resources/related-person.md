# RelatedPerson

## Overview

The RelatedPerson resource represents a person who is related to a patient but is not a direct healthcare provider. This includes family members, caregivers, guardians, and emergency contacts.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/relatedperson.html](https://hl7.org/fhir/R4/relatedperson.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `active` | boolean | Whether relationship is active |
| `patient` | Reference(Patient) | The patient this person is related to |
| `relationship` | CodeableConcept[] | Nature of relationship |
| `name` | HumanName[] | Person's name |
| `telecom` | ContactPoint[] | Contact information |
| `gender` | code | male, female, other, unknown |
| `birthDate` | date | Date of birth |
| `address` | Address[] | Addresses |
| `photo` | Attachment[] | Photos |
| `period` | Period | Period of relationship validity |
| `communication` | BackboneElement[] | Languages spoken |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=rp-001` |
| `identifier` | token | Business identifier | `identifier=RP-12345` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `name` | string | Person name | `name=Smith` |
| `active` | token | Active status | `active=true` |
| `gender` | token | Gender | `gender=female` |
| `birthdate` | date | Date of birth | `birthdate=1982-03-15` |
| `relationship` | token | Relationship type | `relationship=SPS` |
| `telecom` | token | Contact information | `telecom=555-1234` |
| `address` | string | Address | `address=Boston` |
| `address-city` | string | City | `address-city=Boston` |
| `address-state` | string | State | `address-state=MA` |

## Examples

### Create a RelatedPerson

```bash
curl -X POST http://localhost:8080/baseR4/RelatedPerson \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "RelatedPerson",
    "active": true,
    "patient": {
      "reference": "Patient/patient-001"
    },
    "relationship": [
      {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
          "code": "SPS",
          "display": "spouse"
        }],
        "text": "Spouse"
      },
      {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
          "code": "ECON",
          "display": "emergency contact"
        }],
        "text": "Emergency Contact"
      }
    ],
    "name": [{
      "use": "official",
      "family": "Smith",
      "given": ["Mary", "Jane"]
    }],
    "telecom": [
      {"system": "phone", "value": "555-987-6543", "use": "mobile"},
      {"system": "email", "value": "mary.smith@email.com"}
    ],
    "gender": "female",
    "birthDate": "1982-03-15",
    "address": [{
      "use": "home",
      "line": ["456 Oak Street"],
      "city": "Boston",
      "state": "MA",
      "postalCode": "02116"
    }],
    "period": {"start": "2010-06-20"},
    "communication": [{
      "language": {
        "coding": [{
          "system": "urn:ietf:bcp:47",
          "code": "en",
          "display": "English"
        }]
      },
      "preferred": true
    }]
  }'
```

### Search RelatedPersons

```bash
# By patient
curl "http://localhost:8080/baseR4/RelatedPerson?patient=Patient/123"

# By name
curl "http://localhost:8080/baseR4/RelatedPerson?name=Smith"

# By relationship type
curl "http://localhost:8080/baseR4/RelatedPerson?relationship=SPS"

# Active relationships
curl "http://localhost:8080/baseR4/RelatedPerson?active=true"

# Combined: patient's emergency contacts
curl "http://localhost:8080/baseR4/RelatedPerson?patient=Patient/123&relationship=ECON"
```

### With _include

```bash
# Include patient
curl "http://localhost:8080/baseR4/RelatedPerson?_include=RelatedPerson:patient"
```

### Patient Compartment

```bash
# Get all related persons for a patient
curl "http://localhost:8080/baseR4/Patient/123/RelatedPerson"
```

## Relationship Types (v3-RoleCode)

### Family Relationships

| Code | Display |
|------|---------|
| FAMMEMB | Family Member |
| CHILD | Child |
| CHLDADOPT | Adopted Child |
| DAUADOPT | Adopted Daughter |
| SONADOPT | Adopted Son |
| CHLDFOST | Foster Child |
| DAUFOST | Foster Daughter |
| SONFOST | Foster Son |
| DAUC | Daughter |
| SONC | Son |
| STPCHLD | Step Child |
| STPDAU | Step Daughter |
| STPSON | Step Son |
| NCHILD | Natural Child |
| DAU | Natural Daughter |
| SON | Natural Son |

### Spousal Relationships

| Code | Display |
|------|---------|
| SPS | Spouse |
| HUSB | Husband |
| WIFE | Wife |
| DOMPART | Domestic Partner |

### Parent Relationships

| Code | Display |
|------|---------|
| PRN | Parent |
| FTH | Father |
| MTH | Mother |
| NPRN | Natural Parent |
| NFTH | Natural Father |
| NMTH | Natural Mother |
| STPPRN | Step Parent |
| STPFTH | Step Father |
| STPMTH | Step Mother |

### Sibling Relationships

| Code | Display |
|------|---------|
| SIB | Sibling |
| BRO | Brother |
| SIS | Sister |
| HBRO | Half-Brother |
| HSIS | Half-Sister |
| STPBRO | Step Brother |
| STPSIS | Step Sister |

### Other Relationships

| Code | Display |
|------|---------|
| ECON | Emergency Contact |
| GUARD | Guardian |
| POWATT | Power of Attorney |
| DPOWATT | Durable Power of Attorney |
| FRND | Friend |
| NBOR | Neighbor |
