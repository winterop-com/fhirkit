/*
 * Quality Measure - Example clinical quality measure
 * Based on: Diabetes HbA1c Control Measure
 */
library DiabetesHbA1cMeasure version '1.0.0'

using FHIR version '4.0.1'

// Code systems
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED": 'http://snomed.info/sct'

// Value sets
valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'
valueset "HbA1c Lab Test": 'http://example.org/fhir/ValueSet/hba1c'

// Codes
code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'

// Parameters
parameter "Measurement Period" Interval<DateTime>
    default Interval[@2024-01-01T00:00:00, @2024-12-31T23:59:59]

context Patient

// Initial Population: Patients with diabetes
define "Initial Population":
    exists([Condition: "Diabetes"] C
        where C.clinicalStatus ~ 'active')

// Denominator: Same as initial population
define "Denominator":
    "Initial Population"

// Denominator Exclusions: None for this measure
define "Denominator Exclusions":
    false

// Numerator: HbA1c < 8%
define "Numerator":
    exists("Most Recent HbA1c" H
        where H.value < 8 '%')

// Most recent HbA1c in measurement period
define "Most Recent HbA1c":
    Last([Observation: "HbA1c Lab Test"] O
        where O.effective during "Measurement Period"
        sort by effective)

// Stratification by age
define "Age 18-44":
    years between Patient.birthDate and Today() in Interval[18, 44]

define "Age 45-64":
    years between Patient.birthDate and Today() in Interval[45, 64]

define "Age 65+":
    years between Patient.birthDate and Today() >= 65
