"""Tests for CDS Hooks service registry."""

from pathlib import Path

import pytest

from fhirkit.cds_hooks.config.settings import (
    CardTemplate,
    CDSHooksSettings,
    CDSServiceConfig,
)
from fhirkit.cds_hooks.service.registry import ServiceRegistry


@pytest.fixture
def sample_service_config() -> CDSServiceConfig:
    """Create a sample service configuration."""
    return CDSServiceConfig(
        id="test-service",
        hook="patient-view",
        title="Test Service",
        description="A test service for testing",
        cqlLibrary="test.cql",
        evaluateDefinitions=["TestDefinition"],
        prefetch={"patient": "Patient/{{context.patientId}}"},
        cards=[
            CardTemplate(
                condition="TestDefinition",
                indicator="info",
                summary="Test card",
                source="Test CDS",
            )
        ],
    )


@pytest.fixture
def yaml_config_content() -> str:
    """Create YAML content for testing."""
    return """
services:
  - id: service-one
    hook: patient-view
    title: Service One
    description: First test service
    cqlLibrary: examples/cql/01_hello_world.cql
    evaluateDefinitions:
      - Greeting
    prefetch:
      patient: Patient/{{context.patientId}}
    cards:
      - indicator: info
        summary: Hello!
        source: Test

  - id: service-two
    hook: order-sign
    title: Service Two
    description: Second test service
    cqlLibrary: examples/cql/02_basic_types.cql
    evaluateDefinitions:
      - Definition1
      - Definition2
"""


@pytest.fixture
def config_file(tmp_path: Path, yaml_config_content: str) -> Path:
    """Create a temporary config file."""
    config_path = tmp_path / "test_services.yaml"
    config_path.write_text(yaml_config_content)
    return config_path


@pytest.fixture
def settings_with_config(config_file: Path) -> CDSHooksSettings:
    """Create settings pointing to test config."""
    return CDSHooksSettings(services_config_path=str(config_file))


# =============================================================================
# ServiceRegistry Initialization Tests
# =============================================================================


class TestServiceRegistryInit:
    """Tests for ServiceRegistry initialization."""

    def test_init_with_valid_config(self, settings_with_config: CDSHooksSettings) -> None:
        """Test initializing registry with valid config file."""
        registry = ServiceRegistry(settings_with_config)
        assert len(registry.list_services()) == 2

    def test_init_with_nonexistent_file(self, tmp_path: Path) -> None:
        """Test initializing registry with non-existent config file."""
        settings = CDSHooksSettings(services_config_path=str(tmp_path / "nonexistent.yaml"))
        registry = ServiceRegistry(settings)
        # Should handle gracefully with empty services
        assert len(registry.list_services()) == 0

    def test_init_with_empty_config(self, tmp_path: Path) -> None:
        """Test initializing registry with empty config file."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")
        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)
        assert len(registry.list_services()) == 0

    def test_init_with_null_services(self, tmp_path: Path) -> None:
        """Test initializing registry with null services in config."""
        config_path = tmp_path / "null.yaml"
        config_path.write_text("services: null")
        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)
        assert len(registry.list_services()) == 0

    def test_init_filters_disabled_services(self, tmp_path: Path) -> None:
        """Test that disabled services are filtered out."""
        config_content = """
services:
  - id: enabled-service
    hook: patient-view
    title: Enabled
    description: This is enabled
    cqlLibrary: test.cql
    evaluateDefinitions: [Test]
    enabled: true

  - id: disabled-service
    hook: patient-view
    title: Disabled
    description: This is disabled
    cqlLibrary: test.cql
    evaluateDefinitions: [Test]
    enabled: false
