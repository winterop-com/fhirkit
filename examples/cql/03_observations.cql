/*
 * Observations - Working with clinical observations
 */
library Observations version '1.0.0'

using FHIR version '4.0.1'

// Code systems
codesystem "LOINC": 'http://loinc.org'

// Value sets
valueset "Blood Pressure": 'http://example.org/fhir/ValueSet/blood-pressure'

// Codes
code "Systolic BP": '8480-6' from "LOINC" display 'Systolic blood pressure'
code "Diastolic BP": '8462-4' from "LOINC" display 'Diastolic blood pressure'

context Patient

// All observations for patient
define AllObservations: [Observation]

// Blood pressure observations
define BloodPressureObs:
    [Observation: "Blood Pressure"]

// Most recent observation
define MostRecentObservation:
    Last([Observation] O sort by effective)

// Observations in last 30 days
define RecentObservations:
    [Observation] O
    where O.effective during Interval[Today() - 30 days, Today()]
