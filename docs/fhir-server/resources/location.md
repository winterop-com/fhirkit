# Location

## Overview

The Location resource describes physical places where healthcare services are provided. This includes hospitals, clinics, rooms, beds, and mobile units.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/location.html](https://hl7.org/fhir/R4/location.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | Business identifiers |
| `status` | code | active, suspended, inactive |
| `operationalStatus` | Coding | Operational status |
| `name` | string | Location name |
| `alias` | string[] | Alternative names |
| `description` | string | Additional details |
| `mode` | code | instance or kind |
| `type` | CodeableConcept[] | Type of location |
| `telecom` | ContactPoint[] | Contact information |
| `address` | Address | Physical address |
| `physicalType` | CodeableConcept | Physical form (building, room, etc.) |
| `position` | BackboneElement | GPS coordinates |
| `managingOrganization` | Reference(Organization) | Managing organization |
| `partOf` | Reference(Location) | Parent location |
| `hoursOfOperation` | BackboneElement[] | Hours of operation |
| `availabilityExceptions` | string | Exceptions to hours |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=loc-001` |
| `identifier` | token | Business identifier | `identifier=LOC-12345` |
| `name` | string | Location name | `name=Main` |
| `status` | token | Location status | `status=active` |
| `type` | token | Location type | `type=HOSP` |
| `address` | string | Any address field | `address=Boston` |
| `address-city` | string | City | `address-city=Boston` |
| `address-state` | string | State | `address-state=MA` |
| `address-postalcode` | string | Postal code | `address-postalcode=02115` |
| `address-country` | string | Country | `address-country=USA` |
| `operational-status` | token | Operational status | `operational-status=O` |
| `organization` | reference | Managing organization | `organization=Organization/123` |
| `partof` | reference | Parent location | `partof=Location/456` |

## Examples

### Create a Location

```bash
curl -X POST http://localhost:8080/baseR4/Location \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Location",
    "status": "active",
    "operationalStatus": {
      "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
      "code": "O",
      "display": "Occupied"
    },
    "name": "General Hospital - Main Building",
    "alias": ["Main Hospital", "GH Main"],
    "description": "Main hospital building with emergency and inpatient facilities",
    "mode": "instance",
    "type": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
        "code": "HOSP",
        "display": "Hospital"
      }]
    }],
    "telecom": [
      {"system": "phone", "value": "555-123-4567", "use": "work"},
      {"system": "fax", "value": "555-123-4568", "use": "work"}
    ],
    "address": {
      "use": "work",
      "type": "physical",
      "line": ["123 Medical Center Drive"],
      "city": "Boston",
      "state": "MA",
      "postalCode": "02115",
      "country": "USA"
    },
    "physicalType": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
        "code": "bu",
        "display": "Building"
      }]
    },
    "position": {
      "longitude": -71.0892,
      "latitude": 42.3370
    },
    "managingOrganization": {
      "reference": "Organization/organization-001",
      "display": "General Hospital"
    },
    "hoursOfOperation": [{
      "daysOfWeek": ["mon", "tue", "wed", "thu", "fri"],
      "allDay": false,
      "openingTime": "08:00:00",
      "closingTime": "20:00:00"
    }]
  }'
```

### Search Locations

```bash
# By name
curl "http://localhost:8080/baseR4/Location?name=Main"

# By status
curl "http://localhost:8080/baseR4/Location?status=active"

# By type
curl "http://localhost:8080/baseR4/Location?type=http://terminology.hl7.org/CodeSystem/v3-RoleCode|HOSP"

# By city
curl "http://localhost:8080/baseR4/Location?address-city=Boston"

# By managing organization
curl "http://localhost:8080/baseR4/Location?organization=Organization/123"
```

### With _include

```bash
# Include managing organization
curl "http://localhost:8080/baseR4/Location?_include=Location:organization"

# Include parent location
curl "http://localhost:8080/baseR4/Location?_include=Location:partof"
```

## Location Status

| Code | Display |
|------|---------|
| active | Active |
| suspended | Suspended |
| inactive | Inactive |

## Location Mode

| Code | Display | Description |
|------|---------|-------------|
| instance | Instance | A specific location instance |
| kind | Kind | A class of locations |

## Location Types (v3-RoleCode)

| Code | Display |
|------|---------|
| HOSP | Hospital |
| PTRES | Patient Residence |
| PROFF | Provider Office |
| ER | Emergency Room |
| ICU | Intensive Care Unit |
| PEDU | Pediatric Unit |
| PHU | Psychiatric Hospital Unit |
| RHU | Rehabilitation Hospital Unit |
| HLAB | Hospital Laboratory |
| PHARM | Pharmacy |

## Physical Types

| Code | Display |
|------|---------|
| si | Site |
| bu | Building |
| wi | Wing |
| wa | Ward |
| lvl | Level |
| co | Corridor |
| ro | Room |
| bd | Bed |
| ve | Vehicle |
| ho | House |
| ca | Cabinet |
| rd | Road |
| area | Area |
