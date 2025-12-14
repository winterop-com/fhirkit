"""Tests for CDS Hooks API endpoints."""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fhirkit.cds_hooks.api.app import create_app
from fhirkit.cds_hooks.config.settings import CDSHooksSettings


@pytest.fixture
def yaml_config_content() -> str:
    """Create YAML content for testing."""
    return """
services:
  - id: test-service
    hook: patient-view
    title: Test Service
    description: A test service
    cqlLibrary: examples/cql/01_hello_world.cql
    evaluateDefinitions:
      - Greeting
    prefetch:
      patient: Patient/{{context.patientId}}
    cards:
      - indicator: info
        summary: Hello from test!
        source: Test CDS

  - id: order-service
    hook: order-sign
    title: Order Service
    description: An order service
    cqlLibrary: examples/cql/02_basic_types.cql
    evaluateDefinitions:
      - StringLiteral
    cards:
      - indicator: warning
        summary: Order alert
        source: Order CDS
"""


@pytest.fixture
def config_file(tmp_path: Path, yaml_config_content: str) -> Path:
    """Create a temporary config file."""
    config_path = tmp_path / "test_services.yaml"
    config_path.write_text(yaml_config_content)
    return config_path


@pytest.fixture
def settings(config_file: Path) -> CDSHooksSettings:
    """Create test settings."""
    return CDSHooksSettings(
        services_config_path=str(config_file),
        enable_cors=True,
    )


@pytest.fixture
def client(settings: CDSHooksSettings) -> TestClient:
    """Create test client."""
    app = create_app(settings)
    return TestClient(app)


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check returns healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# =============================================================================
# Discovery Endpoint Tests
# =============================================================================


class TestDiscoveryEndpoint:
    """Tests for discovery endpoint."""

    def test_discovery_returns_services(self, client: TestClient) -> None:
        """Test discovery endpoint returns list of services."""
        response = client.get("/cds-services")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert len(data["services"]) == 2

    def test_discovery_service_structure(self, client: TestClient) -> None:
        """Test that discovered services have correct structure."""
        response = client.get("/cds-services")
        data = response.json()

        service = next(s for s in data["services"] if s["id"] == "test-service")
        assert service["hook"] == "patient-view"
        assert service["title"] == "Test Service"
        assert service["description"] == "A test service"
        assert "prefetch" in service
        assert "patient" in service["prefetch"]

    def test_discovery_different_hooks(self, client: TestClient) -> None:
        """Test that services with different hooks are returned."""
        response = client.get("/cds-services")
        data = response.json()

        hooks = [s["hook"] for s in data["services"]]
        assert "patient-view" in hooks
        assert "order-sign" in hooks


# =============================================================================
# Service Invocation Tests
# =============================================================================


class TestServiceInvocation:
    """Tests for service invocation endpoint."""

    def test_invoke_service_success(self, client: TestClient) -> None:
        """Test successful service invocation."""
        response = client.post(
            "/cds-services/test-service",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "123", "userId": "456"},
                "prefetch": {
                    "patient": {"resourceType": "Patient", "id": "123"},
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "cards" in data

    def test_invoke_nonexistent_service(self, client: TestClient) -> None:
        """Test invoking a service that doesn't exist."""
        response = client.post(
            "/cds-services/nonexistent",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {},
            },
        )
        assert response.status_code == 404

    def test_invoke_with_wrong_hook(self, client: TestClient) -> None:
        """Test invoking service with wrong hook type."""
        response = client.post(
            "/cds-services/test-service",
            json={
                "hook": "order-sign",  # Wrong hook for test-service
                "hookInstance": str(uuid4()),
                "context": {},
            },
        )
        assert response.status_code == 400

    def test_invoke_missing_required_fields(self, client: TestClient) -> None:
        """Test invoking service with missing required fields."""
        response = client.post(
            "/cds-services/test-service",
            json={
                "hook": "patient-view",
                # Missing hookInstance and context
            },
        )
        assert response.status_code == 422

    def test_invoke_with_prefetch_data(self, client: TestClient) -> None:
        """Test invoking service with prefetch data."""
        response = client.post(
            "/cds-services/test-service",
            json={
                "hook": "patient-view",
                "hookInstance": str(uuid4()),
                "context": {"patientId": "patient-123"},
                "prefetch": {
                    "patient": {
                        "resourceType": "Patient",
                        "id": "patient-123",
                        "birthDate": "1990-01-01",
                        "name": [{"given": ["John"], "family": "Doe"}],
                    },
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "cards" in data


# =============================================================================
# Feedback Endpoint Tests
# =============================================================================


class TestFeedbackEndpoint:
    """Tests for feedback endpoint."""

    def test_feedback_accepted(self, client: TestClient) -> None:
        """Test submitting feedback for accepted card."""
        response = client.post(
            "/cds-services/test-service/feedback",
            json={
                "feedback": [
                    {
                        "card": "card-uuid-123",
                        "outcome": "accepted",
                        "outcomeTimestamp": "2024-01-01T12:00:00Z",
                    }
                ]
            },
        )
        assert response.status_code == 200

    def test_feedback_overridden(self, client: TestClient) -> None:
        """Test submitting feedback for overridden card."""
        response = client.post(
            "/cds-services/test-service/feedback",
            json={
                "feedback": [
                    {
                        "card": "card-uuid-123",
                        "outcome": "overridden",
                        "outcomeTimestamp": "2024-01-01T12:00:00Z",
                        "overrideReason": {
                            "userComment": "Not applicable to this patient",
                        },
                    }
                ]
            },
        )
        assert response.status_code == 200

    def test_feedback_nonexistent_service(self, client: TestClient) -> None:
        """Test feedback for non-existent service."""
        response = client.post(
            "/cds-services/nonexistent/feedback",
            json={
                "feedback": [
                    {
                        "card": "card-123",
                        "outcome": "accepted",
                        "outcomeTimestamp": "2024-01-01T12:00:00Z",
                    }
                ]
            },
        )
        assert response.status_code == 404


# =============================================================================
# CORS Tests
# =============================================================================


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test that CORS headers are present in response."""
        response = client.get(
            "/cds-services",
            headers={"Origin": "https://ehr.example.org"},
        )
        # When CORS is enabled, response should include CORS headers
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


# =============================================================================
# API Documentation Tests
# =============================================================================


class TestAPIDocs:
    """Tests for API documentation endpoints."""

    def test_openapi_schema(self, client: TestClient) -> None:
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_docs_endpoint(self, client: TestClient) -> None:
        """Test that docs endpoint is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, client: TestClient) -> None:
        """Test that redoc endpoint is available."""
        response = client.get("/redoc")
        assert response.status_code == 200


# =============================================================================
# Empty Registry Tests
# =============================================================================


class TestEmptyRegistry:
    """Tests with empty service registry."""

    def test_discovery_empty_registry(self, tmp_path: Path) -> None:
        """Test discovery with no services configured."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("services: []")
        settings = CDSHooksSettings(services_config_path=str(config_path))
        app = create_app(settings)
        client = TestClient(app)

        response = client.get("/cds-services")
        assert response.status_code == 200
        data = response.json()
        assert data["services"] == []
