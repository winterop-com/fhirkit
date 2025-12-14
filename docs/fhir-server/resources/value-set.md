# ValueSet

## Overview

The ValueSet resource represents a set of codes from one or more code systems that can be used in a particular context. ValueSets define collections of values for use in coded elements.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/valueset.html](https://hl7.org/fhir/R4/valueset.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `url` | uri | Canonical identifier |
| `identifier` | Identifier[] | Business identifiers |
| `version` | string | Version |
| `name` | string | Computer-friendly name |
| `title` | string | Human-friendly name |
| `status` | code | draft, active, retired, unknown |
| `experimental` | boolean | For testing purposes |
| `date` | dateTime | Publication date |
| `publisher` | string | Publisher name |
| `contact` | ContactDetail[] | Contact details |
| `description` | markdown | Natural language description |
| `useContext` | UsageContext[] | Usage context |
| `jurisdiction` | CodeableConcept[] | Intended jurisdiction |
| `immutable` | boolean | Whether content is fixed |
| `purpose` | markdown | Why defined |
| `copyright` | markdown | Copyright information |
| `compose` | BackboneElement | Content definition |
| `expansion` | BackboneElement | Expanded value set |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=vs-001` |
| `identifier` | token | Business identifier | `identifier=http://example.org/vs` |
| `url` | uri | Canonical URL | `url=http://hl7.org/fhir/ValueSet/condition-severity` |
| `version` | token | Version | `version=1.0.0` |
| `name` | string | Computer name | `name=ConditionSeverity` |
| `title` | string | Human name | `title=Condition Severity` |
| `status` | token | Publication status | `status=active` |
| `publisher` | string | Publisher | `publisher=HL7` |
| `description` | string | Description | `description=severity` |
| `code` | token | Code in value set | `code=severe` |
| `reference` | uri | Code system reference | `reference=http://snomed.info/sct` |

## Examples

### Create a ValueSet

```bash
curl -X POST http://localhost:8080/baseR4/ValueSet \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ValueSet",
    "url": "http://example.org/fhir/ValueSet/condition-severity",
    "version": "1.0.0",
    "name": "ConditionSeverity",
    "title": "Condition Severity",
    "status": "active",
    "experimental": false,
    "date": "2024-01-01",
    "publisher": "Example Organization",
    "description": "Severity levels for conditions",
    "compose": {
      "include": [{
        "system": "http://snomed.info/sct",
        "concept": [
          {"code": "24484000", "display": "Severe"},
          {"code": "6736007", "display": "Moderate"},
          {"code": "255604002", "display": "Mild"}
        ]
      }]
    }
  }'
```

### Search ValueSets

```bash
# By URL
curl "http://localhost:8080/baseR4/ValueSet?url=http://example.org/fhir/ValueSet/condition-severity"

# By status
curl "http://localhost:8080/baseR4/ValueSet?status=active"

# By name
curl "http://localhost:8080/baseR4/ValueSet?name=ConditionSeverity"

# By publisher
curl "http://localhost:8080/baseR4/ValueSet?publisher=HL7"
```

### Expand ValueSet

```bash
# Expand a specific value set
curl "http://localhost:8080/baseR4/ValueSet/vs-001/$expand"

# Expand by URL
curl "http://localhost:8080/baseR4/ValueSet/$expand?url=http://example.org/fhir/ValueSet/condition-severity"
```

## Status Codes

| Code | Display |
|------|---------|
| draft | Draft |
| active | Active |
| retired | Retired |
| unknown | Unknown |

## Common ValueSets

| URL | Description |
|-----|-------------|
| http://hl7.org/fhir/ValueSet/condition-severity | Condition severity |
| http://hl7.org/fhir/ValueSet/observation-status | Observation status |
| http://hl7.org/fhir/ValueSet/administrative-gender | Gender codes |
| http://hl7.org/fhir/ValueSet/encounter-status | Encounter status |
| http://hl7.org/fhir/ValueSet/medication-status | Medication status |
