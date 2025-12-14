"""Tests for FHIR synthetic data generators."""

from fhir_cql.server.generator import (
    AdverseEventGenerator,
    AuditEventGenerator,
    ClinicalImpressionGenerator,
    CommunicationGenerator,
    ConditionGenerator,
    DetectedIssueGenerator,
    EncounterGenerator,
    FamilyMemberHistoryGenerator,
    FlagGenerator,
    HealthcareServiceGenerator,
    MediaGenerator,
    MedicationAdministrationGenerator,
    MedicationDispenseGenerator,
    MedicationRequestGenerator,
    MedicationStatementGenerator,
    NutritionOrderGenerator,
    ObservationGenerator,
    OrganizationGenerator,
    PatientGenerator,
    PatientRecordGenerator,
    PractitionerGenerator,
    ProcedureGenerator,
    ProvenanceGenerator,
    RiskAssessmentGenerator,
    SpecimenGenerator,
)
from fhir_cql.server.generator.clinical_codes import (
    CONDITIONS_SNOMED,
    LAB_TESTS,
    MEDICATIONS_RXNORM,
    VITAL_SIGNS,
)


class TestPatientGenerator:
    """Tests for PatientGenerator."""

    def test_generate_patient(self):
        """Test generating a single patient."""
        gen = PatientGenerator(seed=42)
        patient = gen.generate()

        assert patient["resourceType"] == "Patient"
        assert "id" in patient
        assert "meta" in patient
        assert "name" in patient
        assert "gender" in patient
        assert "birthDate" in patient

    def test_generate_patient_with_id(self):
        """Test generating a patient with specific ID."""
        gen = PatientGenerator(seed=42)
        patient = gen.generate(patient_id="test-patient-123")

        assert patient["id"] == "test-patient-123"

    def test_generate_patient_has_identifier(self):
        """Test that patient has identifiers (MRN, SSN)."""
        gen = PatientGenerator(seed=42)
        patient = gen.generate()

        assert "identifier" in patient
        assert len(patient["identifier"]) >= 1

    def test_generate_patient_has_contact(self):
        """Test that patient has contact information."""
        gen = PatientGenerator(seed=42)
        patient = gen.generate()

        assert "telecom" in patient
        assert "address" in patient

    def test_generate_batch(self):
        """Test generating multiple patients."""
        gen = PatientGenerator(seed=42)
        patients = gen.generate_batch(5)

        assert len(patients) == 5
        ids = {p["id"] for p in patients}
        assert len(ids) == 5  # All unique IDs

    def test_reproducible_with_seed(self):
        """Test that seed produces reproducible demographic patterns."""
        # Note: UUIDs are generated via uuid4() which is not seeded,
        # so we test reproducibility of demographic data instead
        gen1 = PatientGenerator(seed=42)
        gen2 = PatientGenerator(seed=42)

        patient1 = gen1.generate(patient_id="test-1")
        patient2 = gen2.generate(patient_id="test-2")

        # Same seed should produce same gender and similar demographic patterns
        assert patient1["gender"] == patient2["gender"]
        # Both should have same structure
        assert "name" in patient1 and "name" in patient2
        assert "birthDate" in patient1 and "birthDate" in patient2


class TestPractitionerGenerator:
    """Tests for PractitionerGenerator."""

    def test_generate_practitioner(self):
        """Test generating a practitioner."""
        gen = PractitionerGenerator(seed=42)
        practitioner = gen.generate()

        assert practitioner["resourceType"] == "Practitioner"
        assert "id" in practitioner
        assert "name" in practitioner
        assert "identifier" in practitioner  # NPI

    def test_practitioner_has_npi(self):
        """Test that practitioner has NPI identifier."""
        gen = PractitionerGenerator(seed=42)
        practitioner = gen.generate()

        npi_identifier = next(
            (i for i in practitioner["identifier"] if "npi" in i.get("system", "").lower()),
            None,
        )
        assert npi_identifier is not None


class TestOrganizationGenerator:
    """Tests for OrganizationGenerator."""

    def test_generate_organization(self):
        """Test generating an organization."""
        gen = OrganizationGenerator(seed=42)
        org = gen.generate()

        assert org["resourceType"] == "Organization"
        assert "id" in org
        assert "name" in org
        assert "type" in org


