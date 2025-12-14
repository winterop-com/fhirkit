"""Tests for CDS Hooks configuration settings."""

import pytest
from pydantic import ValidationError

from fhirkit.cds_hooks.config.settings import (
    CardTemplate,
    CDSHooksSettings,
    CDSServiceConfig,
)

# =============================================================================
# CardTemplate Tests
# =============================================================================


class TestCardTemplate:
    """Tests for CardTemplate model."""

    def test_minimal_template(self) -> None:
        """Test card template with minimal required fields."""
        template = CardTemplate(
            summary="Alert: {{AlertType}}",
            source="My CDS Service",
        )
        assert template.summary == "Alert: {{AlertType}}"
        assert template.source == "My CDS Service"
        assert template.condition is None
        assert template.indicator == "info"  # default

    def test_full_template(self) -> None:
        """Test card template with all fields."""
        template = CardTemplate(
            condition="HasAlerts",
            indicator="warning",
            summary="{{AlertCount}} alerts found",
            detail="## Details\n{{AlertDetails}}",
            source="CDS Service",
            sourceUrl="https://example.org",
            suggestions=[{"label": "Review", "isRecommended": True}],
            links=[{"label": "More", "url": "https://example.org", "type": "absolute"}],
        )
        assert template.condition == "HasAlerts"
        assert template.indicator == "warning"
        assert template.detail is not None
        assert len(template.suggestions) == 1
        assert len(template.links) == 1

    def test_valid_indicators(self) -> None:
        """Test valid indicator values."""
        for indicator in ["info", "warning", "critical"]:
            template = CardTemplate(
                summary="Test",
                source="CDS",
                indicator=indicator,
            )
            assert template.indicator == indicator

    def test_default_indicator(self) -> None:
        """Test default indicator is info."""
        template = CardTemplate(summary="Test", source="CDS")
        assert template.indicator == "info"

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise errors."""
        with pytest.raises(ValidationError):
            CardTemplate(source="CDS")  # type: ignore # missing summary

        with pytest.raises(ValidationError):
            CardTemplate(summary="Test")  # type: ignore # missing source


# =============================================================================
# CDSServiceConfig Tests
# =============================================================================


class TestCDSServiceConfig:
    """Tests for CDSServiceConfig model."""

    def test_minimal_config(self) -> None:
        """Test service config with minimal required fields."""
        config = CDSServiceConfig(
            id="test-service",
            hook="patient-view",
            title="Test Service",
            description="A test service",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Definition1"],
        )
        assert config.id == "test-service"
        assert config.hook == "patient-view"
        assert config.enabled is True  # default

    def test_full_config(self) -> None:
        """Test service config with all fields."""
        config = CDSServiceConfig(
            id="med-safety",
            hook="order-sign",
            title="Medication Safety",
            description="Checks for drug interactions",
            cqlLibrary="examples/cql/medication_safety.cql",
            evaluateDefinitions=["HasInteractions", "InteractionList"],
            prefetch={
                "patient": "Patient/{{context.patientId}}",
                "meds": "MedicationRequest?patient={{context.patientId}}",
            },
            cards=[
                CardTemplate(
                    condition="HasInteractions",
                    indicator="warning",
                    summary="Drug interactions detected",
                    source="Med Safety CDS",
                )
            ],
            enabled=True,
            usageRequirements="Requires medication access",
        )
        assert config.cqlLibrary == "examples/cql/medication_safety.cql"
        assert len(config.evaluateDefinitions) == 2
        assert len(config.prefetch) == 2
        assert len(config.cards) == 1
        assert config.usageRequirements is not None

    def test_disabled_service(self) -> None:
        """Test disabled service configuration."""
        config = CDSServiceConfig(
            id="disabled-service",
            hook="patient-view",
            title="Disabled",
            description="Not active",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
            enabled=False,
        )
        assert config.enabled is False

    def test_empty_prefetch(self) -> None:
        """Test service with empty prefetch."""
        config = CDSServiceConfig(
            id="test",
            hook="patient-view",
            title="Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
        )
        assert config.prefetch == {}

    def test_empty_cards(self) -> None:
        """Test service with no card templates."""
        config = CDSServiceConfig(
            id="test",
            hook="patient-view",
            title="Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
        )
        assert config.cards == []

    def test_multiple_definitions(self) -> None:
        """Test service with multiple definitions."""
        config = CDSServiceConfig(
            id="test",
            hook="patient-view",
            title="Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Def1", "Def2", "Def3", "Def4"],
        )
        assert len(config.evaluateDefinitions) == 4

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise errors."""
        with pytest.raises(ValidationError):
            CDSServiceConfig(
                hook="patient-view",
                title="Test",
                description="Test",
                cqlLibrary="test.cql",
                evaluateDefinitions=["Test"],
            )  # missing id

        with pytest.raises(ValidationError):
            CDSServiceConfig(
                id="test",
                title="Test",
                description="Test",
                cqlLibrary="test.cql",
                evaluateDefinitions=["Test"],
            )  # missing hook

        with pytest.raises(ValidationError):
            CDSServiceConfig(
                id="test",
                hook="patient-view",
                title="Test",
                description="Test",
                evaluateDefinitions=["Test"],
            )  # missing cqlLibrary


