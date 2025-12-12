/*
 * Conditions - Working with diagnoses and conditions
 */
library Conditions version '1.0.0'

using FHIR version '4.0.1'

codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "ICD10": 'http://hl7.org/fhir/sid/icd-10-cm'

valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'
valueset "Hypertension": 'http://example.org/fhir/ValueSet/hypertension'

context Patient

// All active conditions
define ActiveConditions:
    [Condition] C
    where C.clinicalStatus ~ 'active'

// Diabetes diagnosis
define HasDiabetes:
    exists([Condition: "Diabetes"])

// Hypertension diagnosis
define HasHypertension:
    exists([Condition: "Hypertension"])

// Multiple conditions (comorbidity)
define HasDiabetesAndHypertension:
    HasDiabetes and HasHypertension

// Condition onset date
define DiabetesOnset:
    [Condition: "Diabetes"] C
    return C.onset
