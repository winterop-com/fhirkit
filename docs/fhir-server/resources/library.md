# Library

## Overview

The Library resource represents a shareable library of clinical knowledge, most commonly CQL (Clinical Quality Language) logic. Libraries are referenced by Measures and can contain embedded CQL or reference external CQL files.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/library.html](https://hl7.org/fhir/R4/library.html)

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
| `subtitle` | string | Subordinate title |
| `status` | code | draft, active, retired, unknown |
| `experimental` | boolean | For testing purposes |
| `type` | CodeableConcept | logic-library, model-definition, asset-collection, module-definition |
| `subjectCodeableConcept` | CodeableConcept | Subject type |
| `subjectReference` | Reference(Group) | Subject reference |
| `date` | dateTime | Publication date |
| `publisher` | string | Publisher name |
| `contact` | ContactDetail[] | Contact details |
| `description` | markdown | Natural language description |
| `useContext` | UsageContext[] | Usage context |
| `jurisdiction` | CodeableConcept[] | Intended jurisdiction |
| `purpose` | markdown | Why defined |
| `usage` | string | How to use |
| `copyright` | markdown | Copyright information |
| `approvalDate` | date | Approval date |
| `lastReviewDate` | date | Last review date |
| `effectivePeriod` | Period | When effective |
| `topic` | CodeableConcept[] | Topics |
| `author` | ContactDetail[] | Authors |
| `editor` | ContactDetail[] | Editors |
| `reviewer` | ContactDetail[] | Reviewers |
| `endorser` | ContactDetail[] | Endorsers |
| `relatedArtifact` | RelatedArtifact[] | Related resources |
| `parameter` | ParameterDefinition[] | Parameters |
| `dataRequirement` | DataRequirement[] | Required data |
| `content` | Attachment[] | Library content (CQL, ELM) |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=lib-001` |
| `identifier` | token | Business identifier | `identifier=LIB-12345` |
| `url` | uri | Canonical URL | `url=http://example.org/Library/DiabetesLogic` |
| `version` | token | Version | `version=1.0.0` |
| `name` | string | Computer name | `name=DiabetesLogic` |
| `title` | string | Human name | `title=Diabetes Logic` |
| `status` | token | Publication status | `status=active` |
| `type` | token | Library type | `type=logic-library` |
| `publisher` | string | Publisher | `publisher=CMS` |
| `description` | string | Description | `description=diabetes` |
| `content-type` | token | Content MIME type | `content-type=text/cql` |
| `composed-of` | reference | Dependencies | `composed-of=Library/FHIRHelpers` |
| `depends-on` | reference | Dependencies | `depends-on=Library/FHIRHelpers` |
| `derived-from` | reference | Derived from | `derived-from=Library/BaseLogic` |
| `predecessor` | reference | Previous version | `predecessor=Library/DiabetesLogic-v1` |
| `successor` | reference | Next version | `successor=Library/DiabetesLogic-v3` |
| `topic` | token | Topic | `topic=diabetes` |

## Examples

### Create a CQL Library

```bash
curl -X POST http://localhost:8080/baseR4/Library \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Library",
    "url": "http://example.org/fhir/Library/DiabetesLogic",
    "version": "1.0.0",
    "name": "DiabetesLogic",
    "title": "Diabetes Quality Measure Logic",
    "status": "active",
    "experimental": false,
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/library-type",
        "code": "logic-library",
        "display": "Logic Library"
      }]
    },
    "date": "2024-01-01",
    "publisher": "Example Organization",
    "description": "CQL logic for diabetes quality measures",
    "relatedArtifact": [{
      "type": "depends-on",
      "resource": "Library/FHIRHelpers"
    }],
    "parameter": [
      {
        "name": "Patient",
        "use": "in",
        "type": "Patient"
      },
      {
        "name": "Measurement Period",
        "use": "in",
        "type": "Period"
      }
    ],
    "dataRequirement": [
      {
        "type": "Condition",
        "codeFilter": [{
          "path": "code",
          "valueSet": "http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.103.12.1001"
        }]
      },
      {
        "type": "Observation",
        "codeFilter": [{
          "path": "code",
          "code": [{"system": "http://loinc.org", "code": "4548-4"}]
        }]
      }
    ],
    "content": [{
      "contentType": "text/cql",
      "data": "bGlicmFyeSBEaWFiZXRlc0xvZ2ljIHZlcnNpb24gJzEuMC4wJw=="
    }]
  }'
```

### Create with External CQL Reference

```bash
curl -X POST http://localhost:8080/baseR4/Library \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Library",
    "url": "http://example.org/fhir/Library/ExternalCQL",
    "version": "1.0.0",
    "name": "ExternalCQL",
    "title": "External CQL Library",
    "status": "active",
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/library-type",
        "code": "logic-library"
      }]
    },
    "content": [{
      "contentType": "text/cql",
      "url": "http://example.org/cql/ExternalCQL.cql"
    }]
  }'
```

### Search Libraries

```bash
# By URL
curl "http://localhost:8080/baseR4/Library?url=http://example.org/fhir/Library/DiabetesLogic"

# By status
curl "http://localhost:8080/baseR4/Library?status=active"

# By type
curl "http://localhost:8080/baseR4/Library?type=logic-library"

# By name
curl "http://localhost:8080/baseR4/Library?name=DiabetesLogic"

# By content type
curl "http://localhost:8080/baseR4/Library?content-type=text/cql"
```

## Library Types

| Code | Display | Description |
|------|---------|-------------|
| logic-library | Logic Library | CQL or other executable logic |
| model-definition | Model Definition | Data model definition |
| asset-collection | Asset Collection | Collection of knowledge assets |
| module-definition | Module Definition | Defines a CDS module |

## Content Types

| MIME Type | Description |
|-----------|-------------|
| text/cql | CQL source code |
| application/elm+json | ELM JSON format |
| application/elm+xml | ELM XML format |

## Integration with Measures

Libraries are referenced by Measure resources to provide the evaluation logic:

```json
{
  "resourceType": "Measure",
  "library": ["http://example.org/fhir/Library/DiabetesLogic"],
  "group": [{
    "population": [{
      "code": {"coding": [{"code": "initial-population"}]},
      "criteria": {
        "language": "text/cql",
        "expression": "Initial Population"
      }
    }]
  }]
}
```

## CQL Content Example

The `content` attachment typically contains base64-encoded CQL:

```cql
library DiabetesLogic version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Has Diabetes":
  exists([Condition: "Diabetes"] C
    where C.clinicalStatus ~ "active")

define "HbA1c Tests":
  [Observation: "HbA1c Laboratory Test"] O
    where O.status = 'final'
      and O.effective in "Measurement Period"
```