class TestEncounterGenerator:
    """Tests for EncounterGenerator."""

    def test_generate_encounter(self):
        """Test generating an encounter."""
        gen = EncounterGenerator(seed=42)
        encounter = gen.generate(patient_ref="Patient/123")

        assert encounter["resourceType"] == "Encounter"
        assert "id" in encounter
        assert "status" in encounter
        assert "class" in encounter
        assert "period" in encounter
        assert encounter["subject"]["reference"] == "Patient/123"

    def test_encounter_has_valid_class(self):
        """Test that encounter has valid class code."""
        gen = EncounterGenerator(seed=42)
        encounter = gen.generate()

        valid_classes = ["AMB", "EMER", "IMP", "ACUTE", "OBSENC"]
        assert encounter["class"]["code"] in valid_classes


class TestConditionGenerator:
    """Tests for ConditionGenerator."""

    def test_generate_condition(self):
        """Test generating a condition."""
        gen = ConditionGenerator(seed=42)
        condition = gen.generate(patient_ref="Patient/123")

        assert condition["resourceType"] == "Condition"
        assert "id" in condition
        assert "clinicalStatus" in condition
        assert "verificationStatus" in condition
        assert "code" in condition
        assert condition["subject"]["reference"] == "Patient/123"

    def test_condition_has_snomed_code(self):
        """Test that condition has SNOMED code."""
        gen = ConditionGenerator(seed=42)
        condition = gen.generate()

        coding = condition["code"]["coding"][0]
        assert "http://snomed.info/sct" in coding["system"]


class TestObservationGenerator:
    """Tests for ObservationGenerator."""

    def test_generate_vital_sign(self):
        """Test generating a vital sign observation."""
        gen = ObservationGenerator(seed=42)
        obs = gen.generate(
            patient_ref="Patient/123",
            observation_type="vital-signs",
        )

        assert obs["resourceType"] == "Observation"
        assert "id" in obs
        assert "valueQuantity" in obs
        assert obs["category"][0]["coding"][0]["code"] == "vital-signs"

    def test_generate_lab_result(self):
        """Test generating a lab observation."""
        gen = ObservationGenerator(seed=42)
        obs = gen.generate(
            patient_ref="Patient/123",
            observation_type="laboratory",
        )

        assert obs["resourceType"] == "Observation"
        assert obs["category"][0]["coding"][0]["code"] == "laboratory"

    def test_observation_has_reference_range(self):
        """Test that observation has reference range."""
        gen = ObservationGenerator(seed=42)
        obs = gen.generate()

        assert "referenceRange" in obs
        assert "low" in obs["referenceRange"][0]
        assert "high" in obs["referenceRange"][0]

    def test_observation_has_interpretation(self):
        """Test that observation has interpretation."""
        gen = ObservationGenerator(seed=42)
        obs = gen.generate()

        assert "interpretation" in obs
        interp_code = obs["interpretation"][0]["coding"][0]["code"]
        assert interp_code in ["L", "N", "H"]


class TestMedicationRequestGenerator:
    """Tests for MedicationRequestGenerator."""

    def test_generate_medication_request(self):
        """Test generating a medication request."""
        gen = MedicationRequestGenerator(seed=42)
        med = gen.generate(patient_ref="Patient/123")

        assert med["resourceType"] == "MedicationRequest"
        assert "id" in med
        assert "status" in med
        assert "intent" in med
        assert "medicationCodeableConcept" in med
        assert med["subject"]["reference"] == "Patient/123"

    def test_medication_has_dosage(self):
        """Test that medication request has dosage instructions."""
        gen = MedicationRequestGenerator(seed=42)
        med = gen.generate()

        assert "dosageInstruction" in med
        assert len(med["dosageInstruction"]) > 0
        assert "text" in med["dosageInstruction"][0]


class TestProcedureGenerator:
    """Tests for ProcedureGenerator."""

    def test_generate_procedure(self):
        """Test generating a procedure."""
        gen = ProcedureGenerator(seed=42)
        proc = gen.generate(patient_ref="Patient/123")

        assert proc["resourceType"] == "Procedure"
        assert "id" in proc
        assert "status" in proc
        assert "code" in proc
        assert proc["subject"]["reference"] == "Patient/123"


