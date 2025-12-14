# PractitionerRole

## Overview

The PractitionerRole resource links practitioners to organizations, locations, and specialties. It describes the roles a practitioner plays at an organization, including their specialty, location, and availability.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/practitionerrole.html](https://hl7.org/fhir/R4/practitionerrole.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `active` | boolean | Whether role is currently active |
| `period` | Period | Period during which role is valid |
| `practitioner` | Reference(Practitioner) | The practitioner |
| `organization` | Reference(Organization) | The organization |
| `code` | CodeableConcept[] | Role codes (doctor, nurse, etc.) |
| `specialty` | CodeableConcept[] | Medical specialties |
| `location` | Reference(Location)[] | Practice locations |
| `healthcareService` | Reference(HealthcareService)[] | Services provided |
| `telecom` | ContactPoint[] | Role-specific contact info |
| `availableTime` | BackboneElement[] | Times available |
| `notAvailable` | BackboneElement[] | Times not available |
| `availabilityExceptions` | string | Exceptions to availability |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=pr-001` |
| `identifier` | token | Business identifier | `identifier=PR-12345` |
| `practitioner` | reference | Practitioner reference | `practitioner=Practitioner/123` |
| `organization` | reference | Organization reference | `organization=Organization/456` |
| `role` | token | Role code | `role=doctor` |
| `specialty` | token | Specialty code | `specialty=394814009` |
| `active` | token | Active status | `active=true` |
| `location` | reference | Location reference | `location=Location/789` |
| `telecom` | token | Contact information | `telecom=555-1234` |
| `date` | date | Period start date | `date=ge2024-01-01` |

## Examples

### Create a PractitionerRole

```bash
curl -X POST http://localhost:8080/baseR4/PractitionerRole \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "PractitionerRole",
    "active": true,
    "period": {"start": "2020-01-01"},
    "practitioner": {
      "reference": "Practitioner/practitioner-001",
      "display": "Dr. Jane Smith"
    },
    "organization": {
      "reference": "Organization/organization-001",
      "display": "General Hospital"
    },
    "code": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/practitioner-role",
        "code": "doctor",
        "display": "Doctor"
      }]
    }],
    "specialty": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "394814009",
        "display": "General practice"
      }]
    }],
    "location": [{
      "reference": "Location/location-001",
      "display": "Main Building"
    }],
    "telecom": [
      {"system": "phone", "value": "555-123-4567", "use": "work"},
      {"system": "email", "value": "dr.smith@hospital.org"}
    ],
    "availableTime": [{
      "daysOfWeek": ["mon", "tue", "wed", "thu", "fri"],
      "availableStartTime": "08:00:00",
      "availableEndTime": "17:00:00"
    }]
  }'
```

### Search PractitionerRoles

```bash
# By practitioner
curl "http://localhost:8080/baseR4/PractitionerRole?practitioner=Practitioner/123"

# By organization
curl "http://localhost:8080/baseR4/PractitionerRole?organization=Organization/456"

# By specialty
curl "http://localhost:8080/baseR4/PractitionerRole?specialty=http://snomed.info/sct|394814009"

# Active roles
curl "http://localhost:8080/baseR4/PractitionerRole?active=true"

# Combined: active roles at specific organization
curl "http://localhost:8080/baseR4/PractitionerRole?organization=Organization/456&active=true"
```

### With _include

```bash
# Include practitioner
curl "http://localhost:8080/baseR4/PractitionerRole?_include=PractitionerRole:practitioner"

# Include organization
curl "http://localhost:8080/baseR4/PractitionerRole?_include=PractitionerRole:organization"

# Include location
curl "http://localhost:8080/baseR4/PractitionerRole?_include=PractitionerRole:location"
```

## Role Codes

| Code | Display |
|------|---------|
| doctor | Doctor |
| nurse | Nurse |
| pharmacist | Pharmacist |
| researcher | Researcher |
| teacher | Teacher/Educator |
| ict | ICT Professional |

## Common Specialties (SNOMED CT)

| Code | Display |
|------|---------|
| 394814009 | General practice |
| 394802001 | General medicine |
| 394579002 | Cardiology |
| 394585009 | Obstetrics and gynecology |
| 394537008 | Pediatrics |
| 394576009 | Surgery |
