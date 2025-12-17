# _sort Parameter

## Overview

The `_sort` parameter controls the order of search results. It allows sorting by any search parameter defined for the resource type, with support for ascending and descending order.

## FHIR Specification

- [Sorting](https://hl7.org/fhir/search.html#_sort) - FHIR Search Sort Parameter

## Syntax

```
_sort=[- ]<search_param>[,<search_param>]...
```

- Prefix with `-` for descending order (default is ascending)
- Separate multiple sort fields with commas
- Sort fields are applied in order (primary, secondary, etc.)

## Examples

### Basic Sorting

```bash
# Sort patients by birthdate (ascending - oldest first)
curl "http://localhost:8080/baseR4/Patient?_sort=birthdate"

# Sort patients by birthdate (descending - youngest first)
curl "http://localhost:8080/baseR4/Patient?_sort=-birthdate"

# Sort patients by family name (alphabetically)
curl "http://localhost:8080/baseR4/Patient?_sort=family"
```

### Multiple Sort Fields

```bash
# Sort by birthdate, then by family name for same dates
curl "http://localhost:8080/baseR4/Patient?_sort=birthdate,family"

# Sort by gender ascending, then by birthdate descending
curl "http://localhost:8080/baseR4/Patient?_sort=gender,-birthdate"
```

### Sorting Different Resource Types

```bash
# Sort observations by date (newest first)
curl "http://localhost:8080/baseR4/Observation?_sort=-date"

# Sort conditions by onset date
curl "http://localhost:8080/baseR4/Condition?_sort=onset-date"

# Sort encounters by date (most recent first)
curl "http://localhost:8080/baseR4/Encounter?_sort=-date"
```

### Combining with Search Parameters

```bash
# Find all conditions for a patient, sorted by onset date
curl "http://localhost:8080/baseR4/Condition?patient=Patient/123&_sort=-onset-date"

# Find all female patients, sorted by age (oldest first)
curl "http://localhost:8080/baseR4/Patient?gender=female&_sort=birthdate"
```

## Supported Sort Parameters

You can sort by any search parameter defined for the resource type. Common examples:

| Resource | Sort Parameters |
|----------|----------------|
| Patient | `_id`, `_lastUpdated`, `birthdate`, `family`, `given`, `name`, `gender` |
| Observation | `_id`, `_lastUpdated`, `date`, `code`, `status` |
| Condition | `_id`, `_lastUpdated`, `onset-date`, `code`, `clinical-status` |
| Encounter | `_id`, `_lastUpdated`, `date`, `status`, `class` |
| MedicationRequest | `_id`, `_lastUpdated`, `authoredon`, `status` |

## Special Sort Fields

- `_id` - Sort by resource ID
- `_lastUpdated` - Sort by last modification time

## Behavior Notes

- **Null values**: Resources with missing values for the sort field are placed at the end
- **Case sensitivity**: String sorting is case-insensitive
- **Date formats**: All date formats (date, dateTime, instant) are handled correctly
- **Complex types**: For fields like `name`, the first value in the array is used for sorting

## Example Response

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 3,
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "oldest",
        "birthDate": "1950-01-15"
      }
    },
    {
      "resource": {
        "resourceType": "Patient",
        "id": "middle",
        "birthDate": "1980-06-20"
      }
    },
    {
      "resource": {
        "resourceType": "Patient",
        "id": "youngest",
        "birthDate": "2000-12-25"
      }
    }
  ]
}
```
