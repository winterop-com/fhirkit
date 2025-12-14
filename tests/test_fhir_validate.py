"""Tests for the FHIR $validate operation."""

import pytest

from fhirkit.server.validation import FHIRValidator, ValidationIssue, ValidationResult
from fhirkit.server.validation.rules import RESOURCE_RULES, VALID_RESOURCE_TYPES

# =============================================================================
# Unit Tests for FHIRValidator
# =============================================================================


class TestFHIRValidator:
    """Unit tests for the FHIRValidator class."""

    def test_valid_patient(self):
        """Test validation of a valid Patient resource."""
        validator = FHIRValidator()
        patient = {
            "resourceType": "Patient",
            "id": "123",
            "name": [{"family": "Smith", "given": ["John"]}],
            "gender": "male",
        }
        result = validator.validate(patient)

        assert result.valid is True
        assert len(result.issues) == 0

    def test_missing_resource_type(self):
        """Test validation fails for missing resourceType."""
        validator = FHIRValidator()
        resource = {"id": "123", "name": [{"family": "Smith"}]}
        result = validator.validate(resource)

        assert result.valid is False
        assert len(result.issues) == 1
        assert result.issues[0].code == "required"
        assert "resourceType" in result.issues[0].message

    def test_invalid_resource_type(self):
        """Test validation fails for invalid resourceType."""
        validator = FHIRValidator()
        resource = {"resourceType": "InvalidType", "id": "123"}
        result = validator.validate(resource)

        assert result.valid is False
        assert len(result.issues) == 1
        assert result.issues[0].code == "invalid"
        assert "InvalidType" in result.issues[0].message

    def test_observation_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        validator = FHIRValidator()
        observation = {"resourceType": "Observation", "id": "123"}
        result = validator.validate(observation)

        assert result.valid is False
        # Should have errors for missing status and code
        error_messages = [i.message for i in result.issues if i.severity == "error"]
        assert any("status" in msg for msg in error_messages)
        assert any("code" in msg for msg in error_messages)

    def test_observation_with_required_fields(self):
        """Test validation passes with all required fields."""
        validator = FHIRValidator()
        observation = {
            "resourceType": "Observation",
            "id": "123",
            "status": "final",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
        }
        result = validator.validate(observation)

        assert result.valid is True
        assert len(result.issues) == 0

    def test_invalid_code_binding_required(self):
        """Test validation fails for invalid code value with required binding."""
        validator = FHIRValidator()
        observation = {
            "resourceType": "Observation",
            "id": "123",
            "status": "invalid-status",  # Invalid status
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
        }
        result = validator.validate(observation)

        assert result.valid is False
        assert any(i.code == "code-invalid" for i in result.issues)
        assert any("invalid-status" in i.message for i in result.issues)

    def test_valid_observation_status_values(self):
        """Test all valid observation status values pass validation."""
        validator = FHIRValidator()
        valid_statuses = [
            "registered",
            "preliminary",
            "final",
            "amended",
            "corrected",
            "cancelled",
            "entered-in-error",
            "unknown",
        ]

        for status in valid_statuses:
            observation = {
                "resourceType": "Observation",
                "status": status,
                "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
            }
            result = validator.validate(observation)
            assert result.valid is True, f"Status '{status}' should be valid"

    def test_invalid_patient_gender(self):
        """Test validation fails for invalid gender value."""
        validator = FHIRValidator()
        patient = {"resourceType": "Patient", "gender": "invalid"}
        result = validator.validate(patient)

        assert result.valid is False
        assert any("gender" in i.message for i in result.issues)

    def test_valid_patient_gender_values(self):
        """Test all valid gender values pass validation."""
        validator = FHIRValidator()
        valid_genders = ["male", "female", "other", "unknown"]

        for gender in valid_genders:
            patient = {"resourceType": "Patient", "gender": gender}
            result = validator.validate(patient)
            assert result.valid is True, f"Gender '{gender}' should be valid"

    def test_condition_required_subject(self):
        """Test Condition requires subject."""
        validator = FHIRValidator()
        condition = {"resourceType": "Condition", "id": "123"}
        result = validator.validate(condition)

        assert result.valid is False
        assert any("subject" in i.message for i in result.issues)

    def test_condition_with_subject(self):
        """Test Condition is valid with subject."""
        validator = FHIRValidator()
        condition = {
            "resourceType": "Condition",
            "id": "123",
            "subject": {"reference": "Patient/123"},
        }
        result = validator.validate(condition)

        assert result.valid is True

    def test_condition_clinical_status_validation(self):
        """Test Condition clinicalStatus code validation."""
        validator = FHIRValidator()

        # Valid clinical status
        condition = {
            "resourceType": "Condition",
            "subject": {"reference": "Patient/123"},
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                    }
                ]
            },
        }
        result = validator.validate(condition)
        assert result.valid is True

        # Invalid clinical status
        condition["clinicalStatus"]["coding"][0]["code"] = "invalid"
        result = validator.validate(condition)
        assert result.valid is False
        assert any("clinicalStatus" in i.location for i in result.issues)

    def test_medication_request_required_fields(self):
        """Test MedicationRequest requires status, intent, medication[x], subject."""
        validator = FHIRValidator()
        med_request = {"resourceType": "MedicationRequest", "id": "123"}
        result = validator.validate(med_request)

        assert result.valid is False
        error_messages = [i.message for i in result.issues if i.severity == "error"]
        assert any("status" in msg for msg in error_messages)
        assert any("intent" in msg for msg in error_messages)
        assert any("subject" in msg for msg in error_messages)
        assert any("medication" in msg for msg in error_messages)

    def test_medication_request_with_medication_reference(self):
        """Test MedicationRequest with medicationReference."""
        validator = FHIRValidator()
        med_request = {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "medicationReference": {"reference": "Medication/123"},
            "subject": {"reference": "Patient/123"},
        }
        result = validator.validate(med_request)

        assert result.valid is True

    def test_medication_request_with_medication_codeable_concept(self):
        """Test MedicationRequest with medicationCodeableConcept."""
        validator = FHIRValidator()
        med_request = {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": {"coding": [{"system": "http://snomed.info/sct", "code": "123456"}]},
            "subject": {"reference": "Patient/123"},
        }
        result = validator.validate(med_request)

        assert result.valid is True

    def test_encounter_required_fields(self):
        """Test Encounter requires status and class."""
        validator = FHIRValidator()
        encounter = {"resourceType": "Encounter", "id": "123"}
        result = validator.validate(encounter)

        assert result.valid is False
        error_messages = [i.message for i in result.issues if i.severity == "error"]
        assert any("status" in msg for msg in error_messages)
        assert any("class" in msg for msg in error_messages)

    def test_valid_encounter(self):
        """Test valid Encounter passes validation."""
        validator = FHIRValidator()
        encounter = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
            },
        }
        result = validator.validate(encounter)

        assert result.valid is True


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_to_operation_outcome_valid(self):
        """Test converting valid result to OperationOutcome."""
        result = ValidationResult(valid=True, issues=[])
        outcome = result.to_operation_outcome()

        assert outcome["resourceType"] == "OperationOutcome"
        assert outcome["issue"] == []

    def test_to_operation_outcome_with_issues(self):
        """Test converting result with issues to OperationOutcome."""
        issues = [
            ValidationIssue(
                severity="error",
                code="required",
                location="Observation.status",
                message="Missing required field: status",
            ),
            ValidationIssue(
                severity="warning",
                code="code-invalid",
                location="Patient.gender",
                message="Invalid code value",
            ),
        ]
        result = ValidationResult(valid=False, issues=issues)
        outcome = result.to_operation_outcome()

        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 2
        assert outcome["issue"][0]["severity"] == "error"
        assert outcome["issue"][0]["code"] == "required"
        assert outcome["issue"][0]["location"] == ["Observation.status"]
        assert outcome["issue"][0]["diagnostics"] == "Missing required field: status"
        assert outcome["issue"][1]["severity"] == "warning"


