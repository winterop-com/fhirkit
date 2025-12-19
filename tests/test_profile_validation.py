"""Tests for FHIR profile validation against StructureDefinition."""

import pytest

from fhirkit.server.storage.fhir_store import FHIRStore
from fhirkit.server.validation import ProfileValidator, ValidationResult


class TestProfileValidator:
    """Tests for ProfileValidator class."""

    @pytest.fixture
    def store(self):
        """Create a test FHIR store."""
        return FHIRStore()

    @pytest.fixture
    def validator(self, store):
        """Create a profile validator."""
        return ProfileValidator(store)

    @pytest.fixture
    def simple_patient_profile(self):
        """Create a simple Patient profile requiring identifier and name."""
        return {
            "resourceType": "StructureDefinition",
            "id": "simple-patient",
            "url": "http://example.org/fhir/StructureDefinition/simple-patient",
            "name": "SimplePatient",
            "status": "active",
            "kind": "resource",
            "abstract": False,
            "type": "Patient",
            "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
            "derivation": "constraint",
            "snapshot": {
                "element": [
                    {"id": "Patient", "path": "Patient", "min": 0, "max": "*"},
                    {"id": "Patient.identifier", "path": "Patient.identifier", "min": 1, "max": "*"},
                    {"id": "Patient.name", "path": "Patient.name", "min": 1, "max": "*"},
                    {"id": "Patient.name.family", "path": "Patient.name.family", "min": 1, "max": "1"},
                ]
            },
        }

    @pytest.fixture
    def observation_profile(self):
        """Create an Observation profile with fixed status."""
        return {
            "resourceType": "StructureDefinition",
            "id": "vital-signs",
            "url": "http://example.org/fhir/StructureDefinition/vital-signs",
            "name": "VitalSigns",
            "status": "active",
            "kind": "resource",
            "abstract": False,
            "type": "Observation",
            "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Observation",
            "derivation": "constraint",
            "snapshot": {
                "element": [
                    {"id": "Observation", "path": "Observation", "min": 0, "max": "*"},
                    {
                        "id": "Observation.status",
                        "path": "Observation.status",
                        "min": 1,
                        "max": "1",
                        "fixedCode": "final",
                    },
                    {"id": "Observation.category", "path": "Observation.category", "min": 1, "max": "*"},
                    {"id": "Observation.code", "path": "Observation.code", "min": 1, "max": "1"},
                    {"id": "Observation.subject", "path": "Observation.subject", "min": 1, "max": "1"},
                ]
            },
        }

    def test_profile_not_found(self, validator):
        """Test validation when profile is not found."""
        resource = {"resourceType": "Patient", "id": "test"}

        result = validator.validate_against_profile(
            resource,
            "http://example.org/fhir/StructureDefinition/nonexistent",
        )

        assert not result.valid
        assert any(issue.code == "not-found" for issue in result.issues)

    def test_resource_type_mismatch(self, store, validator, simple_patient_profile):
        """Test validation when resource type doesn't match profile."""
        store.create(simple_patient_profile)

        observation = {
            "resourceType": "Observation",
            "id": "obs-001",
            "status": "final",
            "code": {"text": "test"},
        }

        result = validator.validate_against_profile(
            observation,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        assert not result.valid
        assert any(issue.code == "invalid" for issue in result.issues)

    def test_valid_resource(self, store, validator, simple_patient_profile):
        """Test validation of a valid resource."""
        store.create(simple_patient_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "identifier": [{"system": "http://hospital.org", "value": "12345"}],
            "name": [{"family": "Smith", "given": ["John"]}],
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        assert result.valid

    def test_missing_required_element(self, store, validator, simple_patient_profile):
        """Test validation detects missing required element."""
        store.create(simple_patient_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "name": [{"family": "Smith"}],
            # Missing identifier (required by profile)
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        assert not result.valid
        assert any("identifier" in issue.message for issue in result.issues)

    def test_cardinality_min_violation(self, store, validator, simple_patient_profile):
        """Test validation detects minimum cardinality violation."""
        store.create(simple_patient_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "identifier": [{"value": "12345"}],
            # Missing name (required by profile)
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        assert not result.valid
        assert any("name" in issue.message and "minimum" in issue.message for issue in result.issues)

    def test_fixed_value_validation(self, store, validator, observation_profile):
        """Test validation of fixed values."""
        store.create(observation_profile)

        observation = {
            "resourceType": "Observation",
            "id": "obs-001",
            "status": "preliminary",  # Should be "final" per profile
            "category": [{"text": "vital-signs"}],
            "code": {"text": "BP"},
            "subject": {"reference": "Patient/123"},
        }

        result = validator.validate_against_profile(
            observation,
            "http://example.org/fhir/StructureDefinition/vital-signs",
        )

        assert not result.valid
        assert any("status" in issue.message and "fixed" in issue.message.lower() for issue in result.issues)

    def test_valid_fixed_value(self, store, validator, observation_profile):
        """Test valid fixed value passes validation."""
        store.create(observation_profile)

        observation = {
            "resourceType": "Observation",
            "id": "obs-001",
            "status": "final",
            "category": [{"text": "vital-signs"}],
            "code": {"text": "BP"},
            "subject": {"reference": "Patient/123"},
        }

        result = validator.validate_against_profile(
            observation,
            "http://example.org/fhir/StructureDefinition/vital-signs",
        )

        assert result.valid

    def test_profile_with_version(self, store, validator, simple_patient_profile):
        """Test loading profile with version in URL."""
        profile = simple_patient_profile.copy()
        profile["version"] = "1.0.0"
        store.create(profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "identifier": [{"value": "12345"}],
            "name": [{"family": "Smith"}],
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient|1.0.0",
        )

        assert result.valid

    def test_profile_cache(self, store, validator, simple_patient_profile):
        """Test that profiles are cached."""
        store.create(simple_patient_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "identifier": [{"value": "12345"}],
            "name": [{"family": "Smith"}],
        }

        # First call loads profile
        validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        # Check cache
        assert "http://example.org/fhir/StructureDefinition/simple-patient" in validator._profile_cache

        # Second call uses cache
        validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

    def test_clear_cache(self, store, validator, simple_patient_profile):
        """Test clearing the profile cache."""
        store.create(simple_patient_profile)

        patient = {"resourceType": "Patient", "identifier": [{}], "name": [{"family": "X"}]}
        validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/simple-patient",
        )

        assert len(validator._profile_cache) > 0

        validator.clear_cache()

        assert len(validator._profile_cache) == 0


class TestPatternValidation:
    """Tests for pattern[x] validation."""

    @pytest.fixture
    def store(self):
        return FHIRStore()

    @pytest.fixture
    def validator(self, store):
        return ProfileValidator(store)

    @pytest.fixture
    def pattern_profile(self):
        """Create a profile with pattern constraint."""
        return {
            "resourceType": "StructureDefinition",
            "id": "pattern-obs",
            "url": "http://example.org/fhir/StructureDefinition/pattern-obs",
            "name": "PatternObs",
            "status": "active",
            "kind": "resource",
            "abstract": False,
            "type": "Observation",
            "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Observation",
            "derivation": "constraint",
            "snapshot": {
                "element": [
                    {"id": "Observation", "path": "Observation", "min": 0, "max": "*"},
                    {
                        "id": "Observation.category",
                        "path": "Observation.category",
                        "min": 1,
                        "max": "*",
                        "patternCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "vital-signs",
                                }
                            ]
                        },
                    },
                ]
            },
        }

    def test_pattern_match(self, store, validator, pattern_profile):
        """Test resource matching pattern."""
        store.create(pattern_profile)

        observation = {
            "resourceType": "Observation",
            "id": "obs-001",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                        }
                    ]
                }
            ],
            "code": {"text": "BP"},
        }

        result = validator.validate_against_profile(
            observation,
            "http://example.org/fhir/StructureDefinition/pattern-obs",
        )

        assert result.valid

    def test_pattern_mismatch(self, store, validator, pattern_profile):
        """Test resource not matching pattern."""
        store.create(pattern_profile)

        observation = {
            "resourceType": "Observation",
            "id": "obs-001",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",  # Wrong code
                        }
                    ]
                }
            ],
            "code": {"text": "Lab test"},
        }

        result = validator.validate_against_profile(
            observation,
            "http://example.org/fhir/StructureDefinition/pattern-obs",
        )

        assert not result.valid
        assert any("pattern" in issue.message.lower() for issue in result.issues)


