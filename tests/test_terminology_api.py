"""Tests for terminology API."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.terminology import (
    InMemoryTerminologyService,
    ValueSet,
    ValueSetCompose,
    ValueSetComposeInclude,
    ValueSetComposeIncludeConcept,
)
from fhirkit.terminology.api import create_app


@pytest.fixture
def service() -> InMemoryTerminologyService:
    """Create a service with test value sets."""
    service = InMemoryTerminologyService()

    # Add observation status value set
    obs_status_vs = ValueSet(
        id="observation-status",
        url="http://hl7.org/fhir/ValueSet/observation-status",
        name="ObservationStatus",
        compose=ValueSetCompose(
            include=[
                ValueSetComposeInclude(
                    system="http://hl7.org/fhir/observation-status",
                    concept=[
                        ValueSetComposeIncludeConcept(code="final", display="Final"),
                        ValueSetComposeIncludeConcept(code="preliminary", display="Preliminary"),
                    ],
                )
            ]
        ),
    )
    service.add_value_set(obs_status_vs)

    return service


@pytest.fixture
def client(service) -> TestClient:
    """Create test client with pre-configured service."""
    app = create_app(service=service)
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "docs" in data


class TestValidateCodeEndpoint:
    """Test $validate-code endpoint."""

    def test_validate_code_post(self, client):
        response = client.post(
            "/terminology/ValueSet/$validate-code",
            json={
                "url": "http://hl7.org/fhir/ValueSet/observation-status",
                "code": "final",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    def test_validate_code_post_invalid(self, client):
        response = client.post(
            "/terminology/ValueSet/$validate-code",
            json={
                "url": "http://hl7.org/fhir/ValueSet/observation-status",
                "code": "invalid",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is False

    def test_validate_code_get(self, client):
        response = client.get(
            "/terminology/ValueSet/$validate-code",
            params={
                "url": "http://hl7.org/fhir/ValueSet/observation-status",
                "code": "final",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True


class TestSubsumesEndpoint:
    """Test $subsumes endpoint."""

    def test_subsumes_post_equivalent(self, client):
        response = client.post(
            "/terminology/CodeSystem/$subsumes",
            json={
                "codeA": "final",
                "codeB": "final",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["outcome"] == "equivalent"

    def test_subsumes_post_not_subsumed(self, client):
        response = client.post(
            "/terminology/CodeSystem/$subsumes",
            json={
                "codeA": "final",
                "codeB": "preliminary",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["outcome"] == "not-subsumed"

    def test_subsumes_get(self, client):
        response = client.get(
            "/terminology/CodeSystem/$subsumes",
            params={
                "codeA": "final",
                "codeB": "final",
                "system": "http://hl7.org/fhir/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["outcome"] == "equivalent"


class TestMemberOfEndpoint:
    """Test memberOf endpoint."""

    def test_member_of_true(self, client):
        response = client.get(
            "/terminology/memberOf",
            params={
                "code": "final",
                "system": "http://hl7.org/fhir/observation-status",
                "valueset": "http://hl7.org/fhir/ValueSet/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    def test_member_of_false(self, client):
        response = client.get(
            "/terminology/memberOf",
            params={
                "code": "invalid",
                "system": "http://hl7.org/fhir/observation-status",
                "valueset": "http://hl7.org/fhir/ValueSet/observation-status",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is False


class TestValueSetEndpoint:
    """Test ValueSet retrieval endpoints."""

    def test_get_value_set_by_url(self, client):
        response = client.get(
            "/terminology/ValueSet",
            params={"url": "http://hl7.org/fhir/ValueSet/observation-status"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ObservationStatus"

    def test_get_value_set_not_found(self, client):
        response = client.get(
            "/terminology/ValueSet",
            params={"url": "http://nonexistent/ValueSet"},
        )
        assert response.status_code == 404

    def test_get_value_set_by_id(self, client):
        response = client.get("/terminology/ValueSet/observation-status")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "observation-status"