class TestPatientRecordGenerator:
    """Tests for PatientRecordGenerator (orchestrator)."""

    def test_generate_patient_record(self):
        """Test generating a complete patient record."""
        gen = PatientRecordGenerator(seed=42)
        resources = gen.generate_patient_record(
            num_conditions=(1, 2),
            num_encounters=(1, 2),
            num_observations_per_encounter=(1, 2),
            num_medications=(1, 2),
            num_procedures=(0, 1),
        )

        assert len(resources) > 0

        # Check we have required resource types
        types = {r["resourceType"] for r in resources}
        assert "Patient" in types
        assert "Practitioner" in types
        assert "Organization" in types

    def test_generate_population(self):
        """Test generating a population of patients."""
        gen = PatientRecordGenerator(seed=42)
        resources = gen.generate_population(
            num_patients=3,
            num_conditions=(1, 1),
            num_encounters=(1, 1),
            num_observations_per_encounter=(1, 1),
            num_medications=(0, 0),
            num_procedures=(0, 0),
        )

        # Count patients
        patients = [r for r in resources if r["resourceType"] == "Patient"]
        assert len(patients) == 3

    def test_references_are_valid(self):
        """Test that resource references are valid."""
        gen = PatientRecordGenerator(seed=42)
        resources = gen.generate_patient_record()

        # Build index of resources
        resource_ids = {f"{r['resourceType']}/{r['id']}" for r in resources}

        # Check references in conditions
        conditions = [r for r in resources if r["resourceType"] == "Condition"]
        for condition in conditions:
            patient_ref = condition.get("subject", {}).get("reference")
            if patient_ref:
                assert patient_ref in resource_ids


class TestMedicationAdministrationGenerator:
    """Tests for MedicationAdministrationGenerator."""

    def test_generate_medication_administration(self):
        """Test generating a medication administration."""
        gen = MedicationAdministrationGenerator(seed=42)
        admin = gen.generate(patient_ref="Patient/123")

        assert admin["resourceType"] == "MedicationAdministration"
        assert "id" in admin
        assert "status" in admin
        assert "medicationCodeableConcept" in admin
        assert admin["subject"]["reference"] == "Patient/123"

    def test_medication_administration_has_dosage(self):
        """Test that medication administration has dosage."""
        gen = MedicationAdministrationGenerator(seed=42)
        admin = gen.generate()

        assert "dosage" in admin
        assert "dose" in admin["dosage"]

    def test_medication_administration_with_encounter(self):
        """Test medication administration with encounter reference."""
        gen = MedicationAdministrationGenerator(seed=42)
        admin = gen.generate(
            patient_ref="Patient/123",
            encounter_ref="Encounter/456",
        )

        assert admin["context"]["reference"] == "Encounter/456"


class TestMedicationStatementGenerator:
    """Tests for MedicationStatementGenerator."""

    def test_generate_medication_statement(self):
        """Test generating a medication statement."""
        gen = MedicationStatementGenerator(seed=42)
        stmt = gen.generate(patient_ref="Patient/123")

        assert stmt["resourceType"] == "MedicationStatement"
        assert "id" in stmt
        assert "status" in stmt
        assert "medicationCodeableConcept" in stmt
        assert stmt["subject"]["reference"] == "Patient/123"

    def test_medication_statement_has_dosage(self):
        """Test that medication statement has dosage."""
        gen = MedicationStatementGenerator(seed=42)
        stmt = gen.generate()

        assert "dosage" in stmt
        assert len(stmt["dosage"]) > 0


class TestFlagGenerator:
    """Tests for FlagGenerator."""

    def test_generate_flag(self):
        """Test generating a flag."""
        gen = FlagGenerator(seed=42)
        flag = gen.generate(patient_ref="Patient/123")

        assert flag["resourceType"] == "Flag"
        assert "id" in flag
        assert "status" in flag
        assert "category" in flag
        assert "code" in flag
        assert flag["subject"]["reference"] == "Patient/123"

    def test_flag_has_valid_status(self):
        """Test that flag has valid status."""
        gen = FlagGenerator(seed=42)
        flag = gen.generate()

        assert flag["status"] in ["active", "inactive", "entered-in-error"]

    def test_flag_has_period(self):
        """Test that flag has period."""
        gen = FlagGenerator(seed=42)
        flag = gen.generate()

        assert "period" in flag
        assert "start" in flag["period"]


