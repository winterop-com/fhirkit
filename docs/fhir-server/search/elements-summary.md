# _elements and _summary Search Parameters

## Overview

The `_elements` and `_summary` parameters allow clients to control which elements are returned in search results, reducing payload size and improving performance.

## FHIR Specification

- [_elements](https://hl7.org/fhir/R4/search.html#elements) - Return only specified elements
- [_summary](https://hl7.org/fhir/R4/search.html#summary) - Return summary views

## _elements Parameter

The `_elements` parameter specifies which elements to include in the returned resources.

### Usage

```bash
GET /Patient?_elements=name,birthDate,gender
```

### Behavior

- Elements are specified as a comma-separated list
- The following elements are **always included** regardless of the parameter:
  - `resourceType`
  - `id`
  - `meta` (if present)
- Only top-level elements can be specified
- If an element doesn't exist in a resource, it's simply not included
- Applies to both primary results and included resources (`_include`, `_revinclude`)

### Examples

```bash
# Return only name and birthDate
curl "http://localhost:8000/Patient?_elements=name,birthDate"

# Return identifier and code for Conditions
curl "http://localhost:8000/Condition?_elements=identifier,code,subject"

# Combine with other search parameters
curl "http://localhost:8000/Observation?code=4548-4&_elements=value,effectiveDateTime"
```

## _summary Parameter

The `_summary` parameter returns predefined views of resources.

### Values

| Value | Description |
|-------|-------------|
| `true` | Return summary elements only (resource-type specific) |
| `text` | Return only `id`, `meta`, and `text` narrative |
| `data` | Return all elements except `text` narrative |
| `count` | Return only the total count, no entries |
| `false` | Return full resources (default behavior) |

### Summary Elements by Resource Type

When `_summary=true`, the following elements are included:

| Resource Type | Summary Elements |
|--------------|------------------|
| Patient | identifier, active, name, telecom, gender, birthDate, address |
| Condition | identifier, clinicalStatus, verificationStatus, code, subject, onsetDateTime |
| Observation | identifier, status, category, code, subject, effectiveDateTime, valueQuantity |
| Encounter | identifier, status, class, type, subject, period |
| MedicationRequest | identifier, status, intent, medicationCodeableConcept, subject, authoredOn |
| Procedure | identifier, status, code, subject, performedDateTime, performedPeriod |

### Examples

```bash
# Summary view
curl "http://localhost:8000/Patient?_summary=true"

# Count only - useful for checking how many resources match
curl "http://localhost:8000/Condition?patient=Patient/123&_summary=count"

# Data without text narrative (for systems that don't display narrative)
curl "http://localhost:8000/Observation?_summary=data"

# Text narrative only
curl "http://localhost:8000/Patient?_id=123&_summary=text"
```

### _summary=count Response

When using `_summary=count`, the response contains only the bundle total:

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 42
}
```

## Supported Endpoints

Both parameters are supported on:

- **Type search**: `GET /Patient?_elements=name`
- **Compartment search**: `GET /Patient/123/Condition?_summary=true`
- **Patient $everything**: `GET /Patient/123/$everything?_elements=code,name`

## Combining with Other Parameters

These parameters can be combined with:

- **Pagination**: `?_elements=name&_count=10&_offset=20`
- **Sorting**: `?_elements=name,birthDate&_sort=-birthDate`
- **_include/_revinclude**: `?_include=Condition:subject&_elements=code,name`
- **Standard search params**: `?code=12345&_summary=true`

### Example with _include

```bash
# Get conditions with patient references, filtered to essential fields
curl "http://localhost:8000/Condition?_include=Condition:subject&_elements=code,clinicalStatus,name,birthDate"
```

Both the Condition resources and the included Patient resources will be filtered to include only the specified elements.

## Performance Benefits

Using these parameters can significantly improve performance:

1. **Reduced payload size** - Only transfer needed data
2. **Faster serialization** - Less data to serialize/deserialize
3. **Lower bandwidth** - Smaller network transfers
4. **Quick counts** - `_summary=count` for checking existence without fetching data

## Notes

- `_elements` and `_summary` should not be used together (per FHIR spec)
- The `text` element is a narrative summary, distinct from `_summary=text`
- When both parameters could apply, `_summary=count` takes precedence
