# $everything Operation

## Overview

The `$everything` operation returns all resources related to a patient in a single Bundle. This is useful for retrieving a patient's complete medical record.

**FHIR Specification**: https://hl7.org/fhir/R4/patient-operation-everything.html

## Endpoint

```
GET /Patient/{patient_id}/$everything
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `_count` | integer | 100 | Maximum resources per page (1-1000) |
| `_offset` | integer | 0 | Pagination offset |
| `_elements` | string | - | Comma-separated list of elements to include |
| `_summary` | string | - | Summary mode: true, text, data, count, false |

## Response

Returns a searchset Bundle containing:

1. The Patient resource (first entry, mode="match")
2. All related resources (mode="include")

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 45,
  "link": [
    {"relation": "self", "url": "http://localhost:8080/baseR4/Patient/patient-001/$everything"},
    {"relation": "next", "url": "http://localhost:8080/baseR4/Patient/patient-001/$everything?_offset=100&_count=100"}
  ],
  "entry": [
    {
      "fullUrl": "http://localhost:8080/baseR4/Patient/patient-001",
      "resource": {"resourceType": "Patient", "id": "patient-001", ...},
      "search": {"mode": "match"}
    },
    {
      "fullUrl": "http://localhost:8080/baseR4/Condition/condition-001",
      "resource": {"resourceType": "Condition", "id": "condition-001", ...},
      "search": {"mode": "include"}
    }
  ]
}
```

## Included Resource Types

The operation searches the Patient compartment and includes:

| Category | Resource Types |
|----------|---------------|
| Clinical | Condition, Observation, Procedure, DiagnosticReport |
| Medications | MedicationRequest, MedicationAdministration, MedicationDispense, MedicationStatement |
| Encounters | Encounter, EpisodeOfCare |
| Care Management | CarePlan, CareTeam, Goal |
| Allergies | AllergyIntolerance |
| Immunizations | Immunization |
| Documents | DocumentReference, Composition |
| Orders | ServiceRequest, NutritionOrder |
| Appointments | Appointment |
| Claims | Claim, ExplanationOfBenefit, Coverage |
| And more... | All resources in the Patient compartment |

## Examples

### Basic Usage

```bash
curl http://localhost:8080/baseR4/Patient/patient-001/\$everything
```

### With Pagination

```bash
# Get first 50 resources
curl "http://localhost:8080/baseR4/Patient/patient-001/\$everything?_count=50"

# Get next page
curl "http://localhost:8080/baseR4/Patient/patient-001/\$everything?_count=50&_offset=50"
```

### Count Only

```bash
curl "http://localhost:8080/baseR4/Patient/patient-001/\$everything?_summary=count"
```

Response:
```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 127
}
```

### Specific Elements

```bash
# Only include id, resourceType, and status
curl "http://localhost:8080/baseR4/Patient/patient-001/\$everything?_elements=id,status"
```

### Summary View

```bash
# Get text summaries only
curl "http://localhost:8080/baseR4/Patient/patient-001/\$everything?_summary=text"
```

## Use Cases

1. **Patient Portal**: Display complete patient record
2. **Data Export**: Export patient data for transfer
3. **Clinical Review**: Review all patient information
4. **Analytics**: Aggregate patient data for analysis
5. **Audit**: Review all data associated with a patient

## Performance Considerations

- Use `_count` to limit results per request
- Use `_summary=count` to get total without data
- Use `_elements` to reduce payload size
- Pagination is recommended for patients with many resources

## Notes

- The Patient resource is always the first entry
- Resources are not duplicated even if referenced multiple times
- Deleted resources are not included
- Pagination links are provided for large result sets