# =============================================================================
# CDSHooksSettings Tests
# =============================================================================


class TestCDSHooksSettings:
    """Tests for CDSHooksSettings model."""

    def test_default_values(self) -> None:
        """Test settings with default values."""
        settings = CDSHooksSettings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080
        assert settings.base_path == "/cds-services"
        assert settings.services_config_path == "cds_services.yaml"
        assert settings.cql_library_path == ""
        assert settings.enable_cors is True
        assert settings.allowed_origins == ["*"]
        assert settings.log_level == "INFO"
        assert settings.log_requests is True
        assert settings.max_cards_per_response == 10
        assert settings.evaluation_timeout_seconds == 30

    def test_custom_values(self) -> None:
        """Test settings with custom values."""
        settings = CDSHooksSettings(
            host="127.0.0.1",
            port=9000,
            base_path="/cds",
            services_config_path="/etc/cds/config.yaml",
            cql_library_path="/opt/cql",
            enable_cors=False,
            log_level="DEBUG",
        )
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.base_path == "/cds"
        assert settings.services_config_path == "/etc/cds/config.yaml"
        assert settings.cql_library_path == "/opt/cql"
        assert settings.enable_cors is False
        assert settings.log_level == "DEBUG"

    def test_cors_settings(self) -> None:
        """Test CORS configuration."""
        settings = CDSHooksSettings(
            enable_cors=True,
            allowed_origins=["https://ehr.example.org", "https://app.example.org"],
        )
        assert settings.enable_cors is True
        assert len(settings.allowed_origins) == 2
        assert "https://ehr.example.org" in settings.allowed_origins

    def test_performance_settings(self) -> None:
        """Test performance-related settings."""
        settings = CDSHooksSettings(
            max_cards_per_response=5,
            evaluation_timeout_seconds=60,
        )
        assert settings.max_cards_per_response == 5
        assert settings.evaluation_timeout_seconds == 60

    def test_environment_variable_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override defaults."""
        monkeypatch.setenv("CDS_HOOKS_HOST", "192.168.1.1")
        monkeypatch.setenv("CDS_HOOKS_PORT", "3000")
        monkeypatch.setenv("CDS_HOOKS_LOG_LEVEL", "WARNING")

        settings = CDSHooksSettings()
        assert settings.host == "192.168.1.1"
        assert settings.port == 3000
        assert settings.log_level == "WARNING"

    def test_env_prefix(self) -> None:
        """Test that model config includes env prefix."""
        assert CDSHooksSettings.model_config.get("env_prefix") == "CDS_HOOKS_"

    def test_model_config_env_file(self) -> None:
        """Test that model config includes env_file setting."""
        assert CDSHooksSettings.model_config.get("env_file") == ".env"
