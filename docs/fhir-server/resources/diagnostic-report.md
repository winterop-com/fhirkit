# DiagnosticReport

## Overview

The DiagnosticReport resource represents the findings and interpretation of diagnostic tests such as laboratory panels, radiology studies, and pathology reports. It groups related Observations together with clinical interpretations and conclusions.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/diagnosticreport.html](https://hl7.org/fhir/R4/diagnosticreport.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `status` | code | registered, partial, preliminary, final, amended, corrected, appended, cancelled, entered-in-error |
| `category` | CodeableConcept[] | Service category (LAB, RAD, PAT, etc.) |
| `code` | CodeableConcept | Type of report (LOINC code) |
| `subject` | Reference(Patient) | Patient the report is about |
| `encounter` | Reference(Encounter) | Health care event related to the report |
| `effectiveDateTime` | dateTime | Clinically relevant time for the report |
| `issued` | instant | DateTime this version was made available |
| `performer` | Reference(Practitioner)[] | Responsible diagnostic service |
| `result` | Reference(Observation)[] | Observations included in the report |
| `conclusion` | string | Clinical conclusion (interpretation) |
| `conclusionCode` | CodeableConcept[] | Codes for the clinical conclusion |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=abc123` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `code` | token | Report type code | `code=http://loinc.org\|58410-2` |
| `category` | token | Service category | `category=LAB` |
| `status` | token | Report status | `status=final` |
| `date` | date | Effective date | `date=ge2024-01-01` |
| `issued` | date | Issue date | `issued=2024-06-15` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/456` |
| `performer` | reference | Performer reference | `performer=Practitioner/789` |
| `result` | reference | Result observation | `result=Observation/obs-1` |
| `conclusion` | string | Conclusion text | `conclusion=Normal` |

## Examples

### Create a DiagnosticReport

```bash
curl -X POST http://localhost:8080/baseR4/DiagnosticReport \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "DiagnosticReport",
    "status": "final",
    "category": [{
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
        "code": "LAB",
        "display": "Laboratory"
      }]
    }],
    "code": {
      "coding": [{
        "system": "http://loinc.org",
        "code": "58410-2",
        "display": "Complete blood count (CBC) panel"
      }],
      "text": "Complete blood count (CBC) panel"
    },
    "subject": {"reference": "Patient/patient-001"},
    "effectiveDateTime": "2024-06-15T10:30:00Z",
    "issued": "2024-06-15T11:00:00Z",
    "conclusion": "CBC panel results within normal limits."
  }'
```

### Search DiagnosticReports

```bash
# By patient
curl "http://localhost:8080/baseR4/DiagnosticReport?patient=Patient/123"

# By category (laboratory reports)
curl "http://localhost:8080/baseR4/DiagnosticReport?category=LAB"

# By code (CBC panel)
curl "http://localhost:8080/baseR4/DiagnosticReport?code=http://loinc.org|58410-2"

# By status (final reports only)
curl "http://localhost:8080/baseR4/DiagnosticReport?status=final"

# By date range
curl "http://localhost:8080/baseR4/DiagnosticReport?date=ge2024-01-01&date=le2024-12-31"

# Combined search
curl "http://localhost:8080/baseR4/DiagnosticReport?patient=Patient/123&category=RAD&status=final"
```

### With _include

```bash
# Include the patient
curl "http://localhost:8080/baseR4/DiagnosticReport?patient=123&_include=DiagnosticReport:subject"

# Include the observations referenced in results
curl "http://localhost:8080/baseR4/DiagnosticReport?_include=DiagnosticReport:result"

# Include performer (practitioner)
curl "http://localhost:8080/baseR4/DiagnosticReport?_include=DiagnosticReport:performer"
```

### Patient Compartment Search

```bash
# Get all DiagnosticReports for a patient via compartment
curl "http://localhost:8080/baseR4/Patient/123/DiagnosticReport"

# With category filter
curl "http://localhost:8080/baseR4/Patient/123/DiagnosticReport?category=LAB"
```

## Generator

The `DiagnosticReportGenerator` creates synthetic DiagnosticReport resources with:

- Realistic LOINC codes for laboratory panels, radiology studies, and pathology reports
- Proper HL7 category codes (LAB, RAD, PAT)
- Weighted status distributions (70% final, 15% preliminary, 10% amended, 5% registered)
- Realistic conclusion text based on report type
- SNOMED conclusion codes

### Usage

```python
from fhirkit.server.generator import DiagnosticReportGenerator

generator = DiagnosticReportGenerator(seed=42)

# Generate a random diagnostic report
report = generator.generate(
    patient_ref="Patient/123",
    encounter_ref="Encounter/456",
    performer_ref="Practitioner/789",
    result_refs=["Observation/obs-1", "Observation/obs-2"]
)

# Generate a specific type of report
lab_report = generator.generate_lab_panel(
    patient_ref="Patient/123",
    result_refs=["Observation/obs-1", "Observation/obs-2"]
)

radiology_report = generator.generate_radiology_report(
    patient_ref="Patient/123",
    performer_ref="Practitioner/789"
)

pathology_report = generator.generate_pathology_report(
    patient_ref="Patient/123"
)

# Generate batch
reports = generator.generate_batch(
    count=10,
    patient_ref="Patient/123"
)
```

## Clinical Codes

Loaded from `fixtures/diagnostic_report_codes.json`:

### Report Types (LOINC)

| Code | Display | Category |
|------|---------|----------|
| 58410-2 | Complete blood count (CBC) panel | LAB |
| 24323-8 | Comprehensive metabolic panel | LAB |
| 57698-3 | Lipid panel | LAB |
| 24356-8 | Urinalysis panel | LAB |
| 36643-5 | Chest X-ray 2 views | RAD |
| 30746-2 | CT head without contrast | RAD |
| 24558-9 | MRI brain without contrast | RAD |
| 11526-1 | Pathology study | PAT |
| 60567-5 | Surgical pathology report | PAT |

### Categories (HL7 v2-0074)

| Code | Display |
|------|---------|
| LAB | Laboratory |
| RAD | Radiology |
| PAT | Pathology |
| CUS | Cardiac Ultrasound |
| NRS | Nursing Service |

### Conclusion Codes (SNOMED CT)

| Code | Display |
|------|---------|
| 17621005 | Normal |
| 263654008 | Abnormal |
| 260415000 | Not detected |
| 52101004 | Present |
| 2667000 | Absent |
| 419984006 | Inconclusive |
