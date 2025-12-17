# _include and _revinclude Parameters

## Overview

The `_include` and `_revinclude` parameters allow you to retrieve related resources in a single request, reducing the number of API calls needed.

- **`_include`**: Follow references FROM search results to include related resources
- **`_revinclude`**: Find resources that REFERENCE the search results

## FHIR Specification

- [Including Referenced Resources](https://hl7.org/fhir/search.html#include) - FHIR Search Include

## Syntax

```
_include=<SourceType>:<search_param>[:<TargetType>]
_revinclude=<SourceType>:<search_param>[:<TargetType>]
```

- `SourceType`: The resource type containing the reference
- `search_param`: The search parameter representing the reference
- `TargetType`: (Optional) Filter to only include specific target types

## _include Examples

### Basic Include

```bash
# Get patients with their general practitioners
curl "http://localhost:8080/baseR4/Patient?_include=Patient:general-practitioner"

# Get conditions with the patients they reference
curl "http://localhost:8080/baseR4/Condition?_include=Condition:subject"

# Get observations with their encounters
curl "http://localhost:8080/baseR4/Observation?_include=Observation:encounter"
```

### Include with Target Type

```bash
# Get medication requests including only Patient subjects (not Groups)
curl "http://localhost:8080/baseR4/MedicationRequest?_include=MedicationRequest:subject:Patient"
```

### Multiple Includes

```bash
# Get conditions with both patients and encounters
curl "http://localhost:8080/baseR4/Condition?_include=Condition:subject&_include=Condition:encounter"
```

## _revinclude Examples

### Basic Revinclude

```bash
# Get patients with all their conditions
curl "http://localhost:8080/baseR4/Patient?_revinclude=Condition:patient"

# Get patients with all their observations
curl "http://localhost:8080/baseR4/Patient?_revinclude=Observation:patient"

# Get practitioners with encounters where they participated
curl "http://localhost:8080/baseR4/Practitioner?_revinclude=Encounter:participant"
```

### Multiple Revincludes

```bash
# Get patients with their conditions AND observations
curl "http://localhost:8080/baseR4/Patient?_revinclude=Condition:patient&_revinclude=Observation:patient"
```

## Combined _include and _revinclude

```bash
# Get patients with their practitioners AND all conditions referencing them
curl "http://localhost:8080/baseR4/Patient?_include=Patient:general-practitioner&_revinclude=Condition:patient"
```

## Response Format

The search results will include both primary results and included resources, distinguished by the `search.mode` field:

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 1,
  "entry": [
    {
      "fullUrl": "http://localhost:8080/baseR4/Patient/123",
      "resource": {
        "resourceType": "Patient",
        "id": "123",
        "name": [{"family": "Smith"}],
        "generalPractitioner": [{"reference": "Practitioner/456"}]
      },
      "search": {
        "mode": "match"
      }
    },
    {
      "fullUrl": "http://localhost:8080/baseR4/Practitioner/456",
      "resource": {
        "resourceType": "Practitioner",
        "id": "456",
        "name": [{"family": "Doctor"}]
      },
      "search": {
        "mode": "include"
      }
    },
    {
      "fullUrl": "http://localhost:8080/baseR4/Condition/789",
      "resource": {
        "resourceType": "Condition",
        "id": "789",
        "subject": {"reference": "Patient/123"},
        "code": {"text": "Diabetes"}
      },
      "search": {
        "mode": "include"
      }
    }
  ]
}
```

## Supported Reference Parameters

### Common Include Parameters

| Resource | Reference Parameters |
|----------|---------------------|
| Patient | `general-practitioner`, `organization`, `link` |
| Condition | `subject`, `patient`, `encounter`, `asserter` |
| Observation | `subject`, `patient`, `encounter`, `performer`, `device` |
| MedicationRequest | `subject`, `patient`, `encounter`, `requester`, `performer` |
| Encounter | `subject`, `patient`, `participant`, `service-provider` |
| Procedure | `subject`, `patient`, `encounter`, `performer` |
| DiagnosticReport | `subject`, `patient`, `encounter`, `performer` |
| CarePlan | `subject`, `patient`, `encounter` |
| AllergyIntolerance | `patient`, `recorder`, `asserter` |
| Immunization | `patient`, `performer` |
| DocumentReference | `subject`, `patient`, `author`, `encounter`, `custodian` |
| QuestionnaireResponse | `subject`, `patient`, `author`, `source`, `encounter` |

### Revinclude Examples

To include all resources that reference a Patient:

```bash
# All conditions for patients
Patient?_revinclude=Condition:patient

# All observations for patients
Patient?_revinclude=Observation:patient

# All medication requests for patients
Patient?_revinclude=MedicationRequest:patient

# All encounters for patients
Patient?_revinclude=Encounter:patient
```

## Behavior Notes

- **Deduplication**: Included resources are automatically deduplicated
- **Missing references**: If a referenced resource doesn't exist, it won't cause an error - it simply won't be included
- **Pagination**: The `total` count in the bundle refers to primary matches only, not included resources
- **Performance**: Use judiciously as including many resources can increase response size

## Combining with Other Parameters

```bash
# Get active conditions for a patient, including the encounter, sorted by date
curl "http://localhost:8080/baseR4/Condition?patient=Patient/123&clinical-status=active&_include=Condition:encounter&_sort=-onset-date"

# Get patients born after 1990 with their conditions
curl "http://localhost:8080/baseR4/Patient?birthdate=ge1990-01-01&_revinclude=Condition:patient"
```
