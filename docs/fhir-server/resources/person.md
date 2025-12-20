# Person

## Overview

A Person represents a human being regardless of their role in the healthcare system. Unlike Patient or Practitioner, which represent specific roles, Person is used to link multiple patient or practitioner records that belong to the same individual.

This resource is particularly useful for patient matching, identity management, and linking records across different organizations or systems.

**Common use cases:**
- Master person index
- Patient record linking
- Identity management
- Cross-organization matching
- Demographics management

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/person.html](https://hl7.org/fhir/R4/person.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `name` | HumanName[] | Person's names |
| `telecom` | ContactPoint[] | Contact details |
| `gender` | code | male, female, other, unknown |
| `birthDate` | date | Date of birth |
| `address` | Address[] | Addresses |
| `photo` | Attachment | Photo of the person |
| `managingOrganization` | Reference(Organization) | Organization managing record |
| `active` | boolean | Whether record is active |
| `link` | BackboneElement[] | Links to related resources |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=person-001` |
| `identifier` | token | Business identifier | `identifier=SSN\|123-45-6789` |
| `name` | string | Person name | `name=Smith` |
| `gender` | token | Gender | `gender=male` |
| `birthdate` | date | Birth date | `birthdate=1980-05-15` |
| `address` | string | Address | `address=Boston` |
| `telecom` | token | Phone or email | `telecom=555-1234` |

## Examples

### Create a Person

```bash
curl -X POST http://localhost:8080/baseR4/Person \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Person",
    "identifier": [{
      "system": "http://hl7.org/fhir/sid/us-ssn",
      "value": "123-45-6789"
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
      "city": "Boston",
      "state": "MA"
    }],
    "link": [
      {
        "target": {"reference": "Patient/patient-123"},
        "assurance": "level4"
      },
      {
        "target": {"reference": "Practitioner/pract-456"},
        "assurance": "level3"
      }
    ]
  }'
```

### Search Persons

```bash
# By name
curl "http://localhost:8080/baseR4/Person?name=Smith"

# By identifier
curl "http://localhost:8080/baseR4/Person?identifier=123-45-6789"

# By gender and birthdate
curl "http://localhost:8080/baseR4/Person?gender=male&birthdate=1980-05-15"
```

## Generator Usage

```python
from fhirkit.server.generator import PersonGenerator

generator = PersonGenerator(seed=42)

# Generate a random person
person = generator.generate()

# Generate with specific gender
male_person = generator.generate(gender="male")

# Generate batch
persons = generator.generate_batch(count=10)
```

## Link Assurance Levels

| Level | Description |
|-------|-------------|
| level1 | No assurance - matches may be wrong |
| level2 | Some assurance - matches are probably correct |
| level3 | High assurance - matches are highly likely correct |
| level4 | Absolute assurance - records are known to be same person |

## Related Resources

- [Patient](./patient.md) - Patient records linked to person
- [Practitioner](./practitioner.md) - Practitioner records linked to person
- [RelatedPerson](./related-person.md) - Related person records
