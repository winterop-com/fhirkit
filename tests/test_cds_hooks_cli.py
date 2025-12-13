"""Tests for CDS Hooks CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from fhir_cql.cds_cli import app

runner = CliRunner()


@pytest.fixture
def valid_config_content() -> str:
    """Create valid YAML config content."""
    return """
services:
  - id: test-service
    hook: patient-view
    title: Test Service
    description: A test service for CLI testing
    cqlLibrary: examples/cql/01_hello_world.cql
    evaluateDefinitions:
      - Greeting
    prefetch:
      patient: Patient/{{context.patientId}}
    cards:
      - indicator: info
        summary: Hello from CLI test!
        source: Test CDS

  - id: another-service
    hook: order-sign
    title: Another Service
    description: Another test service
    cqlLibrary: examples/cql/02_basic_types.cql
    evaluateDefinitions:
      - StringLiteral
"""


@pytest.fixture
def invalid_config_content() -> str:
    """Create invalid YAML config content."""
    return """
services:
  - id: missing-required-fields
    # Missing: hook, title, description, cqlLibrary, evaluateDefinitions
"""


@pytest.fixture
def valid_config_file(tmp_path: Path, valid_config_content: str) -> Path:
    """Create a valid temporary config file."""
    config_path = tmp_path / "valid_config.yaml"
    config_path.write_text(valid_config_content)
    return config_path


@pytest.fixture
def invalid_config_file(tmp_path: Path, invalid_config_content: str) -> Path:
    """Create an invalid temporary config file."""
    config_path = tmp_path / "invalid_config.yaml"
    config_path.write_text(invalid_config_content)
    return config_path


@pytest.fixture
def sample_patient_file(tmp_path: Path) -> Path:
    """Create a sample patient JSON file."""
    import json

    patient = {
        "resourceType": "Patient",
        "id": "test-patient",
        "birthDate": "1990-01-15",
        "name": [{"given": ["Test"], "family": "Patient"}],
        "gender": "male",
    }
    patient_path = tmp_path / "patient.json"
    patient_path.write_text(json.dumps(patient))
    return patient_path


# =============================================================================
# Validate Command Tests
# =============================================================================


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_valid_config(self, valid_config_file: Path) -> None:
        """Test validating a valid config file."""
        result = runner.invoke(app, ["validate", str(valid_config_file)])
        assert result.exit_code == 0
        assert "Valid configuration" in result.stdout
        assert "2 service(s)" in result.stdout

    def test_validate_invalid_config(self, invalid_config_file: Path) -> None:
        """Test validating an invalid config file."""
        result = runner.invoke(app, ["validate", str(invalid_config_file)])
        assert result.exit_code == 1
        assert "Validation error" in result.stdout or "error" in result.stdout.lower()

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validating a file that doesn't exist."""
        result = runner.invoke(app, ["validate", str(tmp_path / "nonexistent.yaml")])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_validate_empty_config(self, tmp_path: Path) -> None:
        """Test validating an empty config file."""
        empty_path = tmp_path / "empty.yaml"
        empty_path.write_text("")
        result = runner.invoke(app, ["validate", str(empty_path)])
        # Empty config may exit with 0 or 1 depending on implementation
        # The important thing is it handles it gracefully without crashing
        assert result.exit_code in (0, 1)
        assert "empty" in result.stdout.lower() or "Warning" in result.stdout or "0 service" in result.stdout

    def test_validate_shows_service_table(self, valid_config_file: Path) -> None:
        """Test that validate shows a table of services."""
        result = runner.invoke(app, ["validate", str(valid_config_file)])
        assert result.exit_code == 0
        assert "test-service" in result.stdout
        assert "patient-view" in result.stdout


# =============================================================================
# List Command Tests
# =============================================================================


