"""Tests for CDS Hooks CQL executor."""

from pathlib import Path
from uuid import uuid4

import pytest

from fhirkit.cds_hooks.config.settings import CDSHooksSettings, CDSServiceConfig
from fhirkit.cds_hooks.models.request import CDSRequest
from fhirkit.cds_hooks.service.executor import CDSExecutor


@pytest.fixture
def tmp_cql_library(tmp_path: Path) -> Path:
    """Create a temporary CQL library file."""
    cql_content = """
library TestLibrary version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "Greeting":
  'Hello, World!'

define "Sum":
  1 + 2 + 3

define "HasValue":
  true

define "EmptyList":
  {}

define "NumberList":
  {1, 2, 3, 4, 5}

define "PatientName":
  Patient.name.first().given.first()
"""
    lib_path = tmp_path / "test_library.cql"
    lib_path.write_text(cql_content)
    return lib_path


@pytest.fixture
def cds_settings(tmp_path: Path, tmp_cql_library: Path) -> CDSHooksSettings:
    """Create CDS settings with temp paths."""
    return CDSHooksSettings(
        services_config_path=str(tmp_path / "config.yaml"),
        cql_library_path=str(tmp_path),
    )


@pytest.fixture
def sample_service_config(tmp_cql_library: Path) -> CDSServiceConfig:
    """Create a sample service configuration."""
    return CDSServiceConfig(
        id="test-service",
        hook="patient-view",
        title="Test Service",
        description="Test description",
        cqlLibrary=str(tmp_cql_library),
        evaluateDefinitions=["Greeting", "Sum", "HasValue"],
    )


@pytest.fixture
def executor(cds_settings: CDSHooksSettings) -> CDSExecutor:
    """Create a CDS executor."""
    return CDSExecutor(cds_settings)


@pytest.fixture
def sample_request() -> CDSRequest:
    """Create a sample CDS request."""
    return CDSRequest(
        hook="patient-view",
        hookInstance=uuid4(),
        context={"patientId": "test-patient", "userId": "test-user"},
    )


@pytest.fixture
def request_with_prefetch() -> CDSRequest:
    """Create a CDS request with prefetch data."""
    return CDSRequest(
        hook="patient-view",
        hookInstance=uuid4(),
        context={"patientId": "patient-123", "userId": "user-456"},
        prefetch={
            "patient": {
                "resourceType": "Patient",
                "id": "patient-123",
                "name": [{"given": ["John"], "family": "Smith"}],
            },
            "conditions": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Condition",
                            "id": "cond-1",
                            "code": {"coding": [{"code": "diabetes"}]},
                        }
                    }
                ],
            },
        },
    )


# =============================================================================
# CQL Library Loading Tests
# =============================================================================