class TestChoiceTypeValidation:
    """Tests for choice type (e.g., deceased[x]) validation."""

    @pytest.fixture
    def store(self):
        return FHIRStore()

    @pytest.fixture
    def validator(self, store):
        return ProfileValidator(store)

    @pytest.fixture
    def choice_profile(self):
        """Create a profile with choice type element."""
        return {
            "resourceType": "StructureDefinition",
            "id": "choice-patient",
            "url": "http://example.org/fhir/StructureDefinition/choice-patient",
            "name": "ChoicePatient",
            "status": "active",
            "kind": "resource",
            "abstract": False,
            "type": "Patient",
            "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
            "derivation": "constraint",
            "snapshot": {
                "element": [
                    {"id": "Patient", "path": "Patient", "min": 0, "max": "*"},
                    {"id": "Patient.deceased[x]", "path": "Patient.deceased[x]", "min": 1, "max": "1"},
                ]
            },
        }

    def test_choice_type_boolean(self, store, validator, choice_profile):
        """Test choice type with boolean value."""
        store.create(choice_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "deceasedBoolean": False,
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/choice-patient",
        )

        assert result.valid

    def test_choice_type_datetime(self, store, validator, choice_profile):
        """Test choice type with dateTime value."""
        store.create(choice_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "deceasedDateTime": "2023-01-15",
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/choice-patient",
        )

        assert result.valid

    def test_choice_type_missing(self, store, validator, choice_profile):
        """Test missing required choice type element."""
        store.create(choice_profile)

        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            # Missing deceased[x]
        }

        result = validator.validate_against_profile(
            patient,
            "http://example.org/fhir/StructureDefinition/choice-patient",
        )

        assert not result.valid
        assert any("deceased" in issue.message for issue in result.issues)


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(valid=True, issues=[])
        assert result.valid
        assert len(result.issues) == 0

    def test_invalid_result(self):
        """Test creating an invalid result with issues."""
        from fhirkit.server.validation import ValidationIssue

        issues = [
            ValidationIssue(
                severity="error",
                code="required",
                location="identifier",
                message="Element 'identifier' is required",
            )
        ]
        result = ValidationResult(valid=False, issues=issues)

        assert not result.valid
        assert len(result.issues) == 1
        assert result.issues[0].severity == "error"

    def test_result_to_operation_outcome(self):
        """Test converting result to OperationOutcome."""
        from fhirkit.server.validation import ValidationIssue

        issues = [
            ValidationIssue(
                severity="error",
                code="required",
                location="identifier",
                message="Element 'identifier' is required",
            ),
            ValidationIssue(
                severity="warning",
                code="value",
                location="name",
                message="Name should have family",
            ),
        ]
        result = ValidationResult(valid=False, issues=issues)

        outcome = result.to_operation_outcome()

        assert outcome["resourceType"] == "OperationOutcome"
        assert len(outcome["issue"]) == 2
        assert outcome["issue"][0]["severity"] == "error"
        assert outcome["issue"][1]["severity"] == "warning"