class TestListCommand:
    """Tests for the list command."""

    def test_list_services(self, valid_config_file: Path) -> None:
        """Test listing services from config."""
        result = runner.invoke(app, ["list", "--config", str(valid_config_file)])
        assert result.exit_code == 0
        assert "test-service" in result.stdout
        # Rich table may truncate long names, so check for partial match
        assert "another-servi" in result.stdout

    def test_list_shows_hooks(self, valid_config_file: Path) -> None:
        """Test that list shows hook types."""
        result = runner.invoke(app, ["list", "--config", str(valid_config_file)])
        assert result.exit_code == 0
        assert "patient-view" in result.stdout
        assert "order-sign" in result.stdout

    def test_list_nonexistent_config(self, tmp_path: Path) -> None:
        """Test listing with non-existent config file."""
        result = runner.invoke(app, ["list", "--config", str(tmp_path / "missing.yaml")])
        # Should handle gracefully
        assert "No services" in result.stdout or "not found" in result.stdout.lower()

    def test_list_empty_config(self, tmp_path: Path) -> None:
        """Test listing with empty config file."""
        empty_path = tmp_path / "empty.yaml"
        empty_path.write_text("services: []")
        result = runner.invoke(app, ["list", "--config", str(empty_path)])
        assert "No services" in result.stdout


# =============================================================================
# Test Command Tests
# =============================================================================


class TestTestCommand:
    """Tests for the test command."""

    def test_test_service(self, valid_config_file: Path) -> None:
        """Test running a service test."""
        result = runner.invoke(
            app,
            ["test", "test-service", "--config", str(valid_config_file)],
        )
        assert result.exit_code == 0
        assert "Testing service" in result.stdout

    def test_test_service_with_patient(
        self,
        valid_config_file: Path,
        sample_patient_file: Path,
    ) -> None:
        """Test running a service test with patient file."""
        result = runner.invoke(
            app,
            [
                "test",
                "test-service",
                "--config",
                str(valid_config_file),
                "--patient",
                str(sample_patient_file),
            ],
        )
        assert result.exit_code == 0
        assert "Loaded patient" in result.stdout

    def test_test_nonexistent_service(self, valid_config_file: Path) -> None:
        """Test running test on non-existent service."""
        result = runner.invoke(
            app,
            ["test", "nonexistent", "--config", str(valid_config_file)],
        )
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_test_shows_cql_results(self, valid_config_file: Path) -> None:
        """Test that test command shows CQL results."""
        result = runner.invoke(
            app,
            ["test", "test-service", "--config", str(valid_config_file)],
        )
        assert result.exit_code == 0
        assert "CQL Results" in result.stdout

    def test_test_shows_cards(self, valid_config_file: Path) -> None:
        """Test that test command shows generated cards."""
        result = runner.invoke(
            app,
            ["test", "test-service", "--config", str(valid_config_file)],
        )
        assert result.exit_code == 0
        assert "Cards generated" in result.stdout


# =============================================================================
# Help Output Tests
# =============================================================================


class TestHelpOutput:
    """Tests for CLI help output."""

    def test_main_help(self) -> None:
        """Test main command help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "serve" in result.stdout
        assert "validate" in result.stdout
        assert "list" in result.stdout
        assert "test" in result.stdout

    def test_validate_help(self) -> None:
        """Test validate command help."""
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate" in result.stdout

    def test_list_help(self) -> None:
        """Test list command help."""
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "List" in result.stdout

    def test_test_help(self) -> None:
        """Test test command help."""
        result = runner.invoke(app, ["test", "--help"])
        assert result.exit_code == 0
        assert "Test" in result.stdout

    def test_serve_help(self) -> None:
        """Test serve command help."""
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "Start" in result.stdout
        # Rich may add ANSI codes that split the option text, so check for keywords
        assert "host" in result.stdout.lower()
        assert "port" in result.stdout.lower()


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for CLI error handling."""

    def test_yaml_parse_error(self, tmp_path: Path) -> None:
        """Test handling of YAML parse errors."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("services: [not: valid: yaml:")
        result = runner.invoke(app, ["validate", str(bad_yaml)])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    def test_test_with_invalid_patient_file(
        self,
        valid_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test with invalid patient file."""
        bad_patient = tmp_path / "bad_patient.json"
        bad_patient.write_text("not valid json")
        result = runner.invoke(
            app,
            [
                "test",
                "test-service",
                "--config",
                str(valid_config_file),
                "--patient",
                str(bad_patient),
            ],
        )
        # Should handle error gracefully
        assert result.exit_code == 1 or "error" in result.stdout.lower()