class TestReferenceValidation:
    """Tests for reference validation."""

    def test_reference_validation_with_store(self):
        """Test reference validation checks references exist."""
        from fhirkit.server.storage.fhir_store import FHIRStore

        store = FHIRStore()
        # Create a patient for reference
        store.create({"resourceType": "Patient", "id": "123"})

        validator = FHIRValidator(store)
        condition = {
            "resourceType": "Condition",
            "subject": {"reference": "Patient/123"},
        }
        result = validator.validate(condition)

        assert result.valid is True

    def test_reference_validation_nonexistent(self):
        """Test reference validation warns for nonexistent references."""
        from fhirkit.server.storage.fhir_store import FHIRStore

        store = FHIRStore()
        validator = FHIRValidator(store)

        condition = {
            "resourceType": "Condition",
            "subject": {"reference": "Patient/nonexistent"},
        }
        result = validator.validate(condition)

        # Should have a warning for missing reference
        assert any(i.code == "not-found" for i in result.issues)
        assert any("Patient/nonexistent" in i.message for i in result.issues)

    def test_external_references_not_validated(self):
        """Test external URLs are not validated against store."""
        from fhirkit.server.storage.fhir_store import FHIRStore

        store = FHIRStore()
        validator = FHIRValidator(store)

        condition = {
            "resourceType": "Condition",
            "subject": {"reference": "https://external.example.com/Patient/123"},
        }
        result = validator.validate(condition)

        # Should not have a not-found warning for external reference
        assert not any(i.code == "not-found" for i in result.issues)