class TestClinicalImpressionGenerator:
    """Tests for ClinicalImpressionGenerator."""

    def test_generate_clinical_impression(self):
        """Test generating a clinical impression."""
        gen = ClinicalImpressionGenerator(seed=42)
        impression = gen.generate(patient_ref="Patient/123")

        assert impression["resourceType"] == "ClinicalImpression"
        assert "id" in impression
        assert "status" in impression
        assert impression["subject"]["reference"] == "Patient/123"

    def test_clinical_impression_has_effective_datetime(self):
        """Test that clinical impression has effective datetime."""
        gen = ClinicalImpressionGenerator(seed=42)
        impression = gen.generate()

        assert "effectiveDateTime" in impression

    def test_clinical_impression_with_encounter(self):
        """Test clinical impression with encounter reference."""
        gen = ClinicalImpressionGenerator(seed=42)
        impression = gen.generate(
            patient_ref="Patient/123",
            encounter_ref="Encounter/456",
        )

        assert impression["encounter"]["reference"] == "Encounter/456"


class TestCommunicationGenerator:
    """Tests for CommunicationGenerator."""

    def test_generate_communication(self):
        """Test generating a communication."""
        gen = CommunicationGenerator(seed=42)
        comm = gen.generate(patient_ref="Patient/123")

        assert comm["resourceType"] == "Communication"
        assert "id" in comm
        assert "status" in comm
        assert "category" in comm
        assert comm["subject"]["reference"] == "Patient/123"

    def test_communication_has_payload(self):
        """Test that communication has payload."""
        gen = CommunicationGenerator(seed=42)
        comm = gen.generate()

        assert "payload" in comm
        assert len(comm["payload"]) > 0

    def test_communication_has_sent_time(self):
        """Test that communication has sent time."""
        gen = CommunicationGenerator(seed=42)
        comm = gen.generate()

        assert "sent" in comm


class TestNutritionOrderGenerator:
    """Tests for NutritionOrderGenerator."""

    def test_generate_nutrition_order(self):
        """Test generating a nutrition order."""
        gen = NutritionOrderGenerator(seed=42)
        order = gen.generate(patient_ref="Patient/123")

        assert order["resourceType"] == "NutritionOrder"
        assert "id" in order
        assert "status" in order
        assert "intent" in order
        assert order["patient"]["reference"] == "Patient/123"

    def test_nutrition_order_has_datetime(self):
        """Test that nutrition order has datetime."""
        gen = NutritionOrderGenerator(seed=42)
        order = gen.generate()

        assert "dateTime" in order

    def test_nutrition_order_has_oral_diet(self):
        """Test that nutrition order has oral diet."""
        gen = NutritionOrderGenerator(seed=42)
        order = gen.generate()

        assert "oralDiet" in order
        assert "type" in order["oralDiet"]


class TestSpecimenGenerator:
    """Tests for SpecimenGenerator."""

    def test_generate_specimen(self):
        """Test generating a specimen."""
        gen = SpecimenGenerator(seed=42)
        specimen = gen.generate(patient_ref="Patient/123")

        assert specimen["resourceType"] == "Specimen"
        assert "id" in specimen
        assert "status" in specimen
        assert "type" in specimen
        assert specimen["subject"]["reference"] == "Patient/123"

    def test_specimen_has_collection(self):
        """Test that specimen has collection info."""
        gen = SpecimenGenerator(seed=42)
        specimen = gen.generate()

        assert "collection" in specimen
        assert "collectedDateTime" in specimen["collection"]
        assert "bodySite" in specimen["collection"]

    def test_specimen_has_container(self):
        """Test that specimen has container info."""
        gen = SpecimenGenerator(seed=42)
        specimen = gen.generate()

        assert "container" in specimen
        assert len(specimen["container"]) > 0


class TestFamilyMemberHistoryGenerator:
    """Tests for FamilyMemberHistoryGenerator."""

    def test_generate_family_member_history(self):
        """Test generating a family member history."""
        gen = FamilyMemberHistoryGenerator(seed=42)
        history = gen.generate(patient_ref="Patient/123")

        assert history["resourceType"] == "FamilyMemberHistory"
        assert "id" in history
        assert "status" in history
        assert "relationship" in history
        assert history["patient"]["reference"] == "Patient/123"

    def test_family_member_history_has_sex(self):
        """Test that family member history has sex."""
        gen = FamilyMemberHistoryGenerator(seed=42)
        history = gen.generate()

        assert "sex" in history

    def test_family_member_history_has_age_or_deceased(self):
        """Test that family member history has age or deceased info."""
        gen = FamilyMemberHistoryGenerator(seed=42)
        history = gen.generate()

        assert "ageAge" in history or "deceasedAge" in history


