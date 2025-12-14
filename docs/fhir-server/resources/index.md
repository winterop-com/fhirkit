# Supported FHIR Resources

This page provides an overview of all FHIR R4 resource types supported by the python-fhir-cql server.

## Resource Categories

The server supports **37 resource types** organized into the following categories:

| Category | Resources | Count |
|----------|-----------|-------|
| [Administrative](#administrative-resources) | Patient, Practitioner, PractitionerRole, Organization, Location, RelatedPerson | 6 |
| [Clinical](#clinical-resources) | Encounter, Condition, Observation, Procedure, DiagnosticReport, AllergyIntolerance, Immunization | 7 |
| [Medications](#medication-resources) | Medication, MedicationRequest | 2 |
| [Care Management](#care-management-resources) | CarePlan, CareTeam, Goal, Task | 4 |
| [Scheduling](#scheduling-resources) | Appointment, Schedule, Slot | 3 |
| [Financial](#financial-resources) | Coverage, Claim, ExplanationOfBenefit | 3 |
| [Devices](#device-resources) | Device | 1 |
| [Documents](#document-resources) | ServiceRequest, DocumentReference | 2 |
| [Forms & Consent](#forms--consent-resources) | Questionnaire, QuestionnaireResponse, Consent | 3 |
| [Quality Measures](#quality-measure-resources) | Measure, MeasureReport, Library | 3 |
| [Terminology](#terminology-resources) | ValueSet, CodeSystem | 2 |
| [Groups](#group-resources) | Group | 1 |

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
| Group | `group.json` |
| Bundle | `bundle.json`, `bundle_patient_diabetic.json`, `bundle_comprehensive.json` |

---

## See Also

- [FHIR Server Guide](../fhir-server-guide.md) - Server configuration and operations
- [Search Parameters](../search/index.md) - Search parameter documentation
- [Operations](../operations/index.md) - FHIR operations documentation