class TestResourceRules:
    """Tests for resource validation rules."""

    def test_all_supported_types_have_rules(self):
        """Test that all supported types have validation rules defined."""
        from fhirkit.server.api.routes import SUPPORTED_TYPES

        for resource_type in SUPPORTED_TYPES:
            # All types should be in VALID_RESOURCE_TYPES or have rules
            assert resource_type in VALID_RESOURCE_TYPES or resource_type in RESOURCE_RULES, (
                f"Missing rules for {resource_type}"
            )

    def test_bundle_validation(self):
        """Test Bundle requires type."""
        validator = FHIRValidator()
        bundle = {"resourceType": "Bundle", "id": "123"}
        result = validator.validate(bundle)

        assert result.valid is False
        assert any("type" in i.message for i in result.issues)

    def test_valid_bundle(self):
        """Test valid Bundle passes validation."""
        validator = FHIRValidator()
        bundle = {"resourceType": "Bundle", "type": "collection"}
        result = validator.validate(bundle)

        assert result.valid is True

    def test_library_required_fields(self):
        """Test Library requires status and type."""
        validator = FHIRValidator()
        library = {"resourceType": "Library", "id": "123"}
        result = validator.validate(library)

        assert result.valid is False
        error_messages = [i.message for i in result.issues if i.severity == "error"]
        assert any("status" in msg for msg in error_messages)
        assert any("type" in msg for msg in error_messages)


# =============================================================================
# Integration Tests for $validate Endpoint
# =============================================================================


@pytest.fixture
def client():
    """Create a test client."""
    from fastapi.testclient import TestClient

    from fhirkit.server.api.app import create_app
    from fhirkit.server.config.settings import FHIRServerSettings

    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings)
    return TestClient(app)


