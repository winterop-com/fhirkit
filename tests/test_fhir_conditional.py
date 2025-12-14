"""Tests for FHIR conditional operations."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store() -> FHIRStore:
    """Create a fresh FHIR store."""
    return FHIRStore()


@pytest.fixture
def client(store: FHIRStore) -> TestClient:
    """Create a test client."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


class TestConditionalCreate:
    """Tests for conditional create (If-None-Exist header)."""

    def test_conditional_create_no_match(self, client):
        """Test conditional create with no existing match creates resource."""
        # Create with unique identifier
        response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "unique-123"}],
                "name": [{"family": "Test"}],
            },
            headers={"If-None-Exist": "identifier=test|unique-123"},
        )

        assert response.status_code == 201
        patient = response.json()
        assert patient["resourceType"] == "Patient"
        assert "id" in patient

    def test_conditional_create_single_match(self, client):
        """Test conditional create with single match returns existing (200)."""
        # First create a patient
        create_response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "cond-create-match"}],
                "name": [{"family": "Original"}],
            },
        )
        assert create_response.status_code == 201
        original = create_response.json()

        # Try conditional create with same identifier
        response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "cond-create-match"}],
                "name": [{"family": "New"}],
            },
            headers={"If-None-Exist": "identifier=test|cond-create-match"},
        )

        # Should return 200 with existing resource
        assert response.status_code == 200
        returned = response.json()
        assert returned["id"] == original["id"]
        assert returned["name"][0]["family"] == "Original"  # Not updated

    def test_conditional_create_multiple_matches(self, client):
        """Test conditional create with multiple matches returns 412."""
        # Create two patients with same family name
        client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "DuplicateFamily"}],
            },
        )
        client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "DuplicateFamily"}],
            },
        )

        # Try conditional create matching both
        response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "DuplicateFamily"}],
            },
            headers={"If-None-Exist": "family=DuplicateFamily"},
        )

        assert response.status_code == 412
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"
        assert "match" in outcome["issue"][0]["diagnostics"].lower()

    def test_conditional_create_without_header(self, client):
        """Test regular create works without If-None-Exist header."""
        response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Regular"}],
            },
        )

        assert response.status_code == 201


class TestConditionalUpdate:
    """Tests for conditional update (PUT with search params)."""

    def test_conditional_update_no_match_creates(self, client):
        """Test conditional update with no match creates new resource."""
        response = client.put(
            "/Patient?identifier=test|new-cond-update",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "new-cond-update"}],
                "name": [{"family": "NewPatient"}],
            },
        )

        assert response.status_code == 201
        patient = response.json()
        assert patient["name"][0]["family"] == "NewPatient"

    def test_conditional_update_single_match_updates(self, client):
        """Test conditional update with single match updates the resource."""
        # First create a patient
        create_response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "cond-update-test"}],
                "name": [{"family": "Original"}],
            },
        )
        assert create_response.status_code == 201
        original = create_response.json()

        # Conditional update by identifier
        response = client.put(
            "/Patient?identifier=test|cond-update-test",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "cond-update-test"}],
                "name": [{"family": "Updated"}],
            },
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["id"] == original["id"]
        assert updated["name"][0]["family"] == "Updated"

    def test_conditional_update_multiple_matches(self, client):
        """Test conditional update with multiple matches returns 412."""
        # Create two patients with same gender
        client.post(
            "/Patient",
            json={"resourceType": "Patient", "gender": "other", "name": [{"family": "A"}]},
        )
        client.post(
            "/Patient",
            json={"resourceType": "Patient", "gender": "other", "name": [{"family": "B"}]},
        )

        # Try conditional update matching both
        response = client.put(
            "/Patient?gender=other",
            json={
                "resourceType": "Patient",
                "gender": "other",
                "name": [{"family": "Updated"}],
            },
        )

        assert response.status_code == 412
        outcome = response.json()
        assert outcome["resourceType"] == "OperationOutcome"

    def test_conditional_update_no_params(self, client):
        """Test conditional update without search params returns 400."""
        response = client.put(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "Test"}]},
        )

        assert response.status_code == 400
        outcome = response.json()
        assert "requires search parameters" in outcome["issue"][0]["diagnostics"]

    def test_conditional_update_wrong_resource_type(self, client):
        """Test conditional update with wrong resourceType in body."""
        response = client.put(
            "/Patient?identifier=test|xyz",
            json={"resourceType": "Observation", "status": "final"},
        )

        assert response.status_code == 400


class TestConditionalDelete:
    """Tests for conditional delete (DELETE with search params)."""

    def test_conditional_delete_deletes_matches(self, client):
        """Test conditional delete removes all matching resources."""
        # Create some patients to delete
        for i in range(3):
            client.post(
                "/Observation",
                json={
                    "resourceType": "Observation",
                    "status": "cancelled",
                    "code": {"text": f"test-delete-{i}"},
                },
            )

        # Search to verify they exist
        search_before = client.get("/Observation?status=cancelled")
        count_before = search_before.json().get("total", 0)
        assert count_before >= 3

        # Conditional delete
        response = client.delete("/Observation?status=cancelled")

        assert response.status_code == 204

        # Verify they're deleted
        search_after = client.get("/Observation?status=cancelled")
        count_after = search_after.json().get("total", 0)
        assert count_after == 0

    def test_conditional_delete_no_match(self, client):
        """Test conditional delete with no matches returns 204."""
        response = client.delete("/Patient?identifier=nonexistent|12345")

        # FHIR spec: return 204 even if nothing deleted
        assert response.status_code == 204

    def test_conditional_delete_no_params(self, client):
        """Test conditional delete without search params returns 400."""
        response = client.delete("/Patient")

        assert response.status_code == 400
        outcome = response.json()
        assert "requires search parameters" in outcome["issue"][0]["diagnostics"]

    def test_conditional_delete_unsupported_type(self, client):
        """Test conditional delete with unsupported type returns 400."""
        response = client.delete("/UnsupportedType?code=test")

        assert response.status_code == 400
        outcome = response.json()
        assert "not supported" in outcome["issue"][0]["diagnostics"]

    def test_conditional_delete_single_resource(self, client):
        """Test conditional delete removes exactly one matched resource."""
        # Create a patient with unique identifier
        create_response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "test", "value": "single-delete-test"}],
                "name": [{"family": "ToDelete"}],
            },
        )
        patient_id = create_response.json()["id"]

        # Delete by identifier
        response = client.delete("/Patient?identifier=test|single-delete-test")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/Patient/{patient_id}")
        assert get_response.status_code == 404
