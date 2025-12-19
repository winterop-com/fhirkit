# $diff Operation

## Overview

The `$diff` operation compares two FHIR resources or two versions of the same resource and returns the differences as JSON Patch-style operations.

## Endpoints

### Compare Resource Versions

```
GET /{resource_type}/{resource_id}/$diff?version={version_id}
```

Compare the current version with a previous version of the same resource.

### Compare Two Resources

```
POST /{resource_type}/$diff
```

Compare two arbitrary resources of the same type.

### Patient-Specific Diff

```
GET /Patient/{patient_id}/$diff?version={version_id}
```

Compare Patient versions (available before compartment routes).

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | string | Version ID to compare against current (for GET) |
| `from` | string | Source version ID (for comparing specific versions) |
| `to` | string | Target version ID (for comparing specific versions) |

## Request (POST)

For comparing two arbitrary resources, POST a Parameters resource:

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "source",
      "resource": {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Smith"}]
      }
    },
    {
      "name": "target",
      "resource": {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Johnson"}]
      }
    }
  ]
}
```

## Response

Returns a Parameters resource containing the diff operations:

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "operation",
      "part": [
        {"name": "type", "valueCode": "replace"},
        {"name": "path", "valueString": "/name/0/family"},
        {"name": "value", "valueString": "Johnson"}
      ]
    }
  ]
}
```

## Operation Types

| Type | Description |
|------|-------------|
| `add` | New element added |
| `remove` | Element removed |
| `replace` | Element value changed |

## Examples

### Compare Patient Versions

```bash
# Get current version
curl http://localhost:8080/baseR4/Patient/patient-001

# Update the patient
curl -X PUT http://localhost:8080/baseR4/Patient/patient-001 \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType": "Patient", "id": "patient-001", "name": [{"family": "NewName"}]}'

# Compare versions
curl "http://localhost:8080/baseR4/Patient/patient-001/\$diff?version=1"
```

### Compare Two Resources

```bash
curl -X POST http://localhost:8080/baseR4/Patient/\$diff \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {
        "name": "source",
        "resource": {"resourceType": "Patient", "name": [{"family": "Smith"}]}
      },
      {
        "name": "target",
        "resource": {"resourceType": "Patient", "name": [{"family": "Jones"}]}
      }
    ]
  }'
```

## UI Integration

The diff operation is integrated into the Web UI's version history page. When viewing resource history, you can compare any two versions using the built-in diff viewer.

## Use Cases

1. **Audit Trail**: Track changes made to clinical data
2. **Merge Conflicts**: Identify differences when merging patient records
3. **Quality Control**: Review changes before approval
4. **Data Migration**: Verify data transformations

## Notes

- The diff uses JSON Patch-style operations (RFC 6902)
- Array comparisons are element-by-element (not using LCS algorithm)
- Complex nested values are serialized as JSON strings in the response
- The operation works with any supported resource type
