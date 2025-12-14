"""Integration tests for CDS Hooks end-to-end flows."""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fhirkit.cds_hooks.api.app import create_app
from fhirkit.cds_hooks.config.settings import CDSHooksSettings
from fhirkit.cds_hooks.service.card_builder import CardBuilder
from fhirkit.cds_hooks.service.executor import CDSExecutor
from fhirkit.cds_hooks.service.registry import ServiceRegistry


@pytest.fixture
def cql_hello_world(tmp_path: Path) -> Path:
    """Create a simple CQL library for testing."""
    cql_content = """
library HelloWorld version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "Greeting":
  'Hello, World!'

define "HasGreeting":
  true

define "PatientId":
  Patient.id
"""
    lib_path = tmp_path / "hello.cql"
    lib_path.write_text(cql_content)
    return lib_path


@pytest.fixture
def cql_patient_age(tmp_path: Path) -> Path:
    """Create a CQL library with patient age logic."""
    cql_content = """
library PatientAge version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "PatientAge":
  AgeInYears()

define "IsElderly":
  PatientAge >= 65

define "AgeGroup":
  case
    when PatientAge < 18 then 'Pediatric'
    when PatientAge < 65 then 'Adult'
    else 'Elderly'
  end
"""
    lib_path = tmp_path / "patient_age.cql"
    lib_path.write_text(cql_content)
    return lib_path


@pytest.fixture
def integration_config(tmp_path: Path, cql_hello_world: Path, cql_patient_age: Path) -> Path:
    """Create a config file with multiple services."""
    config_content = f"""
services:
  - id: hello-world
    hook: patient-view
    title: Hello World Service
    description: Simple greeting service
    cqlLibrary: {cql_hello_world}
    evaluateDefinitions:
      - Greeting
      - HasGreeting
    prefetch:
      patient: Patient/{{{{context.patientId}}}}
    cards:
      - condition: HasGreeting
        indicator: info
        summary: "{{{{Greeting}}}}"
        source: Hello World CDS

  - id: patient-age
    hook: patient-view
    title: Patient Age Service
    description: Checks patient age
    cqlLibrary: {cql_patient_age}
    evaluateDefinitions:
      - PatientAge
      - IsElderly
      - AgeGroup
    prefetch:
      patient: Patient/{{{{context.patientId}}}}
    cards:
      - condition: IsElderly
        indicator: warning
        summary: "Patient is elderly ({{{{AgeGroup}}}})"
        detail: "Age: {{{{PatientAge}}}} years"
        source: Age Assessment CDS
"""
    config_path = tmp_path / "integration_config.yaml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def settings(integration_config: Path) -> CDSHooksSettings:
    """Create settings for integration tests."""
    return CDSHooksSettings(services_config_path=str(integration_config))


@pytest.fixture
def client(settings: CDSHooksSettings) -> TestClient:
    """Create test client for integration tests."""
    app = create_app(settings)
    return TestClient(app)


# =============================================================================
# End-to-End Service Flow Tests
# =============================================================================


class TestEndToEndFlow:
    """Tests for complete service invocation flows."""

    def test_discover_invoke_flow(self, client: TestClient) -> None:
        """Test discovering then invoking a service."""
        # Step 1: Discover services
        discovery_response = client.get("/cds-services")
        assert discovery_response.status_code == 200
        services = discovery_response.json()["services"]
        assert len(services) >= 1

        # Step 2: Find hello-world service
        hello_service = next(s for s in services if s["id"] == "hello-world")
        assert hello_service["hook"] == "patient-view"

        # Step 3: Invoke the service
        invoke_response = client.post(
            f"/cds-services/{hello_service['id']}",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "patient-123"},
                "prefetch": {
                    "patient": {
                        "resourceType": "Patient",
                        "id": "patient-123",
                        "birthDate": "1990-01-01",
                    }
                },
            },
        )
        assert invoke_response.status_code == 200

        # Step 4: Verify cards returned
        cards = invoke_response.json()["cards"]
        assert len(cards) >= 1
        assert "Hello" in cards[0]["summary"]

    def test_elderly_patient_flow(self, client: TestClient) -> None:
        """Test age-based service with elderly patient."""
        response = client.post(
            "/cds-services/patient-age",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "elderly-patient"},
                "prefetch": {
                    "patient": {
                        "resourceType": "Patient",
                        "id": "elderly-patient",
                        "birthDate": "1950-01-01",  # ~74 years old
                    }
                },
            },
        )
        assert response.status_code == 200
        cards = response.json()["cards"]

        # Should have warning card for elderly patient
        assert len(cards) >= 1
        assert cards[0]["indicator"] == "warning"
        assert "elderly" in cards[0]["summary"].lower()

    def test_young_patient_no_elderly_card(self, client: TestClient) -> None:
        """Test that young patient doesn't get elderly warning."""
        response = client.post(
            "/cds-services/patient-age",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "young-patient"},
                "prefetch": {
                    "patient": {
                        "resourceType": "Patient",
                        "id": "young-patient",
                        "birthDate": "2000-01-01",  # ~24 years old
                    }
                },
            },
        )
        assert response.status_code == 200
        cards = response.json()["cards"]

        # Should not have elderly warning card
        elderly_cards = [c for c in cards if "elderly" in c.get("summary", "").lower()]
        assert len(elderly_cards) == 0