class TestValidateEndpoint:
    """Integration tests for the $validate endpoint."""

    def test_validate_valid_patient(self, client):
        """Test validating a valid Patient resource."""
        response = client.post(
            "/Patient/$validate",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Smith", "given": ["John"]}],
                "gender": "male",
            },
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 0

    def test_validate_invalid_observation(self, client):
        """Test validating an invalid Observation resource."""
        response = client.post(
            "/Observation/$validate",
            json={"resourceType": "Observation"},
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        # Should have errors for missing status and code
        assert len(outcome["issue"]) >= 2
        assert any(i["severity"] == "error" for i in outcome["issue"])

    def test_validate_wrong_resource_type(self, client):
        """Test validating with wrong resource type."""
        response = client.post(
            "/Patient/$validate",
            json={"resourceType": "Observation", "status": "final"},
        )

        assert response.status_code == 400
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert any("does not match" in i.get("diagnostics", "") for i in outcome["issue"])

    def test_validate_unsupported_resource_type(self, client):
        """Test validating unsupported resource type."""
        response = client.post(
            "/InvalidType/$validate",
            json={"resourceType": "InvalidType"},
        )

        assert response.status_code == 400
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert any("not supported" in i.get("diagnostics", "") for i in outcome["issue"])

    def test_validate_with_parameters_wrapper(self, client):
        """Test validating with Parameters wrapper."""
        response = client.post(
            "/Patient/$validate",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "resource",
                        "resource": {
                            "resourceType": "Patient",
                            "name": [{"family": "Smith"}],
                        },
                    }
                ],
            },
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 0

    def test_validate_existing_resource_get(self, client):
        """Test validating existing resource via GET."""
        # First create a patient
        create_response = client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "Smith"}]},
        )
        patient = create_response.json()
        patient_id = patient["id"]

        # Validate via GET
        response = client.get(f"/Patient/{patient_id}/$validate")

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 0

    def test_validate_existing_resource_post(self, client):
        """Test validating existing resource via POST."""
        # First create a patient
        create_response = client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "Smith"}]},
        )
        patient = create_response.json()
        patient_id = patient["id"]

        # Validate via POST
        response = client.post(f"/Patient/{patient_id}/$validate")

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 0

    def test_validate_nonexistent_resource(self, client):
        """Test validating nonexistent resource returns 404."""
        response = client.get("/Patient/nonexistent/$validate")

        assert response.status_code == 404
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"

    def test_validate_invalid_json(self, client):
        """Test validating with invalid JSON."""
        response = client.post(
            "/Patient/$validate",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert any("Invalid JSON" in i.get("diagnostics", "") for i in outcome["issue"])

    def test_validate_with_invalid_code_binding(self, client):
        """Test validation returns error for invalid code value."""
        response = client.post(
            "/Observation/$validate",
            json={
                "resourceType": "Observation",
                "status": "invalid-status",
                "code": {"coding": [{"code": "8480-6"}]},
            },
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert any("invalid-status" in i.get("diagnostics", "") for i in outcome["issue"])

    def test_validate_reference_to_nonexistent_resource(self, client):
        """Test validation warns about nonexistent references."""
        response = client.post(
            "/Condition/$validate",
            json={
                "resourceType": "Condition",
                "subject": {"reference": "Patient/nonexistent"},
            },
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        # Should have warning for missing reference
        assert any(
            i.get("severity") == "warning" and "not found" in i.get("diagnostics", "").lower() for i in outcome["issue"]
        )

    def test_validate_condition_with_valid_clinical_status(self, client):
        """Test validating Condition with valid clinical status."""
        response = client.post(
            "/Condition/$validate",
            json={
                "resourceType": "Condition",
                "subject": {"reference": "Patient/123"},
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active",
                        }
                    ]
                },
            },
        )

        assert response.status_code == 200
        outcome = response.json()
        # Validation passes for structure (reference warning is separate)
        errors = [i for i in outcome["issue"] if i["severity"] == "error"]
        assert len(errors) == 0

    def test_validate_mode_parameter(self, client):
        """Test that mode parameter is accepted."""
        response = client.post(
            "/Patient/$validate?mode=create",
            json={"resourceType": "Patient", "name": [{"family": "Smith"}]},
        )

        assert response.status_code == 200
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