"""
        config_path = tmp_path / "mixed.yaml"
        config_path.write_text(config_content)
        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)

        services = registry.list_services()
        assert len(services) == 1
        assert services[0].id == "enabled-service"


# =============================================================================
# ServiceRegistry Operations Tests
# =============================================================================


class TestServiceRegistryOperations:
    """Tests for ServiceRegistry operations."""

    def test_get_service_by_id(self, settings_with_config: CDSHooksSettings) -> None:
        """Test getting a service by ID."""
        registry = ServiceRegistry(settings_with_config)
        service = registry.get_service("service-one")
        assert service is not None
        assert service.id == "service-one"
        assert service.hook == "patient-view"

    def test_get_nonexistent_service(self, settings_with_config: CDSHooksSettings) -> None:
        """Test getting a service that doesn't exist."""
        registry = ServiceRegistry(settings_with_config)
        service = registry.get_service("nonexistent")
        assert service is None

    def test_list_services(self, settings_with_config: CDSHooksSettings) -> None:
        """Test listing all services."""
        registry = ServiceRegistry(settings_with_config)
        services = registry.list_services()
        assert len(services) == 2
        ids = [s.id for s in services]
        assert "service-one" in ids
        assert "service-two" in ids

    def test_register_service(
        self,
        settings_with_config: CDSHooksSettings,
        sample_service_config: CDSServiceConfig,
    ) -> None:
        """Test registering a new service."""
        registry = ServiceRegistry(settings_with_config)
        initial_count = len(registry.list_services())

        registry.register_service(sample_service_config)

        assert len(registry.list_services()) == initial_count + 1
        assert registry.get_service("test-service") is not None

    def test_register_service_replaces_existing(
        self,
        settings_with_config: CDSHooksSettings,
    ) -> None:
        """Test that registering a service with same ID replaces it."""
        registry = ServiceRegistry(settings_with_config)

        new_config = CDSServiceConfig(
            id="service-one",  # Same as existing
            hook="order-sign",  # Different hook
            title="Updated Service",
            description="Updated description",
            cqlLibrary="updated.cql",
            evaluateDefinitions=["Updated"],
        )

        registry.register_service(new_config)

        service = registry.get_service("service-one")
        assert service is not None
        assert service.hook == "order-sign"
        assert service.title == "Updated Service"

    def test_unregister_service(self, settings_with_config: CDSHooksSettings) -> None:
        """Test unregistering a service."""
        registry = ServiceRegistry(settings_with_config)
        initial_count = len(registry.list_services())

        result = registry.unregister_service("service-one")

        assert result is True
        assert len(registry.list_services()) == initial_count - 1
        assert registry.get_service("service-one") is None

    def test_unregister_nonexistent_service(
        self,
        settings_with_config: CDSHooksSettings,
    ) -> None:
        """Test unregistering a service that doesn't exist."""
        registry = ServiceRegistry(settings_with_config)
        result = registry.unregister_service("nonexistent")
        assert result is False


# =============================================================================
# Discovery Response Tests
# =============================================================================


class TestDiscoveryResponse:
    """Tests for discovery response generation."""

    def test_discovery_response_structure(
        self,
        settings_with_config: CDSHooksSettings,
    ) -> None:
        """Test discovery response has correct structure."""
        registry = ServiceRegistry(settings_with_config)
        response = registry.get_discovery_response()

        assert hasattr(response, "services")
        assert len(response.services) == 2

    def test_discovery_response_service_fields(
        self,
        settings_with_config: CDSHooksSettings,
    ) -> None:
        """Test that service descriptors have correct fields."""
        registry = ServiceRegistry(settings_with_config)
        response = registry.get_discovery_response()

        service = next(s for s in response.services if s.id == "service-one")
        assert service.hook == "patient-view"
        assert service.title == "Service One"
        assert service.description == "First test service"
        assert service.prefetch is not None
        assert "patient" in service.prefetch

    def test_discovery_response_empty_registry(self, tmp_path: Path) -> None:
        """Test discovery response with no services."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("services: []")
        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)

        response = registry.get_discovery_response()
        assert response.services == []


# =============================================================================
# Configuration Reload Tests
# =============================================================================


class TestConfigReload:
    """Tests for configuration reloading."""

    def test_reload_from_file(self, tmp_path: Path) -> None:
        """Test reloading configuration from file."""
        config_path = tmp_path / "config.yaml"

        # Initial config with one service
        initial_config = """
services:
  - id: initial-service
    hook: patient-view
    title: Initial
    description: Initial service
    cqlLibrary: test.cql
    evaluateDefinitions: [Test]
"""
        config_path.write_text(initial_config)
        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)

        assert len(registry.list_services()) == 1

        # Update config with two services
        updated_config = """
services:
  - id: service-a
    hook: patient-view
    title: Service A
    description: First service
    cqlLibrary: a.cql
    evaluateDefinitions: [A]

  - id: service-b
    hook: order-sign
    title: Service B
    description: Second service
    cqlLibrary: b.cql
    evaluateDefinitions: [B]
"""
        config_path.write_text(updated_config)

        # Reload
        registry.reload()

        assert len(registry.list_services()) == 2
        assert registry.get_service("initial-service") is None
        assert registry.get_service("service-a") is not None
        assert registry.get_service("service-b") is not None
