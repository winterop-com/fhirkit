# QuestionnaireResponse

## Overview

The QuestionnaireResponse resource captures a completed set of answers to a Questionnaire. It represents a patient's or provider's responses to clinical assessments, intake forms, screening tools, and other structured data collection instruments. Each response is linked to the original Questionnaire definition and can be associated with a specific patient, encounter, and author.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/questionnaireresponse.html](https://hl7.org/fhir/R4/questionnaireresponse.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `identifier` | Identifier | Unique identifier for this response |
| `basedOn` | Reference(CarePlan, ServiceRequest)[] | Plan/order fulfilled by this response |
| `partOf` | Reference(Observation, Procedure)[] | Part of another resource |
| `questionnaire` | canonical | Reference to the Questionnaire being answered |
| `status` | code | in-progress, completed, amended, entered-in-error, stopped |
| `subject` | Reference(Patient, etc.) | Subject of the questionnaire |
| `encounter` | Reference(Encounter) | Encounter during which response was captured |
| `authored` | dateTime | When the response was authored |
| `author` | Reference | Who completed the response |
| `source` | Reference | Who provided the answers (if different from author) |
| `item` | BackboneElement[] | Responses to questions |

### Item Structure

Each response item contains:

| Field | Type | Description |
|-------|------|-------------|
| `linkId` | string | Links to corresponding Questionnaire item |
| `text` | string | Question text (optional, from Questionnaire) |
| `answer` | BackboneElement[] | Answer(s) to the question |
| `item` | BackboneElement[] | Nested response items |

### Answer Structure

Each answer can contain:

| Field | Type | Description |
|-------|------|-------------|
| `valueBoolean` | boolean | Boolean answer |
| `valueDecimal` | decimal | Decimal answer |
| `valueInteger` | integer | Integer answer |
| `valueDate` | date | Date answer |
| `valueDateTime` | dateTime | DateTime answer |
| `valueTime` | time | Time answer |
| `valueString` | string | String answer |
| `valueUri` | uri | URI answer |
| `valueAttachment` | Attachment | File attachment |
| `valueCoding` | Coding | Coded answer |
| `valueQuantity` | Quantity | Quantity with units |
| `valueReference` | Reference | Reference to another resource |
| `item` | BackboneElement[] | Nested items within answer |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=qr-001` |
| `questionnaire` | reference | Questionnaire reference | `questionnaire=http://example.org/Questionnaire/phq-9` |
| `patient` | reference | Patient reference | `patient=Patient/123` |
| `subject` | reference | Subject reference | `subject=Patient/123` |
| `author` | reference | Who completed it | `author=Patient/123` |
| `authored` | date | When authored | `authored=2024-01-15` |
| `status` | token | Response status | `status=completed` |
| `encounter` | reference | Encounter reference | `encounter=Encounter/456` |

## Examples

### Create a Completed PHQ-9 Response

```bash
curl -X POST http://localhost:8080/baseR4/QuestionnaireResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "QuestionnaireResponse",
    "questionnaire": "http://example.org/Questionnaire/phq-9",
    "status": "completed",
    "subject": {"reference": "Patient/patient-001"},
    "encounter": {"reference": "Encounter/encounter-001"},
    "authored": "2024-06-15T10:30:00Z",
    "author": {"reference": "Patient/patient-001"},
    "item": [
      {
        "linkId": "1",
        "text": "Little interest or pleasure in doing things",
        "answer": [{"valueInteger": 2}]
      },
      {
        "linkId": "2",
        "text": "Feeling down, depressed, or hopeless",
        "answer": [{"valueInteger": 1}]
      },
      {
        "linkId": "3",
        "text": "Trouble falling or staying asleep, or sleeping too much",
        "answer": [{"valueInteger": 2}]
      },
      {
        "linkId": "4",
        "text": "Feeling tired or having little energy",
        "answer": [{"valueInteger": 3}]
      },
      {
        "linkId": "5",
        "text": "Poor appetite or overeating",
        "answer": [{"valueInteger": 1}]
      },
      {
        "linkId": "6",
        "text": "Feeling bad about yourself",
        "answer": [{"valueInteger": 1}]
      },
      {
        "linkId": "7",
        "text": "Trouble concentrating on things",
        "answer": [{"valueInteger": 2}]
      },
      {
        "linkId": "8",
        "text": "Moving or speaking slowly, or being fidgety",
        "answer": [{"valueInteger": 0}]
      },
      {
        "linkId": "9",
        "text": "Thoughts of self-harm",
        "answer": [{"valueInteger": 0}]
      }
    ]
  }'
```

### Create a Pain Assessment Response

```bash
curl -X POST http://localhost:8080/baseR4/QuestionnaireResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "QuestionnaireResponse",
    "questionnaire": "http://example.org/Questionnaire/pain-assessment",
    "status": "completed",
    "subject": {"reference": "Patient/patient-001"},
    "authored": "2024-06-15T14:00:00Z",
    "author": {"reference": "Practitioner/practitioner-001"},
    "source": {"reference": "Patient/patient-001"},
    "item": [
      {
        "linkId": "pain-level",
        "text": "Rate your pain level (0-10)",
        "answer": [{"valueInteger": 7}]
      },
      {
        "linkId": "pain-location",
        "text": "Where is your pain located?",
        "answer": [{"valueString": "Lower back"}]
      },
      {
        "linkId": "pain-duration",
        "text": "How long have you had this pain?",
        "answer": [{"valueString": "More than 3 months"}]
      },
      {
        "linkId": "pain-type",
        "text": "Describe your pain",
        "answer": [{"valueString": "aching"}]
      },
      {
        "linkId": "pain-worse",
        "text": "What makes the pain worse?",
        "answer": [{"valueString": "Standing for long periods, bending"}]
      },
      {
        "linkId": "pain-better",
        "text": "What makes the pain better?",
        "answer": [{"valueString": "Rest, heat therapy"}]
      },
      {
        "linkId": "pain-interferes",
        "text": "Does pain interfere with daily activities?",
        "answer": [{"valueBoolean": true}]
      }
    ]
  }'
```

### Create a COVID-19 Screening Response

```bash
curl -X POST http://localhost:8080/baseR4/QuestionnaireResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "QuestionnaireResponse",
    "questionnaire": "http://example.org/Questionnaire/covid-screening",
    "status": "completed",
    "subject": {"reference": "Patient/patient-001"},
    "encounter": {"reference": "Encounter/encounter-001"},
    "authored": "2024-06-15T08:45:00Z",
    "author": {"reference": "Patient/patient-001"},
    "item": [
      {"linkId": "fever", "answer": [{"valueBoolean": false}]},
      {"linkId": "cough", "answer": [{"valueBoolean": false}]},
      {"linkId": "breathing", "answer": [{"valueBoolean": false}]},
      {"linkId": "taste-smell", "answer": [{"valueBoolean": false}]},
      {"linkId": "contact", "answer": [{"valueBoolean": false}]},
      {"linkId": "travel", "answer": [{"valueBoolean": false}]}
    ]
  }'
```

### Create a Health Intake Response with Grouped Items

```bash
curl -X POST http://localhost:8080/baseR4/QuestionnaireResponse \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "QuestionnaireResponse",
    "questionnaire": "http://example.org/Questionnaire/health-intake",
    "status": "completed",
    "subject": {"reference": "Patient/patient-001"},
    "authored": "2024-06-15T09:00:00Z",
    "author": {"reference": "Patient/patient-001"},
    "item": [
      {
        "linkId": "demographics",
        "text": "Demographics",
        "item": [
          {"linkId": "d1", "answer": [{"valueDate": "1985-03-15"}]},
          {"linkId": "d2", "answer": [{"valueString": "female"}]},
          {"linkId": "d3", "answer": [{"valueString": "English"}]}
        ]
      },
      {
        "linkId": "current-symptoms",
        "answer": [{"valueString": "Occasional headaches and fatigue"}]
      },
      {
        "linkId": "symptom-duration",
        "answer": [{"valueString": "About 2 weeks"}]
      },
      {
        "linkId": "medications",
        "answer": [{"valueString": "Daily multivitamin, occasional ibuprofen"}]
      },
      {"linkId": "allergies", "answer": [{"valueBoolean": true}]},
      {"linkId": "allergy-list", "answer": [{"valueString": "Penicillin"}]},
      {"linkId": "smoking", "answer": [{"valueBoolean": false}]},
      {"linkId": "alcohol", "answer": [{"valueString": "Occasionally"}]}
    ]
  }'
```

### Search QuestionnaireResponses

```bash
# All completed responses
curl "http://localhost:8080/baseR4/QuestionnaireResponse?status=completed"

# By patient
curl "http://localhost:8080/baseR4/QuestionnaireResponse?patient=Patient/patient-001"

# By questionnaire URL
curl "http://localhost:8080/baseR4/QuestionnaireResponse?questionnaire=http://example.org/Questionnaire/phq-9"

# By date range
curl "http://localhost:8080/baseR4/QuestionnaireResponse?authored=ge2024-01-01&authored=le2024-06-30"

# Combined: PHQ-9 responses for a patient
curl "http://localhost:8080/baseR4/QuestionnaireResponse?patient=Patient/patient-001&questionnaire=http://example.org/Questionnaire/phq-9"

# Patient compartment
curl "http://localhost:8080/baseR4/Patient/patient-001/QuestionnaireResponse"

# In-progress responses
curl "http://localhost:8080/baseR4/QuestionnaireResponse?status=in-progress"

# With _include to get the questionnaire
curl "http://localhost:8080/baseR4/QuestionnaireResponse?patient=Patient/patient-001&_include=QuestionnaireResponse:questionnaire"
```

## Generator

The `QuestionnaireResponseGenerator` creates synthetic QuestionnaireResponse resources with realistic answers matching questionnaire templates.

### Available Templates

| Template | Description |
|----------|-------------|
| `phq-9` | Depression screening responses (scores 0-3 per item) |
| `gad-7` | Anxiety screening responses (scores 0-3 per item) |
| `pain-assessment` | Pain evaluation responses |
| `covid-screening` | COVID-19 screening responses |
| `health-intake` | Health intake form responses |

### Usage

```python
from fhir_cql.server.generator import QuestionnaireResponseGenerator

generator = QuestionnaireResponseGenerator(seed=42)

# Generate response for specific questionnaire template
phq9_response = generator.generate(
    questionnaire_template="phq-9",
    patient_ref="Patient/patient-001"
)

# Generate with encounter context
response = generator.generate(
    questionnaire_template="pain-assessment",
    patient_ref="Patient/patient-001",
    encounter_ref="Encounter/encounter-001",
    author_ref="Practitioner/practitioner-001"
)

# Generate with custom questionnaire reference
response = generator.generate(
    questionnaire_ref="http://example.org/Questionnaire/custom",
    questionnaire_template="covid-screening",
    patient_ref="Patient/patient-001"
)

# Generate batch of responses
responses = generator.generate_batch(
    count=10,
    patient_ref="Patient/patient-001"
)
```

## Response Status

| Code | Display | Description |
|------|---------|-------------|
| in-progress | In Progress | Response is being worked on |
| completed | Completed | Response is finished |
| amended | Amended | Response has been corrected/updated |
| entered-in-error | Entered in Error | Response was entered incorrectly |
| stopped | Stopped | Response was abandoned before completion |

## Scoring Responses

### PHQ-9 Total Score Calculation

```python
def calculate_phq9_score(response):
    """Calculate total PHQ-9 score from QuestionnaireResponse."""
    total = 0
    for item in response.get("item", []):
        if item.get("linkId") in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            for answer in item.get("answer", []):
                if "valueInteger" in answer:
                    total += answer["valueInteger"]
    return total

# Score interpretation
# 0-4: Minimal depression
# 5-9: Mild depression
# 10-14: Moderate depression
# 15-19: Moderately severe depression
# 20-27: Severe depression
```

### GAD-7 Total Score Calculation

```python
def calculate_gad7_score(response):
    """Calculate total GAD-7 score from QuestionnaireResponse."""
    total = 0
    for item in response.get("item", []):
        if item.get("linkId") in ["1", "2", "3", "4", "5", "6", "7"]:
            for answer in item.get("answer", []):
                if "valueInteger" in answer:
                    total += answer["valueInteger"]
    return total

# Score interpretation
# 0-4: Minimal anxiety
# 5-9: Mild anxiety
# 10-14: Moderate anxiety
# 15-21: Severe anxiety
```

## Use Cases

### Clinical Assessments
- **Depression Screening**: PHQ-9 responses with total scores
- **Anxiety Screening**: GAD-7 responses with total scores
- **Pain Assessment**: Detailed pain evaluation responses
- **Functional Status**: ADL/IADL assessment responses

### Pre-Visit Workflows
- **COVID-19 Screening**: Pre-appointment symptom screening
- **Check-in Forms**: Administrative and clinical intake
- **Consent Collection**: Patient consent responses

### Care Management
- **Care Plan Progress**: Goal achievement questionnaires
- **Symptom Tracking**: Longitudinal symptom diaries
- **Medication Adherence**: Adherence questionnaires

### Research
- **Clinical Trials**: Study protocol questionnaires
- **Patient-Reported Outcomes**: PRO measure responses
- **Registry Data**: Disease registry questionnaires

## Workflow Integration

### Typical Questionnaire Workflow

1. **Questionnaire Selection**: Choose appropriate questionnaire
2. **Response Creation**: Patient or provider completes form
3. **Scoring/Analysis**: Calculate scores if applicable
4. **Clinical Review**: Provider reviews responses
5. **Documentation**: Link to encounter/care plan

### Response Lifecycle

```
in-progress → completed
     ↓           ↓
  stopped    amended
     ↓           ↓
entered-in-error ←
```

## Data Quality

### Validation Considerations

- **Required Items**: Ensure all required questions answered
- **Value Ranges**: Validate numeric responses within expected ranges
- **Linked Questionnaire**: Verify questionnaire reference exists
- **Subject Matching**: Confirm subject matches encounter patient

### Completeness Checks

```bash
# Find incomplete responses for a patient
curl "http://localhost:8080/baseR4/QuestionnaireResponse?patient=Patient/123&status=in-progress"

# Find responses missing required items (application logic required)
```

## Related Resources

- **Questionnaire** - The form definition being answered
- **Patient** - Subject of the response
- **Encounter** - Clinical context
- **Practitioner** - May author or review responses
- **CarePlan** - May be fulfilled by completing questionnaires
- **Observation** - Scores derived from responses may be stored as Observations

## See Also

- [Questionnaire](questionnaire.md) - Documentation for questionnaire definitions
- [FHIR Server Guide](../../fhir-server-guide.md) - Server configuration
- [Observation](observation.md) - For storing derived scores
- [Structured Data Capture (SDC)](https://hl7.org/fhir/uv/sdc/) - Advanced questionnaire features
