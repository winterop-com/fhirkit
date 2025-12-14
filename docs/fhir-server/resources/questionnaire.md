# Questionnaire

## Overview

The Questionnaire resource defines a set of questions and answer options that can be used to collect structured information from patients, caregivers, or healthcare providers. Questionnaires are commonly used for patient intake forms, clinical assessments (PHQ-9, GAD-7), screening tools, and consent forms.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/questionnaire.html](https://hl7.org/fhir/R4/questionnaire.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata including versionId and lastUpdated |
| `url` | uri | Canonical URL for this questionnaire |
| `identifier` | Identifier[] | Business identifiers |
| `version` | string | Version of the questionnaire |
| `name` | string | Computer-friendly name |
| `title` | string | Human-readable title |
| `status` | code | draft, active, retired, unknown |
| `subjectType` | code[] | Resource types that can be subjects (e.g., Patient) |
| `date` | dateTime | Date last changed |
| `publisher` | string | Who published the questionnaire |
| `description` | markdown | Natural language description |
| `purpose` | markdown | Why this questionnaire exists |
| `item` | BackboneElement[] | Questions and groups |

### Item Structure

Each item in a questionnaire can have:

| Field | Type | Description |
|-------|------|-------------|
| `linkId` | string | Unique identifier within questionnaire |
| `text` | string | Question text |
| `type` | code | group, display, boolean, decimal, integer, date, dateTime, time, string, text, url, choice, open-choice, attachment, reference, quantity |
| `required` | boolean | Whether item is required |
| `repeats` | boolean | Whether item can repeat |
| `readOnly` | boolean | Whether item is read-only |
| `answerOption` | BackboneElement[] | Permitted answers for choice items |
| `initial` | BackboneElement[] | Initial value(s) |
| `item` | BackboneElement[] | Nested items (for groups) |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=phq-9` |
| `url` | uri | Canonical URL | `url=http://example.org/Questionnaire/phq-9` |
| `name` | string | Computer name | `name=phq_9` |
| `title` | string | Human-readable title | `title=PHQ-9` |
| `status` | token | Publication status | `status=active` |
| `date` | date | Date last changed | `date=2024-01-15` |
| `publisher` | string | Publisher name | `publisher=Example` |

## Examples

### Create a PHQ-9 Depression Screening Questionnaire

```bash
curl -X POST http://localhost:8080/baseR4/Questionnaire \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Questionnaire",
    "id": "phq-9",
    "url": "http://example.org/Questionnaire/phq-9",
    "name": "phq_9",
    "title": "Patient Health Questionnaire (PHQ-9)",
    "status": "active",
    "subjectType": ["Patient"],
    "description": "A 9-item depression screening tool",
    "purpose": "Depression screening and severity assessment",
    "item": [
      {
        "linkId": "1",
        "text": "Little interest or pleasure in doing things",
        "type": "choice",
        "answerOption": [
          {"valueInteger": 0, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Not at all"}]},
          {"valueInteger": 1, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Several days"}]},
          {"valueInteger": 2, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "More than half the days"}]},
          {"valueInteger": 3, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Nearly every day"}]}
        ]
      },
      {
        "linkId": "2",
        "text": "Feeling down, depressed, or hopeless",
        "type": "choice",
        "answerOption": [
          {"valueInteger": 0, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Not at all"}]},
          {"valueInteger": 1, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Several days"}]},
          {"valueInteger": 2, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "More than half the days"}]},
          {"valueInteger": 3, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay", "valueString": "Nearly every day"}]}
        ]
      }
    ]
  }'
```

### Create a Health Intake Form with Grouped Questions

```bash
curl -X POST http://localhost:8080/baseR4/Questionnaire \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Questionnaire",
    "id": "health-intake",
    "url": "http://example.org/Questionnaire/health-intake",
    "name": "health_intake",
    "title": "Patient Health Intake Form",
    "status": "active",
    "subjectType": ["Patient"],
    "description": "General health intake questionnaire",
    "item": [
      {
        "linkId": "demographics",
        "text": "Demographics",
        "type": "group",
        "item": [
          {"linkId": "d1", "text": "Date of Birth", "type": "date"},
          {"linkId": "d2", "text": "Gender", "type": "choice"},
          {"linkId": "d3", "text": "Primary Language", "type": "string"}
        ]
      },
      {"linkId": "current-symptoms", "text": "What symptoms are you experiencing?", "type": "text"},
      {"linkId": "allergies", "text": "Do you have any allergies?", "type": "boolean"},
      {"linkId": "smoking", "text": "Do you smoke?", "type": "boolean"}
    ]
  }'
```

### Create a Pain Assessment Questionnaire

```bash
curl -X POST http://localhost:8080/baseR4/Questionnaire \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Questionnaire",
    "id": "pain-assessment",
    "url": "http://example.org/Questionnaire/pain-assessment",
    "name": "pain_assessment",
    "title": "Pain Assessment Questionnaire",
    "status": "active",
    "subjectType": ["Patient"],
    "description": "Comprehensive pain evaluation form",
    "item": [
      {"linkId": "pain-level", "text": "Rate your pain level (0-10)", "type": "integer"},
      {"linkId": "pain-location", "text": "Where is your pain located?", "type": "string"},
      {
        "linkId": "pain-type",
        "text": "Describe your pain",
        "type": "choice",
        "answerOption": [
          {"valueString": "sharp"},
          {"valueString": "dull"},
          {"valueString": "burning"},
          {"valueString": "aching"},
          {"valueString": "throbbing"}
        ]
      },
      {"linkId": "pain-interferes", "text": "Does pain interfere with daily activities?", "type": "boolean"}
    ]
  }'
```

### Search Questionnaires

```bash
# All active questionnaires
curl "http://localhost:8080/baseR4/Questionnaire?status=active"

# By canonical URL
curl "http://localhost:8080/baseR4/Questionnaire?url=http://example.org/Questionnaire/phq-9"

# By name (partial match)
curl "http://localhost:8080/baseR4/Questionnaire?name:contains=phq"

# By title
curl "http://localhost:8080/baseR4/Questionnaire?title=Patient%20Health"

# Read a specific questionnaire
curl "http://localhost:8080/baseR4/Questionnaire/phq-9"
```

## Generator

The `QuestionnaireGenerator` creates synthetic Questionnaire resources with pre-built templates for common clinical use cases.

### Available Templates

| Template | Title | Description |
|----------|-------|-------------|
| `phq-9` | Patient Health Questionnaire (PHQ-9) | 9-item depression screening tool |
| `gad-7` | Generalized Anxiety Disorder Assessment (GAD-7) | 7-item anxiety screening tool |
| `health-intake` | Patient Health Intake Form | General health history and symptoms |
| `pain-assessment` | Pain Assessment Questionnaire | Comprehensive pain evaluation |
| `covid-screening` | COVID-19 Screening Questionnaire | Pre-visit symptom screening |

### Usage

```python
from fhir_cql.server.generator import QuestionnaireGenerator

generator = QuestionnaireGenerator(seed=42)

# Generate a specific questionnaire template
phq9 = generator.generate(template="phq-9")

# Generate with custom ID
custom = generator.generate(
    questionnaire_id="my-questionnaire",
    template="gad-7"
)

# Generate random questionnaire from templates
random_q = generator.generate()

# Generate batch
questionnaires = generator.generate_batch(count=5)
```

## Item Types

| Type | Description | Example Use |
|------|-------------|-------------|
| `group` | Container for nested items | Demographics section |
| `display` | Text/instructions (no answer) | Instructions at top of form |
| `boolean` | Yes/No answer | "Do you smoke?" |
| `decimal` | Decimal number | Temperature reading |
| `integer` | Integer number | Pain level 0-10 |
| `date` | Date (YYYY-MM-DD) | Date of birth |
| `dateTime` | Date and time | Appointment time |
| `time` | Time only (HH:MM:SS) | Medication time |
| `string` | Short text | Name, single line |
| `text` | Long text | Free-form notes |
| `url` | URL | Website link |
| `choice` | Single selection from options | Gender selection |
| `open-choice` | Selection with "other" option | Ethnicity with other |
| `attachment` | File upload | Upload documents |
| `reference` | Reference to another resource | Provider reference |
| `quantity` | Numeric with units | Weight in kg |

## Questionnaire Status

| Code | Display | Description |
|------|---------|-------------|
| draft | Draft | Under development |
| active | Active | Ready for use |
| retired | Retired | No longer in use |
| unknown | Unknown | Status not known |

## Scoring PHQ-9 and GAD-7

The PHQ-9 and GAD-7 questionnaires use a standard scoring system:

### PHQ-9 Depression Severity

| Total Score | Severity |
|-------------|----------|
| 0-4 | Minimal |
| 5-9 | Mild |
| 10-14 | Moderate |
| 15-19 | Moderately Severe |
| 20-27 | Severe |

### GAD-7 Anxiety Severity

| Total Score | Severity |
|-------------|----------|
| 0-4 | Minimal |
| 5-9 | Mild |
| 10-14 | Moderate |
| 15-21 | Severe |

## Use Cases

### Clinical Assessments
- Depression screening (PHQ-9)
- Anxiety screening (GAD-7)
- Pain assessment
- Functional status
- Quality of life measures

### Administrative Forms
- Patient intake
- Insurance information
- Consent forms
- Advance directives

### Screening Tools
- COVID-19 pre-visit screening
- Fall risk assessment
- Nutritional screening
- Social determinants of health

## Related Resources

- **QuestionnaireResponse** - Completed responses to a Questionnaire
- **Patient** - Subject of the questionnaire
- **Practitioner** - May author or administer questionnaires
- **Encounter** - Context in which questionnaire is completed

## See Also

- [QuestionnaireResponse](questionnaire-response.md) - Documentation for responses
- [FHIR Server Guide](../../fhir-server-guide.md) - Server configuration
- [Structured Data Capture (SDC)](https://hl7.org/fhir/uv/sdc/) - Advanced questionnaire features
