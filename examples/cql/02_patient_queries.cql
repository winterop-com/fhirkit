/*
 * Patient Queries - Retrieve and filter patient data
 */
library PatientQueries version '1.0.0'

using FHIR version '4.0.1'

// Context: Patient-specific queries
context Patient

// Retrieve all patients
define AllPatients: [Patient]

// Active patients only
define ActivePatients:
    [Patient] P
    where P.active = true

// Patients by gender
define FemalePatients:
    [Patient] P
    where P.gender = 'female'

// Patient age calculation
define PatientBirthDate: Patient.birthDate

// Patient name
define PatientName: Patient.name.given.first() + ' ' + Patient.name.family
