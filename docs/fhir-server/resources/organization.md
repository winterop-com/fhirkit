# Organization

## Overview

The Organization resource represents a formally or informally recognized grouping of people or organizations formed for the purpose of achieving some form of collective action. This includes healthcare providers, insurers, government agencies, and other entities involved in healthcare.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/organization.html](https://hl7.org/fhir/R4/organization.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier[] | NPI, tax ID, etc. |
| `active` | boolean | Whether organization is active |
| `type` | CodeableConcept[] | Organization type |
| `name` | string | Organization name |
| `alias` | string[] | Alternative names |
| `telecom` | ContactPoint[] | Contact information |
| `address` | Address[] | Physical addresses |
| `partOf` | Reference(Organization) | Parent organization |
| `contact` | BackboneElement[] | Contact persons |
| `endpoint` | Reference(Endpoint)[] | Technical endpoints |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=org-001` |
| `identifier` | token | NPI or other identifier | `identifier=NPI\|1234567890` |
| `name` | string | Organization name | `name=General` |
| `active` | token | Active status | `active=true` |
| `type` | token | Organization type | `type=prov` |
| `address` | string | Any address field | `address=Boston` |
| `address-city` | string | City | `address-city=Boston` |
| `address-state` | string | State | `address-state=MA` |

## Examples

### Create an Organization

```bash
curl -X POST http://localhost:8080/baseR4/Organization \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Organization",
    "identifier": [{
      "system": "http://hl7.org/fhir/sid/us-npi",
      "value": "1234567890"
    }],
    "active": true,
    "type": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
        "code": "prov",
        "display": "Healthcare Provider"
      }]
    }],
    "name": "General Hospital",
    "alias": ["GH", "General"],
    "telecom": [
      {"system": "phone", "value": "555-123-4567", "use": "work"},
      {"system": "fax", "value": "555-123-4568", "use": "work"},
      {"system": "email", "value": "info@generalhospital.org"}
    ],
    "address": [{
      "use": "work",
      "type": "physical",
      "line": ["123 Medical Center Drive"],
      "city": "Boston",
      "state": "MA",
      "postalCode": "02115",
      "country": "USA"
    }],
    "contact": [{
      "purpose": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/contactentity-type",
          "code": "ADMIN",
          "display": "Administrative"
        }]
      },
      "name": {"text": "John Administrator"},
      "telecom": [{"system": "phone", "value": "555-123-4569"}]
    }]
  }'
```

### Search Organizations

```bash
# By name
curl "http://localhost:8080/baseR4/Organization?name=General"

# By type
curl "http://localhost:8080/baseR4/Organization?type=prov"

# By city
curl "http://localhost:8080/baseR4/Organization?address-city=Boston"

# Active organizations
curl "http://localhost:8080/baseR4/Organization?active=true"

# Combined: active providers in Boston
curl "http://localhost:8080/baseR4/Organization?type=prov&active=true&address-city=Boston"
```

### With _revinclude

```bash
# Include practitioners at organization
curl "http://localhost:8080/baseR4/Organization?_revinclude=PractitionerRole:organization"

# Include locations managed by organization
curl "http://localhost:8080/baseR4/Organization?_revinclude=Location:organization"
```

## Organization Types

| Code | Display |
|------|---------|
| prov | Healthcare Provider |
| dept | Hospital Department |
| team | Organizational Team |
| govt | Government |
| ins | Insurance Company |
| pay | Payer |
| edu | Educational Institute |
| reli | Religious Institution |
| crs | Clinical Research Sponsor |
| cg | Community Group |
| bus | Non-Healthcare Business or Corporation |
| other | Other |
