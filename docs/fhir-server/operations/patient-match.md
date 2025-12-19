# Patient $match Operation

## Overview

The `$match` operation finds patients that match a given patient resource using weighted field comparison. This is useful for patient deduplication and Master Patient Index (MPI) implementations.

**FHIR Specification**: https://hl7.org/fhir/R4/patient-operation-match.html

## Endpoint

```
POST /Patient/$match
```

## Request

Submit a Parameters resource containing the patient to match:

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "resource",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Smith", "given": ["John"]}],
        "birthDate": "1970-01-15",
        "gender": "male",
        "telecom": [{"system": "phone", "value": "555-123-4567"}],
        "address": [{"postalCode": "12345"}]
      }
    },
    {
      "name": "count",
      "valueInteger": 10
    },
    {
      "name": "onlyCertainMatches",
      "valueBoolean": false
    }
  ]
}
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resource` | Patient | required | Patient resource to match against |
| `count` | integer | 10 | Maximum matches to return |
| `onlyCertainMatches` | boolean | false | Only return certain matches (score >= 0.95) |

## Response

Returns a searchset Bundle with matching patients and scores:

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 2,
  "entry": [
    {
      "fullUrl": "Patient/patient-123",
      "resource": {
        "resourceType": "Patient",
        "id": "patient-123",
        "name": [{"family": "Smith", "given": ["John"]}],
        "birthDate": "1970-01-15"
      },
      "search": {
        "mode": "match",
        "score": 0.92,
        "extension": [
          {
            "url": "http://hl7.org/fhir/StructureDefinition/match-grade",
            "valueCode": "probable"
          }
        ]
      }
    }
  ]
}
```

## Match Scoring

### Field Weights

| Field | Weight | Description |
|-------|--------|-------------|
| `identifier` | 100 | Exact match = 100% score immediately |
| `name.family` | 30 | Family name |
| `name.given` | 20 | Given name(s) |
| `birthDate` | 25 | Date of birth |
| `gender` | 5 | Gender |
| `telecom.phone` | 15 | Phone number |
| `telecom.email` | 15 | Email address |
| `address.postalCode` | 10 | Postal/ZIP code |
| `address.line` | 5 | Street address |

### Match Grades

| Grade | Score Threshold | Description |
|-------|-----------------|-------------|
| `certain` | >= 0.95 | Almost certainly the same patient |
| `probable` | >= 0.80 | Likely the same patient |
| `possible` | >= 0.60 | Possibly the same patient |
| `certainly-not` | < 0.60 | Not a match |

## Matching Algorithm

1. **Identifier Match**: If any identifier matches exactly (same system + value), score is 1.0
2. **Field Comparison**: Each field is compared and weighted
3. **Name Matching**: Supports fuzzy matching for typos and nicknames
4. **Phone Normalization**: Phone numbers are normalized (digits only) before comparison
5. **Score Calculation**: `earned_weight / total_weight`

## Examples

### Basic Match

```bash
curl -X POST http://localhost:8080/baseR4/Patient/\$match \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {
        "name": "resource",
        "resource": {
          "resourceType": "Patient",
          "name": [{"family": "Smith", "given": ["John"]}],
          "birthDate": "1970-01-15"
        }
      }
    ]
  }'
```

### Match with Identifier

```bash
curl -X POST http://localhost:8080/baseR4/Patient/\$match \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {
        "name": "resource",
        "resource": {
          "resourceType": "Patient",
          "identifier": [{"system": "http://hospital.org/mrn", "value": "12345"}]
        }
      }
    ]
  }'
```

### Only Certain Matches

```bash
curl -X POST http://localhost:8080/baseR4/Patient/\$match \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {
        "name": "resource",
        "resource": {
          "resourceType": "Patient",
          "name": [{"family": "Smith"}],
          "birthDate": "1970-01-15",
          "identifier": [{"system": "http://hospital.org/mrn", "value": "12345"}]
        }
      },
      {
        "name": "onlyCertainMatches",
        "valueBoolean": true
      }
    ]
  }'
```

## Use Cases

1. **Patient Registration**: Check for existing records before creating new patient
2. **HIE Integration**: Match incoming patient data to local records
3. **Deduplication**: Find and merge duplicate patient records
4. **Record Linking**: Link records across different systems

## Notes

- Self-matching is excluded (patients don't match themselves)
- Fuzzy name matching uses character overlap algorithm
- Results are sorted by score (highest first)
- Empty or null fields don't contribute to scoring