class TestClinicalCodes:
    """Tests for clinical code templates."""

    def test_conditions_snomed_valid(self):
        """Test that condition codes are valid."""
        assert len(CONDITIONS_SNOMED) > 0
        for code in CONDITIONS_SNOMED:
            assert "code" in code
            assert "display" in code
            assert "system" in code

    def test_vital_signs_valid(self):
        """Test that vital sign templates are valid."""
        assert len(VITAL_SIGNS) > 0
        for vital in VITAL_SIGNS:
            assert "code" in vital
            assert "display" in vital
            assert "unit" in vital
            assert "normal_low" in vital
            assert "normal_high" in vital
            assert vital["normal_low"] < vital["normal_high"]

    def test_lab_tests_valid(self):
        """Test that lab test templates are valid."""
        assert len(LAB_TESTS) > 0
        for lab in LAB_TESTS:
            assert "code" in lab
            assert "display" in lab
            assert "unit" in lab
            assert "normal_low" in lab
            assert "normal_high" in lab

    def test_medications_rxnorm_valid(self):
        """Test that medication codes are valid."""
        assert len(MEDICATIONS_RXNORM) > 0
        for med in MEDICATIONS_RXNORM:
            assert "code" in med
            assert "display" in med
            assert "system" in med


class TestMedicationDispenseGenerator:
    """Tests for MedicationDispenseGenerator."""

    def test_generate_medication_dispense(self):
        """Test generating a medication dispense."""
        gen = MedicationDispenseGenerator(seed=42)
        dispense = gen.generate(patient_ref="Patient/123")

        assert dispense["resourceType"] == "MedicationDispense"
        assert "id" in dispense
        assert "status" in dispense
        assert dispense["subject"]["reference"] == "Patient/123"

    def test_medication_dispense_has_quantity(self):
        """Test that medication dispense has quantity."""
        gen = MedicationDispenseGenerator(seed=42)
        dispense = gen.generate()

        assert "quantity" in dispense
        assert "value" in dispense["quantity"]
        assert "unit" in dispense["quantity"]

    def test_medication_dispense_has_days_supply(self):
        """Test that medication dispense has days supply."""
        gen = MedicationDispenseGenerator(seed=42)
        dispense = gen.generate()

        assert "daysSupply" in dispense
        assert "value" in dispense["daysSupply"]


class TestHealthcareServiceGenerator:
    """Tests for HealthcareServiceGenerator."""

    def test_generate_healthcare_service(self):
        """Test generating a healthcare service."""
        gen = HealthcareServiceGenerator(seed=42)
        service = gen.generate()

        assert service["resourceType"] == "HealthcareService"
        assert "id" in service
        assert "active" in service
        assert "name" in service

    def test_healthcare_service_has_category(self):
        """Test that healthcare service has category."""
        gen = HealthcareServiceGenerator(seed=42)
        service = gen.generate()

        assert "category" in service
        assert len(service["category"]) > 0

    def test_healthcare_service_with_organization(self):
        """Test healthcare service with organization reference."""
        gen = HealthcareServiceGenerator(seed=42)
        service = gen.generate(organization_ref="Organization/456")

        assert service["providedBy"]["reference"] == "Organization/456"


class TestMediaGenerator:
    """Tests for MediaGenerator."""

    def test_generate_media(self):
        """Test generating a media resource."""
        gen = MediaGenerator(seed=42)
        media = gen.generate(patient_ref="Patient/123")

        assert media["resourceType"] == "Media"
        assert "id" in media
        assert "status" in media
        assert media["subject"]["reference"] == "Patient/123"

    def test_media_has_content(self):
        """Test that media has content."""
        gen = MediaGenerator(seed=42)
        media = gen.generate()

        assert "content" in media
        assert "contentType" in media["content"]

    def test_media_has_type(self):
        """Test that media has type."""
        gen = MediaGenerator(seed=42)
        media = gen.generate()

        assert "type" in media


