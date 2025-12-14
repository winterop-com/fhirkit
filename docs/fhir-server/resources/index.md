# Supported FHIR Resources

This page provides an overview of all FHIR R4 resource types supported by the fhirkit server.

## Resource Categories

The server supports **53 resource types** organized into the following categories:

| Category | Resources | Count |
|----------|-----------|-------|
| [Administrative](#administrative-resources) | Patient, Practitioner, PractitionerRole, Organization, Location, RelatedPerson | 6 |
| [Clinical](#clinical-resources) | Encounter, Condition, Observation, Procedure, DiagnosticReport, AllergyIntolerance, Immunization, ClinicalImpression, FamilyMemberHistory | 9 |
| [Medications](#medication-resources) | Medication, MedicationRequest, MedicationAdministration, MedicationStatement, MedicationDispense | 5 |
| [Care Management](#care-management-resources) | CarePlan, CareTeam, Goal, Task | 4 |
| [Scheduling](#scheduling-resources) | Appointment, Schedule, Slot, HealthcareService | 4 |
| [Financial](#financial-resources) | Coverage, Claim, ExplanationOfBenefit | 3 |
| [Devices](#device-resources) | Device | 1 |
| [Documents](#document-resources) | ServiceRequest, DocumentReference, Media | 3 |
| [Forms & Consent](#forms--consent-resources) | Questionnaire, QuestionnaireResponse, Consent | 3 |
| [Quality Measures](#quality-measure-resources) | Measure, MeasureReport, Library | 3 |
| [Terminology](#terminology-resources) | ValueSet, CodeSystem | 2 |
| [Groups](#group-resources) | Group | 1 |
| [Communication & Alerts](#communication--alerts-resources) | Communication, Flag | 2 |
| [Diagnostics](#diagnostics-resources) | Specimen | 1 |
| [Orders](#orders-resources) | NutritionOrder | 1 |
| [Clinical Decision Support](#clinical-decision-support-resources) | RiskAssessment, DetectedIssue | 2 |
| [Safety](#safety-resources) | AdverseEvent | 1 |
| [Infrastructure](#infrastructure-resources) | Provenance, AuditEvent | 2 |

---

## Administrative Resources

### Patient

The foundation of clinical data - represents individuals receiving healthcare services.

**Key Fields:**
- `identifier` - Medical record numbers, SSN, etc.
- `name` - Patient's legal and preferred names
- `gender` - Administrative gender
- `birthDate` - Date of birth
- `address` - Home, work, or temporary addresses
- `telecom` - Phone numbers, email addresses

**Common Search Parameters:**
- `name`, `family`, `given` - Name searches
- `identifier` - Search by MRN or other ID
- `birthdate` - Date of birth
- `gender` - Administrative gender

**Example:**
```json
{
  "resourceType": "Patient",
  "id": "patient-001",
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1980-05-15"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/patient.html)

---

### Practitioner

Healthcare providers who deliver care.

**Key Fields:**
- `identifier` - NPI, DEA, license numbers
- `name` - Provider name
- `qualification` - Medical degrees, certifications
- `active` - Whether currently practicing

**Common Search Parameters:**
- `name`, `family`, `given` - Name searches
- `identifier` - NPI or other identifier
- `active` - Active practitioners

**Example:**
```json
{
  "resourceType": "Practitioner",
  "id": "practitioner-001",
  "name": [{"family": "Smith", "given": ["Jane"], "prefix": ["Dr."]}],
  "active": true
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/practitioner.html)

---

### PractitionerRole

Links practitioners to organizations, locations, and specialties.

**Key Fields:**
- `practitioner` - Reference to Practitioner
- `organization` - Reference to Organization
- `code` - Role codes (doctor, nurse, etc.)
- `specialty` - Medical specialties
- `location` - Where they practice

**Common Search Parameters:**
- `practitioner` - By practitioner reference
- `organization` - By organization
- `role` - By role type
- `specialty` - By specialty

**Example:**
```json
{
  "resourceType": "PractitionerRole",
  "id": "pr-001",
  "practitioner": {"reference": "Practitioner/practitioner-001"},
  "organization": {"reference": "Organization/org-001"},
  "specialty": [{"coding": [{"code": "394814009", "display": "General practice"}]}]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/practitionerrole.html)

---

### Organization

Healthcare organizations, insurers, and other entities.

**Key Fields:**
- `identifier` - NPI, tax ID
- `name` - Organization name
- `type` - Organization type
- `address` - Physical address
- `telecom` - Contact information

**Common Search Parameters:**
- `name` - Organization name
- `identifier` - By identifier
- `type` - Organization type
- `active` - Active organizations

**Example:**
```json
{
  "resourceType": "Organization",
  "id": "org-001",
  "name": "General Hospital",
  "type": [{"coding": [{"code": "prov", "display": "Healthcare Provider"}]}]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/organization.html)

---

### Location

Physical places where care is delivered.

**Key Fields:**
- `name` - Location name
- `status` - active | suspended | inactive
- `mode` - instance | kind
- `type` - Location type
- `address` - Physical address
- `managingOrganization` - Managing organization

**Common Search Parameters:**
- `name` - Location name
- `status` - Location status
- `type` - Location type
- `address`, `address-city`, `address-state`

**Example:**
```json
{
  "resourceType": "Location",
  "id": "loc-001",
  "name": "General Hospital - Main Building",
  "status": "active",
  "address": {"city": "Boston", "state": "MA"}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/location.html)

---

### RelatedPerson

Persons related to a patient (family, caregivers, emergency contacts).

**Key Fields:**
- `patient` - Reference to the patient
- `relationship` - Type of relationship
- `name` - Person's name
- `telecom` - Contact information
- `active` - Whether currently active

**Common Search Parameters:**
- `patient` - By patient reference
- `name` - Person name
- `relationship` - Relationship type
- `identifier` - By identifier

**Example:**
```json
{
  "resourceType": "RelatedPerson",
  "id": "rp-001",
  "patient": {"reference": "Patient/patient-001"},
  "relationship": [{"coding": [{"code": "SPS", "display": "spouse"}]}],
  "name": [{"family": "Smith", "given": ["Mary"]}]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/relatedperson.html)

---

## Clinical Resources

### Encounter

A patient's interaction with healthcare services.

**Key Fields:**
- `status` - planned | arrived | in-progress | finished | cancelled
- `class` - ambulatory | emergency | inpatient | etc.
- `subject` - Reference to Patient
- `period` - Start and end times
- `participant` - Providers involved

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `status` - Encounter status
- `class` - Encounter class
- `date` - Encounter date

[FHIR R4 Specification](https://hl7.org/fhir/R4/encounter.html)

---

### Condition

Clinical conditions, diagnoses, problems, or health concerns.

**Key Fields:**
- `clinicalStatus` - active | recurrence | relapse | inactive | remission | resolved
- `verificationStatus` - unconfirmed | confirmed | refuted
- `code` - Diagnosis code (ICD-10, SNOMED CT)
- `subject` - Reference to Patient
- `onsetDateTime` - When condition started

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `code` - By diagnosis code
- `clinical-status` - By clinical status
- `onset-date` - By onset date

[FHIR R4 Specification](https://hl7.org/fhir/R4/condition.html)

---

### Observation

Measurements and simple assertions about a patient.

**Key Fields:**
- `status` - registered | preliminary | final | amended
- `code` - What was observed (LOINC)
- `subject` - Reference to Patient
- `effectiveDateTime` - When observed
- `valueQuantity` - Numeric result

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `code` - Observation type
- `date` - Observation date
- `status` - Observation status

[FHIR R4 Specification](https://hl7.org/fhir/R4/observation.html)

---

### Procedure

Actions performed on or for a patient.

**Key Fields:**
- `status` - preparation | in-progress | completed | etc.
- `code` - Procedure code (CPT, SNOMED CT)
- `subject` - Reference to Patient
- `performedDateTime` - When performed
- `performer` - Who performed it

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `code` - Procedure code
- `date` - Procedure date
- `status` - Procedure status

[FHIR R4 Specification](https://hl7.org/fhir/R4/procedure.html)

---

### DiagnosticReport

Results and interpretation of diagnostic tests.

See [detailed documentation](diagnostic-report.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/diagnosticreport.html)

---

### AllergyIntolerance

Allergies and intolerances affecting a patient.

See [detailed documentation](allergy-intolerance.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/allergyintolerance.html)

---

### Immunization

Vaccination records.

See [detailed documentation](immunization.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/immunization.html)

---

### ClinicalImpression

Clinical assessments and diagnoses made by practitioners.

**Key Fields:**
- `status` - in-progress | completed | entered-in-error
- `subject` - Reference to Patient
- `encounter` - Reference to Encounter
- `effectiveDateTime` - When assessment was made
- `assessor` - Practitioner who made assessment
- `summary` - Textual summary
- `finding` - Specific findings/diagnoses
- `prognosisCodeableConcept` - Prognosis codes

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `encounter` - By encounter
- `status` - Assessment status
- `assessor` - By assessor

**Example:**
```json
{
  "resourceType": "ClinicalImpression",
  "id": "ci-001",
  "status": "completed",
  "subject": {"reference": "Patient/patient-001"},
  "effectiveDateTime": "2024-06-15T10:30:00Z",
  "assessor": {"reference": "Practitioner/practitioner-001"},
  "summary": "Patient presents with well-controlled Type 2 Diabetes"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/clinicalimpression.html)

---

### FamilyMemberHistory

Health history of patient's family members relevant for understanding genetic and familial disease risk.

**Key Fields:**
- `status` - partial | completed | entered-in-error | health-unknown
- `patient` - Reference to Patient
- `relationship` - Family relationship (father, mother, sibling, etc.)
- `sex` - Sex of family member
- `ageAge` / `deceasedAge` - Age information
- `condition` - Conditions with onset ages

**Common Search Parameters:**
- `patient` - By patient
- `status` - History status
- `relationship` - By relationship type

**Example:**
```json
{
  "resourceType": "FamilyMemberHistory",
  "id": "fmh-001",
  "status": "completed",
  "patient": {"reference": "Patient/patient-001"},
  "relationship": {"coding": [{"code": "FTH", "display": "Father"}]},
  "condition": [
    {
      "code": {"coding": [{"code": "73211009", "display": "Diabetes mellitus"}]},
      "onsetAge": {"value": 55, "unit": "years"}
    }
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/familymemberhistory.html)

---

## Medication Resources

### Medication

Medication definitions.

See [detailed documentation](medication.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/medication.html)

---

### MedicationRequest

Prescriptions and medication orders.

**Key Fields:**
- `status` - active | on-hold | cancelled | completed
- `intent` - proposal | plan | order
- `medicationCodeableConcept` - Medication code (RxNorm)
- `subject` - Reference to Patient
- `authoredOn` - When prescribed
- `dosageInstruction` - How to take

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `code` - Medication code
- `status` - Request status
- `authoredon` - Prescription date

[FHIR R4 Specification](https://hl7.org/fhir/R4/medicationrequest.html)

---

### MedicationAdministration

Record of medication being administered to a patient.

**Key Fields:**
- `status` - in-progress | not-done | on-hold | completed | entered-in-error | stopped | unknown
- `medicationCodeableConcept` - Medication given
- `subject` - Reference to Patient
- `context` - Reference to Encounter
- `effectiveDateTime` / `effectivePeriod` - When administered
- `performer` - Who administered
- `dosage` - Dosage details
- `request` - Reference to MedicationRequest

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `effective-time` - Administration time
- `status` - Administration status
- `code` - Medication code

**Example:**
```json
{
  "resourceType": "MedicationAdministration",
  "id": "ma-001",
  "status": "completed",
  "medicationCodeableConcept": {
    "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin 500mg"}]
  },
  "subject": {"reference": "Patient/patient-001"},
  "effectiveDateTime": "2024-06-15T08:00:00Z"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/medicationadministration.html)

---

### MedicationStatement

Record of what a patient reports they are taking.

**Key Fields:**
- `status` - active | completed | entered-in-error | intended | stopped | on-hold | unknown | not-taken
- `medicationCodeableConcept` - Medication being taken
- `subject` - Reference to Patient
- `effectiveDateTime` / `effectivePeriod` - When taking
- `informationSource` - Who provided the information
- `derivedFrom` - Reference to MedicationRequest
- `dosage` - Dosage details

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `effective` - Effective time
- `status` - Statement status
- `code` - Medication code

**Example:**
```json
{
  "resourceType": "MedicationStatement",
  "id": "ms-001",
  "status": "active",
  "medicationCodeableConcept": {
    "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "197361", "display": "Aspirin 81mg"}]
  },
  "subject": {"reference": "Patient/patient-001"},
  "effectiveDateTime": "2024-06-01"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/medicationstatement.html)

---

### MedicationDispense

Pharmacy dispensing records.

**Key Fields:**
- `status` - preparation | in-progress | cancelled | on-hold | completed | entered-in-error | stopped | declined | unknown
- `medicationCodeableConcept` - Medication dispensed
- `subject` - Reference to Patient
- `performer` - Pharmacist/technician
- `authorizingPrescription` - Reference to MedicationRequest
- `quantity` - Amount dispensed
- `daysSupply` - Days supply
- `whenHandedOver` - When given to patient

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `status` - Dispense status
- `performer` - By performer
- `prescription` - By prescription

**Example:**
```json
{
  "resourceType": "MedicationDispense",
  "id": "md-001",
  "status": "completed",
  "medicationCodeableConcept": {
    "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin 500mg"}]
  },
  "subject": {"reference": "Patient/patient-001"},
  "quantity": {"value": 90, "unit": "tablets"},
  "daysSupply": {"value": 30, "unit": "days"}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/medicationdispense.html)

---

## Care Management Resources

### CarePlan

Plans for patient care.

See [detailed documentation](careplan.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/careplan.html)

---

### CareTeam

Team of providers caring for a patient.

**Key Fields:**
- `status` - proposed | active | suspended | inactive
- `subject` - Reference to Patient
- `participant` - Team members and roles
- `period` - Active period
- `managingOrganization` - Organization

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `status` - Team status
- `participant` - By participant

**Example:**
```json
{
  "resourceType": "CareTeam",
  "id": "ct-001",
  "status": "active",
  "subject": {"reference": "Patient/patient-001"},
  "participant": [
    {
      "role": [{"coding": [{"code": "446050000", "display": "Primary care physician"}]}],
      "member": {"reference": "Practitioner/practitioner-001"}
    }
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/careteam.html)

---

### Goal

Healthcare goals for a patient.

See [detailed documentation](goal.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/goal.html)

---

### Task

Workflow tasks.

**Key Fields:**
- `status` - draft | requested | in-progress | completed | failed
- `intent` - unknown | proposal | plan | order
- `code` - Task type
- `for` - Subject (usually Patient)
- `owner` - Responsible party
- `authoredOn` - When created

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `status` - Task status
- `code` - Task type
- `owner` - Task owner

**Example:**
```json
{
  "resourceType": "Task",
  "id": "task-001",
  "status": "in-progress",
  "intent": "order",
  "code": {"coding": [{"code": "fulfill", "display": "Fulfill request"}]},
  "for": {"reference": "Patient/patient-001"}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/task.html)

---

## Scheduling Resources

### Appointment

Scheduled appointments.

**Key Fields:**
- `status` - proposed | pending | booked | arrived | fulfilled | cancelled
- `start` / `end` - Appointment time
- `participant` - Patient, practitioner, location
- `appointmentType` - Type of appointment
- `reasonCode` - Why scheduled

**Common Search Parameters:**
- `patient` - By patient
- `status` - Appointment status
- `date` - Appointment date
- `actor` - By participant

**Example:**
```json
{
  "resourceType": "Appointment",
  "id": "apt-001",
  "status": "booked",
  "start": "2024-01-15T09:00:00Z",
  "end": "2024-01-15T09:30:00Z",
  "participant": [
    {"actor": {"reference": "Patient/patient-001"}, "status": "accepted"},
    {"actor": {"reference": "Practitioner/practitioner-001"}, "status": "accepted"}
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/appointment.html)

---

### Schedule

Defines availability for booking.

**Key Fields:**
- `active` - Whether schedule is active
- `actor` - Practitioner, Location, etc.
- `planningHorizon` - Period schedule covers
- `serviceType` - Types of services available

**Common Search Parameters:**
- `actor` - By actor
- `active` - Active schedules
- `date` - Schedule date

[FHIR R4 Specification](https://hl7.org/fhir/R4/schedule.html)

---

### Slot

Individual bookable time slots.

**Key Fields:**
- `schedule` - Reference to Schedule
- `status` - busy | free | busy-unavailable | busy-tentative
- `start` / `end` - Slot times
- `serviceType` - Type of service

**Common Search Parameters:**
- `schedule` - By schedule
- `status` - Slot status
- `start` - Start time

[FHIR R4 Specification](https://hl7.org/fhir/R4/slot.html)

---

### HealthcareService

Services offered by healthcare organizations.

**Key Fields:**
- `active` - Whether service is active
- `providedBy` - Reference to Organization
- `category` - Service category
- `type` - Type of service
- `specialty` - Medical specialties
- `location` - Service locations
- `name` - Service name
- `availableTime` - Availability hours
- `notAvailable` - Unavailable times

**Common Search Parameters:**
- `organization` - By organization
- `active` - Active services
- `location` - By location
- `specialty` - By specialty
- `service-type` - By service type

**Example:**
```json
{
  "resourceType": "HealthcareService",
  "id": "hs-001",
  "active": true,
  "providedBy": {"reference": "Organization/org-001"},
  "category": [{"coding": [{"code": "35", "display": "Hospital"}]}],
  "type": [{"coding": [{"code": "124", "display": "General Practice"}]}],
  "name": "General Medicine Clinic"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/healthcareservice.html)

---

## Financial Resources

### Coverage

Insurance coverage information.

**Key Fields:**
- `status` - active | cancelled | draft | entered-in-error
- `type` - Type of coverage
- `beneficiary` - Reference to Patient
- `payor` - Insurance company
- `class` - Coverage details (group, plan)

**Common Search Parameters:**
- `patient`, `beneficiary` - By patient
- `status` - Coverage status
- `type` - Coverage type
- `payor` - By payor

**Example:**
```json
{
  "resourceType": "Coverage",
  "id": "cov-001",
  "status": "active",
  "beneficiary": {"reference": "Patient/patient-001"},
  "payor": [{"reference": "Organization/insurance-001"}]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/coverage.html)

---

### Claim

Insurance claims for services.

**Key Fields:**
- `status` - active | cancelled | draft | entered-in-error
- `type` - Claim type (professional, institutional)
- `use` - claim | preauthorization | predetermination
- `patient` - Reference to Patient
- `provider` - Billing provider
- `item` - Service line items

**Common Search Parameters:**
- `patient` - By patient
- `status` - Claim status
- `created` - Creation date
- `provider` - By provider

[FHIR R4 Specification](https://hl7.org/fhir/R4/claim.html)

---

### ExplanationOfBenefit

Processed claim results.

**Key Fields:**
- `status` - active | cancelled | draft | entered-in-error
- `type` - Claim type
- `use` - claim | preauthorization | predetermination
- `patient` - Reference to Patient
- `outcome` - queued | complete | error | partial
- `total` - Payment totals

**Common Search Parameters:**
- `patient` - By patient
- `status` - EOB status
- `created` - Creation date
- `outcome` - Processing outcome

[FHIR R4 Specification](https://hl7.org/fhir/R4/explanationofbenefit.html)

---

## Device Resources

### Device

Medical devices.

**Key Fields:**
- `status` - active | inactive | entered-in-error
- `type` - Device type
- `patient` - Patient using device
- `manufacturer` - Device manufacturer
- `modelNumber` - Model number
- `udiCarrier` - UDI barcode information

**Common Search Parameters:**
- `patient` - By patient
- `status` - Device status
- `type` - Device type
- `manufacturer` - By manufacturer

[FHIR R4 Specification](https://hl7.org/fhir/R4/device.html)

---

## Document Resources

### ServiceRequest

Orders for services.

See [detailed documentation](service-request.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/servicerequest.html)

---

### DocumentReference

References to clinical documents.

See [detailed documentation](document-reference.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/documentreference.html)

---

### Media

Clinical images, videos, and audio recordings.

**Key Fields:**
- `status` - preparation | in-progress | not-done | on-hold | stopped | completed | entered-in-error | unknown
- `type` - image | video | audio
- `modality` - DICOM modality (X-ray, CT, MRI, etc.)
- `subject` - Reference to Patient
- `encounter` - Reference to Encounter
- `createdDateTime` - When captured
- `operator` - Practitioner who captured
- `bodySite` - Body site imaged
- `content` - Media attachment with contentType

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `encounter` - By encounter
- `status` - Media status
- `type` - Media type
- `created` - Creation date

**Example:**
```json
{
  "resourceType": "Media",
  "id": "media-001",
  "status": "completed",
  "type": {"coding": [{"code": "image", "display": "Image"}]},
  "modality": {"coding": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "DX", "display": "Digital Radiography"}]},
  "subject": {"reference": "Patient/patient-001"},
  "bodySite": {"coding": [{"code": "51185008", "display": "Chest"}]},
  "content": {"contentType": "image/jpeg", "title": "Chest X-ray"}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/media.html)

---

## Forms & Consent Resources

### Questionnaire

Structured data collection forms, assessments, and surveys.

See [detailed documentation](questionnaire.md)

**Key Fields:**
- `url` - Canonical URL
- `name` - Computer-friendly name
- `title` - Human-readable title
- `status` - draft | active | retired | unknown
- `subjectType` - Resource types (Patient)
- `item` - Questions and groups

**Common Search Parameters:**
- `url` - Canonical URL
- `name` - Computer name
- `title` - Human-readable title
- `status` - Publication status

**Example:**
```json
{
  "resourceType": "Questionnaire",
  "id": "phq-9",
  "url": "http://example.org/Questionnaire/phq-9",
  "title": "Patient Health Questionnaire (PHQ-9)",
  "status": "active",
  "item": [
    {"linkId": "1", "text": "Little interest or pleasure", "type": "choice"}
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/questionnaire.html)

---

### QuestionnaireResponse

Completed answers to a Questionnaire.

See [detailed documentation](questionnaire-response.md)

**Key Fields:**
- `questionnaire` - Reference to the form
- `status` - in-progress | completed | amended | entered-in-error | stopped
- `subject` - Patient reference
- `authored` - When completed
- `author` - Who completed it
- `item` - Answer items

**Common Search Parameters:**
- `questionnaire` - By questionnaire URL
- `patient`, `subject` - By patient
- `author` - By author
- `authored` - By date
- `status` - Response status

**Example:**
```json
{
  "resourceType": "QuestionnaireResponse",
  "questionnaire": "http://example.org/Questionnaire/phq-9",
  "status": "completed",
  "subject": {"reference": "Patient/patient-001"},
  "authored": "2024-06-15T10:30:00Z",
  "item": [
    {"linkId": "1", "answer": [{"valueInteger": 2}]}
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/questionnaireresponse.html)

---

### Consent

Privacy and treatment consent records.

**Key Fields:**
- `status` - draft | proposed | active | rejected | inactive | entered-in-error
- `scope` - patient-privacy | research | treatment
- `category` - Consent category codes
- `patient` - Patient reference
- `dateTime` - When consent was given
- `performer` - Who provided consent
- `provision` - Permit/deny rules

**Common Search Parameters:**
- `patient` - By patient
- `status` - Consent status
- `scope` - Consent scope
- `category` - Consent category

**Example:**
```json
{
  "resourceType": "Consent",
  "status": "active",
  "scope": {
    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope", "code": "patient-privacy"}]
  },
  "patient": {"reference": "Patient/patient-001"},
  "dateTime": "2024-06-15T10:00:00Z"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/consent.html)

---

## Quality Measure Resources

### Measure

Quality measure definitions.

See [detailed documentation](measure.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/measure.html)

---

### MeasureReport

Quality measure results.

See [detailed documentation](measure-report.md)

[FHIR R4 Specification](https://hl7.org/fhir/R4/measurereport.html)

---

### Library

CQL libraries and other knowledge artifacts.

**Key Fields:**
- `status` - draft | active | retired
- `type` - logic-library | model-definition | etc.
- `url` - Canonical URL
- `content` - Library content (CQL, ELM)

**Common Search Parameters:**
- `name` - Library name
- `url` - Canonical URL
- `status` - Publication status
- `version` - Version

[FHIR R4 Specification](https://hl7.org/fhir/R4/library.html)

---

## Terminology Resources

### ValueSet

Value set definitions.

**Key Fields:**
- `status` - draft | active | retired
- `url` - Canonical URL
- `name` - Machine-friendly name
- `compose` - Included codes
- `expansion` - Expanded codes

**Common Search Parameters:**
- `name` - ValueSet name
- `url` - Canonical URL
- `status` - Publication status

[FHIR R4 Specification](https://hl7.org/fhir/R4/valueset.html)

---

### CodeSystem

Code system definitions.

**Key Fields:**
- `status` - draft | active | retired
- `url` - Canonical URL
- `content` - not-present | complete | etc.
- `concept` - Code definitions

**Common Search Parameters:**
- `name` - CodeSystem name
- `url` - Canonical URL
- `status` - Publication status

[FHIR R4 Specification](https://hl7.org/fhir/R4/codesystem.html)

---

## Group Resources

### Group

Groups of patients or other entities.

**Key Fields:**
- `type` - person | animal | practitioner | device
- `actual` - true for actual group, false for definitional
- `code` - Group code
- `member` - Group members
- `characteristic` - Defining characteristics

**Common Search Parameters:**
- `type` - Group type
- `actual` - Actual vs definitional
- `member` - By member
- `code` - Group code

**Example:**
```json
{
  "resourceType": "Group",
  "id": "grp-001",
  "type": "person",
  "actual": true,
  "name": "Diabetes Study Cohort",
  "member": [
    {"entity": {"reference": "Patient/patient-001"}},
    {"entity": {"reference": "Patient/patient-002"}}
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/group.html)

---

## Communication & Alerts Resources

### Communication

Messages exchanged between providers and patients.

**Key Fields:**
- `status` - preparation | in-progress | not-done | on-hold | stopped | completed | entered-in-error | unknown
- `category` - alert | notification | reminder | instruction
- `priority` - routine | urgent | asap | stat
- `subject` - Reference to Patient
- `encounter` - Reference to Encounter
- `sender` - Who sent the message
- `recipient` - Who received it
- `payload` - Message content

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `sender` - By sender
- `recipient` - By recipient
- `status` - Message status
- `category` - Message category

**Example:**
```json
{
  "resourceType": "Communication",
  "id": "comm-001",
  "status": "completed",
  "category": [{"coding": [{"code": "notification", "display": "Notification"}]}],
  "subject": {"reference": "Patient/patient-001"},
  "sender": {"reference": "Practitioner/practitioner-001"},
  "payload": [{"contentString": "Your lab results are available"}]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/communication.html)

---

### Flag

Patient safety alerts and warnings.

**Key Fields:**
- `status` - active | inactive | entered-in-error
- `category` - clinical | administrative | behavioral | safety | research
- `code` - Flag type (fall risk, allergy alert, DNR, etc.)
- `subject` - Reference to Patient
- `period` - When flag is active
- `author` - Who created the flag

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `status` - Flag status
- `author` - By author

**Example:**
```json
{
  "resourceType": "Flag",
  "id": "flag-001",
  "status": "active",
  "category": [{"coding": [{"code": "safety", "display": "Safety"}]}],
  "code": {"coding": [{"code": "fall-risk", "display": "Fall Risk"}]},
  "subject": {"reference": "Patient/patient-001"}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/flag.html)

---

## Diagnostics Resources

### Specimen

Laboratory specimens for analysis.

**Key Fields:**
- `status` - available | unavailable | unsatisfactory | entered-in-error
- `type` - Specimen type (blood, urine, tissue, swab)
- `subject` - Reference to Patient
- `receivedTime` - When specimen was received
- `collection` - Collection details (collector, collectedDateTime, bodySite)
- `container` - Container information
- `request` - Reference to ServiceRequest

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `type` - Specimen type
- `status` - Specimen status
- `collector` - By collector

**Example:**
```json
{
  "resourceType": "Specimen",
  "id": "sp-001",
  "status": "available",
  "type": {"coding": [{"code": "119297000", "display": "Blood specimen"}]},
  "subject": {"reference": "Patient/patient-001"},
  "collection": {
    "collectedDateTime": "2024-06-15T08:00:00Z",
    "bodySite": {"coding": [{"code": "53120007", "display": "Arm"}]}
  }
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/specimen.html)

---

## Orders Resources

### NutritionOrder

Diet and nutrition orders for patients.

**Key Fields:**
- `status` - draft | active | on-hold | revoked | completed | entered-in-error | unknown
- `intent` - proposal | plan | directive | order
- `patient` - Reference to Patient
- `encounter` - Reference to Encounter
- `dateTime` - When order was created
- `orderer` - Practitioner who ordered
- `oralDiet` - Oral diet details (type, schedule, nutrient, texture)
- `enteralFormula` - Enteral/tube feeding details

**Common Search Parameters:**
- `patient` - By patient
- `encounter` - By encounter
- `status` - Order status
- `datetime` - Order date
- `orderer` - By ordering practitioner

**Example:**
```json
{
  "resourceType": "NutritionOrder",
  "id": "no-001",
  "status": "active",
  "intent": "order",
  "patient": {"reference": "Patient/patient-001"},
  "dateTime": "2024-06-15T10:00:00Z",
  "oralDiet": {
    "type": [{"coding": [{"code": "diabetic", "display": "Diabetic Diet"}]}]
  }
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/nutritionorder.html)

---

## Clinical Decision Support Resources

### RiskAssessment

Clinical risk predictions and scoring.

**Key Fields:**
- `status` - registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown
- `subject` - Reference to Patient
- `encounter` - Reference to Encounter
- `occurrenceDateTime` - When assessment was performed
- `performer` - Practitioner who performed assessment
- `condition` - Condition being assessed
- `prediction` - Predictions with outcome, probability, and qualitative risk

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `encounter` - By encounter
- `condition` - By condition
- `performer` - By performer

**Example:**
```json
{
  "resourceType": "RiskAssessment",
  "id": "ra-001",
  "status": "final",
  "subject": {"reference": "Patient/patient-001"},
  "occurrenceDateTime": "2024-06-15T10:00:00Z",
  "prediction": [
    {
      "outcome": {"text": "Fall"},
      "probabilityDecimal": 0.35,
      "qualitativeRisk": {"coding": [{"code": "moderate", "display": "Moderate Risk"}]}
    }
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/riskassessment.html)

---

### DetectedIssue

Clinical decision support alerts and warnings.

**Key Fields:**
- `status` - registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown
- `code` - Issue type (drug-drug interaction, duplicate therapy, etc.)
- `severity` - high | moderate | low
- `patient` - Reference to Patient
- `identifiedDateTime` - When issue was identified
- `author` - Who identified the issue
- `implicated` - Resources involved in the issue
- `detail` - Description of the issue
- `mitigation` - Actions taken to address the issue

**Common Search Parameters:**
- `patient` - By patient
- `code` - Issue type
- `author` - By author
- `identified` - When identified

**Example:**
```json
{
  "resourceType": "DetectedIssue",
  "id": "di-001",
  "status": "final",
  "code": {"coding": [{"code": "DRG", "display": "Drug Interaction Alert"}]},
  "severity": "high",
  "patient": {"reference": "Patient/patient-001"},
  "identifiedDateTime": "2024-06-15T10:00:00Z",
  "detail": "Potential interaction between warfarin and aspirin"
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/detectedissue.html)

---

## Safety Resources

### AdverseEvent

Patient safety event reporting.

**Key Fields:**
- `actuality` - actual | potential
- `category` - Event category (product-problem, wrong-dose, medical-device-use-error, etc.)
- `event` - Event type (SNOMED CT codes)
- `subject` - Reference to Patient
- `encounter` - Reference to Encounter
- `date` - When event occurred
- `recorder` - Who recorded the event
- `seriousness` - Non-serious | Serious | Life-threatening | Results in death
- `outcome` - resolved | recovering | ongoing | resolvedWithSequelae | fatal | unknown
- `suspectEntity` - Suspected causative agents

**Common Search Parameters:**
- `patient`, `subject` - By patient
- `actuality` - Actual vs potential
- `category` - Event category
- `date` - Event date

**Example:**
```json
{
  "resourceType": "AdverseEvent",
  "id": "ae-001",
  "actuality": "actual",
  "category": [{"coding": [{"code": "product-problem", "display": "Product Problem"}]}],
  "event": {"coding": [{"system": "http://snomed.info/sct", "code": "418799008", "display": "Adverse reaction to drug"}]},
  "subject": {"reference": "Patient/patient-001"},
  "date": "2024-06-15T10:00:00Z",
  "seriousness": {"coding": [{"code": "Non-serious", "display": "Non-serious"}]}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/adverseevent.html)

---

## Infrastructure Resources

### Provenance

Resource provenance and audit trail tracking.

**Key Fields:**
- `target` - Resources being tracked
- `occurredDateTime` - When activity occurred
- `recorded` - When provenance was recorded
- `activity` - Activity type (create, revise, delete, etc.)
- `agent` - Who/what was responsible (type, who, onBehalfOf)
- `entity` - Entities used/modified (role, what)
- `reason` - Reason for the activity
- `signature` - Digital signatures

**Common Search Parameters:**
- `target` - By target resource
- `agent` - By agent
- `recorded` - When recorded
- `patient` - By patient (via target)

**Example:**
```json
{
  "resourceType": "Provenance",
  "id": "prov-001",
  "target": [{"reference": "Patient/patient-001"}],
  "occurredDateTime": "2024-06-15T10:00:00Z",
  "recorded": "2024-06-15T10:05:00Z",
  "activity": {"coding": [{"code": "CREATE", "display": "create"}]},
  "agent": [
    {
      "type": {"coding": [{"code": "author", "display": "Author"}]},
      "who": {"reference": "Practitioner/practitioner-001"}
    }
  ]
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/provenance.html)

---

### AuditEvent

Security audit logging.

**Key Fields:**
- `type` - Event type (rest, export, import, query, etc.)
- `subtype` - Event subtype for REST operations (create, read, update, delete)
- `action` - C (Create) | R (Read) | U (Update) | D (Delete) | E (Execute)
- `recorded` - When event was recorded
- `outcome` - 0 (success) | 4 (minor failure) | 8 (serious failure) | 12 (major failure)
- `agent` - Who/what participated (type, who, requestor, network)
- `source` - Audit event source (observer, type)
- `entity` - Resources involved (what, type, role)

**Common Search Parameters:**
- `patient` - By patient (via entity)
- `agent` - By agent
- `date` - When recorded
- `action` - By action type
- `outcome` - By outcome

**Example:**
```json
{
  "resourceType": "AuditEvent",
  "id": "audit-001",
  "type": {"coding": [{"code": "rest", "display": "RESTful Operation"}]},
  "subtype": [{"coding": [{"code": "read", "display": "read"}]}],
  "action": "R",
  "recorded": "2024-06-15T10:00:00Z",
  "outcome": "0",
  "agent": [
    {
      "type": {"coding": [{"code": "IRCP", "display": "information recipient"}]},
      "who": {"reference": "Practitioner/practitioner-001"},
      "requestor": true
    }
  ],
  "source": {"observer": {"display": "FHIR Server"}}
}
```

[FHIR R4 Specification](https://hl7.org/fhir/R4/auditevent.html)

---

## Example Files

Complete example JSON files for all resource types are available in the `examples/fhir/` directory:

| Resource Type | Example File |
|---------------|-------------|
| Patient | `patient.json`, `patient_john_smith.json`, `patient_diabetic.json` |
| Practitioner | `practitioner.json` |
| PractitionerRole | `practitioner_role.json` |
| Organization | `organization.json` |
| Location | `location.json` |
| RelatedPerson | `related_person.json` |
| Encounter | `encounter.json` |
| Condition | `condition.json`, `condition_diabetes.json` |
| Observation | `observation_bp.json`, `observation_lab.json`, `observation_hba1c.json`, `observation_glucose.json`, `observation_blood_pressure.json` |
| Procedure | `procedure.json` |
| DiagnosticReport | `diagnostic_report.json` |
| AllergyIntolerance | `allergy_intolerance.json` |
| Immunization | `immunization.json` |
| Medication | `medication.json` |
| MedicationRequest | `medication_request.json` |
| CarePlan | `care_plan.json` |
| CareTeam | `care_team.json` |
| Goal | `goal.json` |
| Task | `task.json` |
| Appointment | `appointment.json` |
| Schedule | `schedule.json` |
| Slot | `slot.json` |
| Coverage | `coverage.json` |
| Claim | `claim.json` |
| ExplanationOfBenefit | `explanation_of_benefit.json` |
| Device | `device.json` |
| ServiceRequest | `service_request.json` |
| DocumentReference | `document_reference.json` |
| Measure | `measure.json` |
| MeasureReport | `measure_report.json`, `measure_report_individual.json` |
| Library | `library.json` |
| ValueSet | `value_set.json` |
| CodeSystem | `code_system.json` |
| Questionnaire | `questionnaire.json` |
| QuestionnaireResponse | `questionnaire_response.json` |
| Group | `group.json` |
| Bundle | `bundle.json`, `bundle_patient_diabetic.json`, `bundle_comprehensive.json` |

---

## See Also

- [FHIR Server Guide](../fhir-server-guide.md) - Server configuration and operations
- [Search Parameters](../search/index.md) - Search parameter documentation
- [Operations](../operations/index.md) - FHIR operations documentation