# =============================================================================
# Multi-Service Tests
# =============================================================================


class TestMultiService:
    """Tests involving multiple services."""

    def test_invoke_different_services(self, client: TestClient) -> None:
        """Test invoking different services."""
        patient_data = {
            "resourceType": "Patient",
            "id": "multi-test",
            "birthDate": "1960-01-01",
        }

        # Invoke hello-world
        hello_response = client.post(
            "/cds-services/hello-world",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "multi-test"},
                "prefetch": {"patient": patient_data},
            },
        )
        assert hello_response.status_code == 200

        # Invoke patient-age
        age_response = client.post(
            "/cds-services/patient-age",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "multi-test"},
                "prefetch": {"patient": patient_data},
            },
        )
        assert age_response.status_code == 200

        # Both should return valid responses
        assert "cards" in hello_response.json()
        assert "cards" in age_response.json()

    def test_discovery_returns_all_services(self, client: TestClient) -> None:
        """Test that discovery returns all configured services."""
        response = client.get("/cds-services")
        assert response.status_code == 200

        services = response.json()["services"]
        service_ids = [s["id"] for s in services]

        assert "hello-world" in service_ids
        assert "patient-age" in service_ids


# =============================================================================
# Error Recovery Tests
# =============================================================================


class TestErrorRecovery:
    """Tests for error handling and recovery."""

    def test_invalid_hook_returns_error(self, client: TestClient) -> None:
        """Test that wrong hook type returns error."""
        response = client.post(
            "/cds-services/hello-world",
            json={
                "hook": "order-sign",  # Wrong hook
                "hookInstance": str(uuid4()),
                "context": {},
            },
        )
        assert response.status_code == 400

    def test_missing_service_returns_404(self, client: TestClient) -> None:
        """Test that non-existent service returns 404."""
        response = client.post(
            "/cds-services/does-not-exist",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {},
            },
        )
        assert response.status_code == 404

    def test_malformed_request_returns_422(self, client: TestClient) -> None:
        """Test that malformed request returns 422."""
        response = client.post(
            "/cds-services/hello-world",
            json={
                "not": "valid",
                "request": "format",
            },
        )
        assert response.status_code == 422


# =============================================================================
# Service Component Integration Tests
# =============================================================================


class TestComponentIntegration:
    """Tests for integration between service components."""

    def test_registry_executor_card_builder_integration(
        self,
        settings: CDSHooksSettings,
    ) -> None:
        """Test that registry, executor, and card builder work together."""
        from fhirkit.cds_hooks.models.request import CDSRequest

        registry = ServiceRegistry(settings)
        executor = CDSExecutor(settings)
        card_builder = CardBuilder()

        # Get service from registry
        service = registry.get_service("hello-world")
        assert service is not None

        # Create request
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={"patientId": "test"},
            prefetch={
                "patient": {"resourceType": "Patient", "id": "test"},
            },
        )

        # Execute with executor
        results = executor.execute(service, request)
        assert "Greeting" in results
        assert "HasGreeting" in results

        # Build cards with card builder
        response = card_builder.build_response(service, results)
        assert len(response.cards) >= 1

    def test_discovery_response_matches_config(
        self,
        settings: CDSHooksSettings,
    ) -> None:
        """Test that discovery response matches service configs."""
        registry = ServiceRegistry(settings)

        # Get services from registry
        services = registry.list_services()
        discovery = registry.get_discovery_response()

        # Should have same number
        assert len(discovery.services) == len(services)

        # Service IDs should match
        registry_ids = {s.id for s in services}
        discovery_ids = {s.id for s in discovery.services}
        assert registry_ids == discovery_ids


# =============================================================================
# Real Config File Tests
# =============================================================================


class TestRealConfigIntegration:
    """Tests using the project's actual config file (if it exists)."""

    def test_load_project_cds_services_yaml(self) -> None:
        """Test loading the project's cds_services.yaml if it exists."""
        config_path = Path("cds_services.yaml")
        if not config_path.exists():
            pytest.skip("cds_services.yaml not found in project root")

        settings = CDSHooksSettings(services_config_path=str(config_path))
        registry = ServiceRegistry(settings)

        services = registry.list_services()
        # Should load without errors
        assert isinstance(services, list)

        # If services exist, they should be valid
        for service in services:
            assert service.id
            assert service.hook
            assert service.title
