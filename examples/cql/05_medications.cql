/*
 * Medications - Working with medication data
 */
library Medications version '1.0.0'

using FHIR version '4.0.1'

codesystem "RxNorm": 'http://www.nlm.nih.gov/research/umls/rxnorm'

valueset "Aspirin": 'http://example.org/fhir/ValueSet/aspirin'
valueset "Statins": 'http://example.org/fhir/ValueSet/statins'
valueset "Beta Blockers": 'http://example.org/fhir/ValueSet/beta-blockers'

context Patient

// Active medications
define ActiveMedications:
    [MedicationRequest] M
    where M.status = 'active'

// Patient on aspirin
define OnAspirin:
    exists([MedicationRequest: "Aspirin"] M where M.status = 'active')

// Patient on statins
define OnStatins:
    exists([MedicationRequest: "Statins"] M where M.status = 'active')

// Count of active medications
define ActiveMedicationCount:
    Count(ActiveMedications)

// Medications started in last year
define NewMedications:
    [MedicationRequest] M
    where M.authoredOn during Interval[Today() - 1 year, Today()]