class TestRiskAssessmentGenerator:
    """Tests for RiskAssessmentGenerator."""

    def test_generate_risk_assessment(self):
        """Test generating a risk assessment."""
        gen = RiskAssessmentGenerator(seed=42)
        assessment = gen.generate(patient_ref="Patient/123")

        assert assessment["resourceType"] == "RiskAssessment"
        assert "id" in assessment
        assert "status" in assessment
        assert assessment["subject"]["reference"] == "Patient/123"

    def test_risk_assessment_has_prediction(self):
        """Test that risk assessment has prediction."""
        gen = RiskAssessmentGenerator(seed=42)
        assessment = gen.generate()

        assert "prediction" in assessment
        assert len(assessment["prediction"]) > 0

    def test_risk_assessment_has_occurrence(self):
        """Test that risk assessment has occurrence datetime."""
        gen = RiskAssessmentGenerator(seed=42)
        assessment = gen.generate()

        assert "occurrenceDateTime" in assessment


class TestDetectedIssueGenerator:
    """Tests for DetectedIssueGenerator."""

    def test_generate_detected_issue(self):
        """Test generating a detected issue."""
        gen = DetectedIssueGenerator(seed=42)
        issue = gen.generate(patient_ref="Patient/123")

        assert issue["resourceType"] == "DetectedIssue"
        assert "id" in issue
        assert "status" in issue
        assert issue["patient"]["reference"] == "Patient/123"

    def test_detected_issue_has_severity(self):
        """Test that detected issue has severity."""
        gen = DetectedIssueGenerator(seed=42)
        issue = gen.generate()

        assert "severity" in issue

    def test_detected_issue_has_code(self):
        """Test that detected issue has code."""
        gen = DetectedIssueGenerator(seed=42)
        issue = gen.generate()

        assert "code" in issue


class TestAdverseEventGenerator:
    """Tests for AdverseEventGenerator."""

    def test_generate_adverse_event(self):
        """Test generating an adverse event."""
        gen = AdverseEventGenerator(seed=42)
        event = gen.generate(patient_ref="Patient/123")

        assert event["resourceType"] == "AdverseEvent"
        assert "id" in event
        assert "actuality" in event
        assert event["subject"]["reference"] == "Patient/123"

    def test_adverse_event_has_category(self):
        """Test that adverse event has category."""
        gen = AdverseEventGenerator(seed=42)
        event = gen.generate()

        assert "category" in event
        assert len(event["category"]) > 0

    def test_adverse_event_has_outcome(self):
        """Test that adverse event has outcome."""
        gen = AdverseEventGenerator(seed=42)
        event = gen.generate()

        assert "outcome" in event


class TestProvenanceGenerator:
    """Tests for ProvenanceGenerator."""

    def test_generate_provenance(self):
        """Test generating a provenance resource."""
        gen = ProvenanceGenerator(seed=42)
        provenance = gen.generate(target_ref="Patient/123")

        assert provenance["resourceType"] == "Provenance"
        assert "id" in provenance
        assert "target" in provenance
        assert provenance["target"][0]["reference"] == "Patient/123"

    def test_provenance_has_agent(self):
        """Test that provenance has agent."""
        gen = ProvenanceGenerator(seed=42)
        provenance = gen.generate()

        assert "agent" in provenance
        assert len(provenance["agent"]) > 0

    def test_provenance_has_recorded(self):
        """Test that provenance has recorded timestamp."""
        gen = ProvenanceGenerator(seed=42)
        provenance = gen.generate()

        assert "recorded" in provenance


class TestAuditEventGenerator:
    """Tests for AuditEventGenerator."""

    def test_generate_audit_event(self):
        """Test generating an audit event."""
        gen = AuditEventGenerator(seed=42)
        event = gen.generate()

        assert event["resourceType"] == "AuditEvent"
        assert "id" in event
        assert "type" in event
        assert "action" in event

    def test_audit_event_has_agent(self):
        """Test that audit event has agent."""
        gen = AuditEventGenerator(seed=42)
        event = gen.generate()

        assert "agent" in event
        assert len(event["agent"]) > 0

    def test_audit_event_has_source(self):
        """Test that audit event has source."""
        gen = AuditEventGenerator(seed=42)
        event = gen.generate()

        assert "source" in event
        assert "observer" in event["source"]

    def test_audit_event_has_outcome(self):
        """Test that audit event has outcome."""
        gen = AuditEventGenerator(seed=42)
        event = gen.generate()

        assert "outcome" in event