class TestCQLLibraryLoading:
    """Tests for CQL library loading."""

    def test_load_library_absolute_path(
        self,
        executor: CDSExecutor,
        tmp_cql_library: Path,
    ) -> None:
        """Test loading a CQL library from absolute path."""
        source = executor._load_cql_library(str(tmp_cql_library))
        assert "library TestLibrary" in source
        assert 'define "Greeting"' in source

    def test_load_library_relative_path(
        self,
        cds_settings: CDSHooksSettings,
        tmp_cql_library: Path,
    ) -> None:
        """Test loading a CQL library from relative path with base path."""
        # Create executor with cql_library_path set
        executor = CDSExecutor(cds_settings)
        source = executor._load_cql_library(tmp_cql_library.name)
        assert "library TestLibrary" in source

    def test_load_library_not_found(self, executor: CDSExecutor) -> None:
        """Test that missing library raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            executor._load_cql_library("nonexistent.cql")

    def test_library_caching(
        self,
        executor: CDSExecutor,
        tmp_cql_library: Path,
    ) -> None:
        """Test that libraries are cached."""
        path = str(tmp_cql_library)
        # Load twice
        source1 = executor._load_cql_library(path)
        source2 = executor._load_cql_library(path)
        assert source1 == source2
        # Should be in cache
        assert path in executor._library_cache


# =============================================================================
# Evaluator Caching Tests
# =============================================================================


class TestEvaluatorCaching:
    """Tests for CQL evaluator caching."""

    def test_evaluator_cached_per_service(
        self,
        executor: CDSExecutor,
        sample_service_config: CDSServiceConfig,
    ) -> None:
        """Test that evaluators are cached per service."""
        evaluator1 = executor._get_evaluator(sample_service_config)
        evaluator2 = executor._get_evaluator(sample_service_config)
        assert evaluator1 is evaluator2

    def test_clear_specific_cache(
        self,
        executor: CDSExecutor,
        sample_service_config: CDSServiceConfig,
    ) -> None:
        """Test clearing cache for specific service."""
        executor._get_evaluator(sample_service_config)
        assert sample_service_config.id in executor._evaluator_cache

        executor.clear_cache(sample_service_config.id)
        assert sample_service_config.id not in executor._evaluator_cache

    def test_clear_all_cache(
        self,
        executor: CDSExecutor,
        sample_service_config: CDSServiceConfig,
    ) -> None:
        """Test clearing entire cache."""
        executor._get_evaluator(sample_service_config)
        executor.clear_cache()
        assert len(executor._evaluator_cache) == 0
        assert len(executor._library_cache) == 0


# =============================================================================
# Data Source Building Tests
# =============================================================================


class TestDataSourceBuilding:
    """Tests for building data source from prefetch."""

    def test_build_empty_data_source(
        self,
        executor: CDSExecutor,
        sample_request: CDSRequest,
    ) -> None:
        """Test building data source with no prefetch."""
        data_source = executor._build_data_source(sample_request)
        assert data_source is not None

    def test_build_data_source_with_patient(
        self,
        executor: CDSExecutor,
        request_with_prefetch: CDSRequest,
    ) -> None:
        """Test building data source with patient resource."""
        data_source = executor._build_data_source(request_with_prefetch)
        # Data source should have resources
        assert data_source is not None

    def test_build_data_source_with_bundle(
        self,
        executor: CDSExecutor,
        request_with_prefetch: CDSRequest,
    ) -> None:
        """Test building data source with bundle."""
        data_source = executor._build_data_source(request_with_prefetch)
        # Should extract resources from bundle
        assert data_source is not None

    def test_build_data_source_ignores_none(self, executor: CDSExecutor) -> None:
        """Test that None prefetch values are ignored."""
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={},
            prefetch={"patient": None, "valid": {"resourceType": "Patient", "id": "123"}},
        )
        data_source = executor._build_data_source(request)
        assert data_source is not None


# =============================================================================
# Patient Extraction Tests
# =============================================================================


class TestPatientExtraction:
    """Tests for extracting patient from prefetch."""

    def test_extract_patient_from_prefetch(
        self,
        executor: CDSExecutor,
        request_with_prefetch: CDSRequest,
    ) -> None:
        """Test extracting patient from prefetch."""
        patient = executor._extract_patient(request_with_prefetch)
        assert patient is not None
        assert patient["resourceType"] == "Patient"
        assert patient["id"] == "patient-123"

    def test_extract_patient_none_when_missing(
        self,
        executor: CDSExecutor,
        sample_request: CDSRequest,
    ) -> None:
        """Test that None is returned when patient is missing."""
        patient = executor._extract_patient(sample_request)
        assert patient is None

    def test_extract_patient_from_Patient_key(
        self,
        executor: CDSExecutor,
    ) -> None:
        """Test extracting patient from 'Patient' key (capitalized)."""
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={},
            prefetch={
                "Patient": {"resourceType": "Patient", "id": "456"},
            },
        )
        patient = executor._extract_patient(request)
        assert patient is not None
        assert patient["id"] == "456"


# =============================================================================
# Result Serialization Tests
# =============================================================================


class TestResultSerialization:
    """Tests for serializing CQL results."""

    def test_serialize_none(self, executor: CDSExecutor) -> None:
        """Test serializing None."""
        assert executor._serialize_result(None) is None

    def test_serialize_primitives(self, executor: CDSExecutor) -> None:
        """Test serializing primitive values."""
        assert executor._serialize_result("hello") == "hello"
        assert executor._serialize_result(42) == 42
        assert executor._serialize_result(3.14) == 3.14
        assert executor._serialize_result(True) is True
        assert executor._serialize_result(False) is False

    def test_serialize_list(self, executor: CDSExecutor) -> None:
        """Test serializing lists."""
        result = executor._serialize_result([1, 2, 3])
        assert result == [1, 2, 3]

    def test_serialize_nested_list(self, executor: CDSExecutor) -> None:
        """Test serializing nested lists."""
        result = executor._serialize_result([[1, 2], [3, 4]])
        assert result == [[1, 2], [3, 4]]

    def test_serialize_dict(self, executor: CDSExecutor) -> None:
        """Test serializing dictionaries."""
        result = executor._serialize_result({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_serialize_nested_dict(self, executor: CDSExecutor) -> None:
        """Test serializing nested dictionaries."""
        result = executor._serialize_result({"outer": {"inner": "value"}})
        assert result == {"outer": {"inner": "value"}}


# =============================================================================
# CQL Execution Tests
# =============================================================================


class TestCQLExecution:
    """Tests for CQL execution."""

    def test_execute_definitions(
        self,
        executor: CDSExecutor,
        sample_service_config: CDSServiceConfig,
        sample_request: CDSRequest,
    ) -> None:
        """Test executing CQL definitions."""
        results = executor.execute(sample_service_config, sample_request)

        assert "Greeting" in results
        assert results["Greeting"] == "Hello, World!"
        assert "Sum" in results
        assert results["Sum"] == 6
        assert "HasValue" in results
        assert results["HasValue"] is True

    def test_execute_adds_context(
        self,
        executor: CDSExecutor,
        sample_service_config: CDSServiceConfig,
        sample_request: CDSRequest,
    ) -> None:
        """Test that execution adds context information."""
        results = executor.execute(sample_service_config, sample_request)

        assert "_context" in results
        assert results["_context"]["patientId"] == "test-patient"
        assert results["_context"]["userId"] == "test-user"
        assert "hookInstance" in results["_context"]

    def test_execute_handles_errors(
        self,
        executor: CDSExecutor,
        sample_request: CDSRequest,
        tmp_path: Path,
    ) -> None:
        """Test that execution handles definition errors gracefully."""
        # Create CQL with a definition that will error
        cql_content = """
library ErrorTest version '1.0.0'

define "WillError":
  1 / 0
"""
        lib_path = tmp_path / "error.cql"
        lib_path.write_text(cql_content)

        service = CDSServiceConfig(
            id="error-service",
            hook="patient-view",
            title="Error Test",
            description="Test",
            cqlLibrary=str(lib_path),
            evaluateDefinitions=["WillError"],
        )

        results = executor.execute(service, sample_request)

        # Should have error info, not raise exception
        assert "WillError" in results
        if isinstance(results["WillError"], dict):
            assert "_error" in results["WillError"]
