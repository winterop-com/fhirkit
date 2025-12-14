# CodeSystem

## Overview

The CodeSystem resource represents a code system, which is a set of codes and their meanings. Code systems provide the vocabulary used in coded elements across FHIR resources.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/codesystem.html](https://hl7.org/fhir/R4/codesystem.html)

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
| `purpose` | markdown | Why defined |
| `copyright` | markdown | Copyright information |
| `caseSensitive` | boolean | Case sensitive codes |
| `valueSet` | canonical | Value set with all codes |
| `hierarchyMeaning` | code | How hierarchy is interpreted |
| `compositional` | boolean | Supports post-coordination |
| `versionNeeded` | boolean | Version in code display |
| `content` | code | not-present, example, fragment, complete, supplement |
| `supplements` | canonical | CodeSystem this supplements |
| `count` | unsignedInt | Total concept count |
| `filter` | BackboneElement[] | Filter properties |
| `property` | BackboneElement[] | Additional properties |
| `concept` | BackboneElement[] | Concepts in the code system |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=cs-001` |
| `identifier` | token | Business identifier | `identifier=http://example.org/cs` |
| `url` | uri | Canonical URL | `url=http://snomed.info/sct` |
| `version` | token | Version | `version=1.0.0` |
| `name` | string | Computer name | `name=SNOMEDCT` |
| `title` | string | Human name | `title=SNOMED CT` |
| `status` | token | Publication status | `status=active` |
| `publisher` | string | Publisher | `publisher=IHTSDO` |
| `description` | string | Description | `description=clinical` |
| `code` | token | Code in system | `code=386661006` |
| `content-mode` | token | Content type | `content-mode=complete` |
| `system` | uri | System URL | `system=http://snomed.info/sct` |

## Examples

### Create a CodeSystem

```bash
curl -X POST http://localhost:8080/baseR4/CodeSystem \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CodeSystem",
    "url": "http://example.org/fhir/CodeSystem/priority-codes",
    "version": "1.0.0",
    "name": "PriorityCodes",
    "title": "Priority Codes",
    "status": "active",
    "experimental": false,
    "date": "2024-01-01",
    "publisher": "Example Organization",
    "description": "Priority levels for clinical tasks",
    "caseSensitive": true,
    "content": "complete",
    "count": 4,
    "concept": [
      {
        "code": "stat",
        "display": "STAT",
        "definition": "Immediate priority, requiring action right away"
      },
      {
        "code": "urgent",
        "display": "Urgent",
        "definition": "High priority, requiring action soon"
      },
      {
        "code": "routine",
        "display": "Routine",
        "definition": "Normal priority"
      },
      {
        "code": "elective",
        "display": "Elective",
        "definition": "Low priority, can be scheduled"
      }
    ]
  }'
```

### Search CodeSystems

```bash
# By URL
curl "http://localhost:8080/baseR4/CodeSystem?url=http://example.org/fhir/CodeSystem/priority-codes"

# By status
curl "http://localhost:8080/baseR4/CodeSystem?status=active"

# By name
curl "http://localhost:8080/baseR4/CodeSystem?name=PriorityCodes"

# By content mode
curl "http://localhost:8080/baseR4/CodeSystem?content-mode=complete"
```

### Lookup Code

```bash
# Lookup a code in a code system
curl "http://localhost:8080/baseR4/CodeSystem/$lookup?system=http://snomed.info/sct&code=386661006"
```

## Status Codes

| Code | Display |
|------|---------|
| draft | Draft |
| active | Active |
| retired | Retired |
| unknown | Unknown |

## Content Modes

| Code | Display | Description |
|------|---------|-------------|
| not-present | Not Present | Content not included |
| example | Example | Only example codes |
| fragment | Fragment | Partial content |
| complete | Complete | All codes included |
| supplement | Supplement | Supplements another system |

## Common Code Systems

| URL | Name |
|-----|------|
| http://snomed.info/sct | SNOMED CT |
| http://loinc.org | LOINC |
| http://hl7.org/fhir/sid/icd-10 | ICD-10 |
| http://www.ama-assn.org/go/cpt | CPT |
| http://www.nlm.nih.gov/research/umls/rxnorm | RxNorm |
| http://unitsofmeasure.org | UCUM |
