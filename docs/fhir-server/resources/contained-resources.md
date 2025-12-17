# Contained Resources

## Overview

Contained resources are resources that are fully nested within another resource. They are used when a referenced resource doesn't have an independent existence and only makes sense in the context of the containing resource.

## FHIR Specification

- [Contained Resources](https://hl7.org/fhir/R4/references.html#contained) - FHIR R4 Contained Resources
- [Internal References](https://hl7.org/fhir/R4/references.html#contained) - Using #id references

## Structure

```json
{
  "resourceType": "MedicationRequest",
  "id": "example",
  "contained": [
    {
      "resourceType": "Medication",
      "id": "med1",
      "code": {
        "coding": [{
          "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
          "code": "1049502",
          "display": "Aspirin 325 MG"
        }]
      }
    }
  ],
  "medicationReference": {
    "reference": "#med1"
  },
  "status": "active",
  "intent": "order",
  "subject": {"reference": "Patient/123"}
}
```

## Rules

### Contained Resource Requirements

1. **Must have `id`**: Each contained resource must have a local ID
2. **Must have `resourceType`**: Each contained resource must specify its type
3. **Unique IDs**: IDs must be unique within the containing resource
4. **No nested contained**: Contained resources cannot themselves have contained resources

### Internal References

- References to contained resources use `#id` format
- The `#` prefix indicates an internal reference
- All `#id` references must point to existing contained resources

## Validation

The server validates contained resources on create and update:

| Check | Error |
|-------|-------|
| Missing resourceType | "Contained resource at index N missing resourceType" |
| Missing id | "Contained Medication at index N missing id" |
| Duplicate IDs | "Duplicate contained resource id: med1" |
| Invalid reference | "Internal reference '#med2' not found in contained resources" |

## CRUD Operations

### Create with Contained

```bash
curl -X POST http://localhost:8080/baseR4/MedicationRequest \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MedicationRequest",
    "status": "active",
    "intent": "order",
    "contained": [{
      "resourceType": "Medication",
      "id": "med1",
      "code": {"text": "Aspirin"}
    }],
    "medicationReference": {"reference": "#med1"},
    "subject": {"reference": "Patient/123"}
  }'
```

### Update with Contained

```bash
curl -X PUT http://localhost:8080/baseR4/MedicationRequest/123 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MedicationRequest",
    "id": "123",
    "status": "active",
    "intent": "order",
    "contained": [{
      "resourceType": "Medication",
      "id": "med1",
      "code": {"text": "Updated Medication"}
    }],
    "medicationReference": {"reference": "#med1"},
    "subject": {"reference": "Patient/123"}
  }'
```

### Read with Contained

```bash
curl http://localhost:8080/baseR4/MedicationRequest/123
```

Returns the full resource including contained resources.

## Search with _contained

The `_contained` parameter controls whether contained resources appear in search results:

```bash
# Default: only top-level resources (contained not returned separately)
GET /MedicationRequest

# Return only contained resources from matching containers
GET /MedicationRequest?_contained=true

# Return both top-level and contained resources
GET /MedicationRequest?_contained=both
```

## ID Normalization

Contained resource IDs are normalized:

- `#med1` becomes `med1` in storage
- References still use `#med1` format

```json
// Input
{
  "contained": [{"resourceType": "Medication", "id": "#med1"}]
}

// Stored as
{
  "contained": [{"resourceType": "Medication", "id": "med1"}]
}
```

## Common Use Cases

### Medication in MedicationRequest

```json
{
  "resourceType": "MedicationRequest",
  "contained": [{
    "resourceType": "Medication",
    "id": "med1",
    "code": {"coding": [{"code": "12345"}]}
  }],
  "medicationReference": {"reference": "#med1"}
}
```

### Practitioner in Condition

```json
{
  "resourceType": "Condition",
  "contained": [{
    "resourceType": "Practitioner",
    "id": "prac1",
    "name": [{"family": "Smith"}]
  }],
  "asserter": {"reference": "#prac1"}
}
```

### Multiple Contained Resources

```json
{
  "resourceType": "DiagnosticReport",
  "contained": [
    {"resourceType": "Observation", "id": "obs1", "status": "final"},
    {"resourceType": "Observation", "id": "obs2", "status": "final"},
    {"resourceType": "Specimen", "id": "spec1"}
  ],
  "result": [
    {"reference": "#obs1"},
    {"reference": "#obs2"}
  ],
  "specimen": [{"reference": "#spec1"}]
}
```

## Python API

```python
from fhirkit.server.api.contained import (
    validate_contained_resources,
    normalize_contained_ids,
    resolve_contained_reference,
    add_contained_resource,
    remove_contained_resource,
    create_internal_reference,
)

# Validate contained resources
issues = validate_contained_resources(resource)
if issues:
    print(f"Validation errors: {issues}")

# Normalize IDs (remove # prefix)
normalized = normalize_contained_ids(resource)

# Resolve internal reference
medication = resolve_contained_reference(resource, "#med1")

# Add contained resource
resource, contained_id = add_contained_resource(
    resource,
    {"resourceType": "Medication", "id": "med1"},
)

# Create reference to contained
ref = create_internal_reference("med1")  # {"reference": "#med1"}

# Remove contained (fails if still referenced)
resource = remove_contained_resource(resource, "med1")
```

## Error Handling

### Missing ID

```bash
curl -X POST http://localhost:8080/baseR4/MedicationRequest \
  -d '{"resourceType": "MedicationRequest", "contained": [{"resourceType": "Medication"}]}'
```

Response (400):
```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "invalid",
    "diagnostics": "Invalid contained resources: Contained Medication at index 0 missing id"
  }]
}
```

### Invalid Reference

```bash
curl -X POST http://localhost:8080/baseR4/MedicationRequest \
  -d '{
    "resourceType": "MedicationRequest",
    "contained": [{"resourceType": "Medication", "id": "med1"}],
    "medicationReference": {"reference": "#med2"}
  }'
```

Response (400):
```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "invalid",
    "diagnostics": "Invalid contained resources: Internal reference '#med2' not found in contained resources"
  }]
}
```

## Best Practices

1. **Use contained when the referenced resource has no independent identity**
2. **Keep contained resources simple** - avoid deeply nested structures
3. **Validate references** - ensure all #id references point to valid contained resources
4. **Consider standalone resources** - if the resource might be referenced elsewhere, don't contain it
5. **Use meaningful IDs** - like "med1", "prac1" rather than random strings
