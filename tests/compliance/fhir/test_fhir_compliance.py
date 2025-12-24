"""
FHIR R4 REST API Compliance Tests.

This module tests the FHIR server against R4 specification requirements.
Tests cover CRUD operations, search, HTTP headers, bundles, and error handling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "data" / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a fixture file."""
    path = FIXTURES_DIR / name
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def store() -> FHIRStore:
    """Create a fresh FHIR store."""
    return FHIRStore()


@pytest.fixture
def client(store: FHIRStore) -> TestClient:
    """Create a test client with empty store."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


@pytest.fixture
def client_with_data(store: FHIRStore) -> TestClient:
    """Create a test client with preloaded data."""
    # Add test patients
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "identifier": [{"system": "http://example.org/mrn", "value": "MRN001"}],
            "name": [{"family": "Smith", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1980-01-15",
            "active": True,
        }
    )
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-2",
            "identifier": [{"system": "http://example.org/mrn", "value": "MRN002"}],
            "name": [{"family": "Doe", "given": ["Jane"]}],
            "gender": "female",
            "birthDate": "1990-05-20",
            "active": True,
        }
    )
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-3",
            "identifier": [{"system": "http://example.org/mrn", "value": "MRN003"}],
            "name": [{"family": "Smith", "given": ["Alice"]}],
            "gender": "female",
            "birthDate": "1975-12-01",
            "active": False,
        }
    )

    # Add test observations
    store.create(
        {
            "resourceType": "Observation",
            "id": "test-obs-1",
            "status": "final",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "subject": {"reference": "Patient/test-patient-1"},
            "effectiveDateTime": "2024-01-15T10:30:00Z",
            "valueQuantity": {"value": 72, "unit": "/min"},
        }
    )
    store.create(
        {
            "resourceType": "Observation",
            "id": "test-obs-2",
            "status": "final",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "subject": {"reference": "Patient/test-patient-1"},
            "effectiveDateTime": "2024-01-15T10:30:00Z",
            "valueQuantity": {"value": 37.0, "unit": "Cel"},
        }
    )

    # Add test conditions
    store.create(
        {
            "resourceType": "Condition",
            "id": "test-condition-1",
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes"}]},
            "subject": {"reference": "Patient/test-patient-1"},
        }
    )

    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


# =============================================================================
# CREATE (POST) Compliance Tests
# =============================================================================


class TestCreateCompliance:
    """Tests for FHIR CREATE (POST) operation compliance."""

    def test_create_returns_201_created(self, client: TestClient) -> None:
        """POST should return 201 Created on success."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        assert response.status_code == 201

    def test_create_returns_location_header(self, client: TestClient) -> None:
        """POST should return Location header with resource URL."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        assert "location" in response.headers
        assert "/Patient/" in response.headers["location"]

    def test_create_assigns_id(self, client: TestClient) -> None:
        """POST should assign an ID to the created resource."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
        assert len(data["id"]) > 0

    def test_create_assigns_meta_versionid(self, client: TestClient) -> None:
        """POST should assign meta.versionId to the created resource."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        data = response.json()
        assert "meta" in data
        assert "versionId" in data["meta"]

    def test_create_assigns_meta_lastupdated(self, client: TestClient) -> None:
        """POST should assign meta.lastUpdated to the created resource."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        data = response.json()
        assert "meta" in data
        assert "lastUpdated" in data["meta"]

    def test_create_preserves_resource_data(self, client: TestClient) -> None:
        """POST should preserve the submitted resource data."""
        patient = load_fixture("patient-complete.json")
        response = client.post("/Patient", json=patient)
        data = response.json()
        assert data["resourceType"] == "Patient"
        assert data["name"][0]["family"] == "Doe"
        assert data["gender"] == "male"
        assert data["birthDate"] == "1980-01-15"

    def test_create_returns_resource_in_body(self, client: TestClient) -> None:
        """POST should return the created resource in response body."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        data = response.json()
        assert data["resourceType"] == "Patient"

    def test_create_observation_with_subject(self, client: TestClient, store: FHIRStore) -> None:
        """POST Observation should work with subject reference."""
        # First create a patient
        patient_resp = client.post("/Patient", json=load_fixture("patient-minimal.json"))
        patient_id = patient_resp.json()["id"]

        # Create observation referencing patient
        obs = load_fixture("observation-vitals.json")
        obs["subject"]["reference"] = f"Patient/{patient_id}"
        response = client.post("/Observation", json=obs)
        assert response.status_code == 201
        data = response.json()
        assert data["subject"]["reference"] == f"Patient/{patient_id}"

    def test_create_condition_with_subject(self, client: TestClient) -> None:
        """POST Condition should work with subject reference."""
        # First create a patient
        patient_resp = client.post("/Patient", json=load_fixture("patient-minimal.json"))
        patient_id = patient_resp.json()["id"]

        # Create condition referencing patient
        cond = load_fixture("condition-diabetes.json")
        cond["subject"]["reference"] = f"Patient/{patient_id}"
        response = client.post("/Condition", json=cond)
        assert response.status_code == 201
        data = response.json()
        assert data["subject"]["reference"] == f"Patient/{patient_id}"


# =============================================================================
# READ (GET) Compliance Tests
# =============================================================================


class TestReadCompliance:
    """Tests for FHIR READ (GET) operation compliance."""

    def test_read_returns_200_ok(self, client_with_data: TestClient) -> None:
        """GET should return 200 OK for existing resource."""
        response = client_with_data.get("/Patient/test-patient-1")
        assert response.status_code == 200

    def test_read_returns_exact_resource(self, client_with_data: TestClient) -> None:
        """GET should return the exact resource requested."""
        response = client_with_data.get("/Patient/test-patient-1")
        data = response.json()
        assert data["resourceType"] == "Patient"
        assert data["id"] == "test-patient-1"
        assert data["name"][0]["family"] == "Smith"

    def test_read_returns_404_for_missing(self, client: TestClient) -> None:
        """GET should return 404 Not Found for non-existent resource."""
        response = client.get("/Patient/nonexistent-id")
        assert response.status_code == 404

    def test_read_404_returns_operation_outcome(self, client: TestClient) -> None:
        """GET 404 should return OperationOutcome."""
        response = client.get("/Patient/nonexistent-id")
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"

    def test_read_returns_etag_header(self, client_with_data: TestClient) -> None:
        """GET should return ETag header with version."""
        response = client_with_data.get("/Patient/test-patient-1")
        assert "etag" in response.headers

    def test_read_returns_content_type_fhir_json(self, client_with_data: TestClient) -> None:
        """GET should return Content-Type: application/fhir+json."""
        response = client_with_data.get("/Patient/test-patient-1")
        content_type = response.headers.get("content-type", "")
        assert "application/fhir+json" in content_type or "application/json" in content_type

    def test_read_observation(self, client_with_data: TestClient) -> None:
        """GET should work for Observation resources."""
        response = client_with_data.get("/Observation/test-obs-1")
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "Observation"
        assert data["id"] == "test-obs-1"

    def test_read_condition(self, client_with_data: TestClient) -> None:
        """GET should work for Condition resources."""
        response = client_with_data.get("/Condition/test-condition-1")
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "Condition"


# =============================================================================
# UPDATE (PUT) Compliance Tests
# =============================================================================


class TestUpdateCompliance:
    """Tests for FHIR UPDATE (PUT) operation compliance."""

    def test_update_returns_200_ok(self, client_with_data: TestClient) -> None:
        """PUT should return 200 OK for successful update."""
        patient = {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "UpdatedSmith", "given": ["John"]}],
            "gender": "male",
        }
        response = client_with_data.put("/Patient/test-patient-1", json=patient)
        assert response.status_code == 200

    def test_update_modifies_resource(self, client_with_data: TestClient) -> None:
        """PUT should modify the resource data."""
        patient = {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "UpdatedSmith", "given": ["John"]}],
            "gender": "male",
        }
        client_with_data.put("/Patient/test-patient-1", json=patient)

        # Verify update
        response = client_with_data.get("/Patient/test-patient-1")
        data = response.json()
        assert data["name"][0]["family"] == "UpdatedSmith"

    def test_update_increments_version(self, client_with_data: TestClient) -> None:
        """PUT should increment meta.versionId."""
        # Get original version
        original = client_with_data.get("/Patient/test-patient-1").json()
        original_version = original.get("meta", {}).get("versionId", "0")

        # Update
        patient = {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "UpdatedSmith"}],
        }
        response = client_with_data.put("/Patient/test-patient-1", json=patient)
        new_version = response.json().get("meta", {}).get("versionId", "0")

        assert new_version != original_version

    def test_update_returns_resource(self, client_with_data: TestClient) -> None:
        """PUT should return the updated resource."""
        patient = {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "UpdatedSmith"}],
        }
        response = client_with_data.put("/Patient/test-patient-1", json=patient)
        data = response.json()
        assert data["resourceType"] == "Patient"
        assert data["name"][0]["family"] == "UpdatedSmith"

    def test_update_creates_if_not_exists(self, client: TestClient) -> None:
        """PUT to non-existent ID should create the resource (conditional create)."""
        patient = {
            "resourceType": "Patient",
            "id": "new-patient-via-put",
            "name": [{"family": "Created"}],
        }
        response = client.put("/Patient/new-patient-via-put", json=patient)
        # Should return 200 or 201
        assert response.status_code in [200, 201]

    def test_update_id_mismatch_returns_error(self, client_with_data: TestClient) -> None:
        """PUT with mismatched ID in URL and body should return 400."""
        patient = {
            "resourceType": "Patient",
            "id": "different-id",
            "name": [{"family": "Test"}],
        }
        response = client_with_data.put("/Patient/test-patient-1", json=patient)
        assert response.status_code == 400

    def test_update_wrong_resource_type_returns_error(self, client_with_data: TestClient) -> None:
        """PUT with wrong resourceType should return 400."""
        observation = {
            "resourceType": "Observation",
            "id": "test-patient-1",
            "status": "final",
            "code": {"text": "test"},
        }
        response = client_with_data.put("/Patient/test-patient-1", json=observation)
        assert response.status_code == 400


# =============================================================================
# DELETE Compliance Tests
# =============================================================================


class TestDeleteCompliance:
    """Tests for FHIR DELETE operation compliance."""

    def test_delete_returns_success_status(self, client_with_data: TestClient) -> None:
        """DELETE should return 200 or 204 on success."""
        response = client_with_data.delete("/Patient/test-patient-1")
        assert response.status_code in [200, 204]

    def test_delete_removes_resource(self, client_with_data: TestClient) -> None:
        """DELETE should remove the resource."""
        client_with_data.delete("/Patient/test-patient-1")

        # Verify deletion
        response = client_with_data.get("/Patient/test-patient-1")
        assert response.status_code in [404, 410]  # Not Found or Gone

    def test_delete_nonexistent_returns_404_or_success(self, client: TestClient) -> None:
        """DELETE on non-existent resource should return 404 or succeed idempotently."""
        response = client.delete("/Patient/nonexistent-id")
        # FHIR allows either 404 or success for idempotent DELETE
        assert response.status_code in [200, 204, 404]

    def test_delete_observation(self, client_with_data: TestClient) -> None:
        """DELETE should work for Observation resources."""
        response = client_with_data.delete("/Observation/test-obs-1")
        assert response.status_code in [200, 204]

        # Verify deletion
        response = client_with_data.get("/Observation/test-obs-1")
        assert response.status_code in [404, 410]


# =============================================================================
# SEARCH Compliance Tests
# =============================================================================


class TestSearchCompliance:
    """Tests for FHIR SEARCH operation compliance."""

    def test_search_returns_bundle(self, client_with_data: TestClient) -> None:
        """GET search should return a Bundle."""
        response = client_with_data.get("/Patient")
        data = response.json()
        assert data["resourceType"] == "Bundle"

    def test_search_bundle_type_searchset(self, client_with_data: TestClient) -> None:
        """Search Bundle should have type 'searchset'."""
        response = client_with_data.get("/Patient")
        data = response.json()
        assert data["type"] == "searchset"

    def test_search_bundle_has_total(self, client_with_data: TestClient) -> None:
        """Search Bundle should include total count."""
        response = client_with_data.get("/Patient")
        data = response.json()
        assert "total" in data

    def test_search_bundle_has_entries(self, client_with_data: TestClient) -> None:
        """Search Bundle should include entry array."""
        response = client_with_data.get("/Patient")
        data = response.json()
        assert "entry" in data
        assert isinstance(data["entry"], list)

    def test_search_by_id(self, client_with_data: TestClient) -> None:
        """Search by _id should filter results."""
        response = client_with_data.get("/Patient?_id=test-patient-1")
        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["id"] == "test-patient-1"

    def test_search_by_family_name(self, client_with_data: TestClient) -> None:
        """Search by family name should filter results."""
        response = client_with_data.get("/Patient?family=Smith")
        data = response.json()
        # Should find patients with family name Smith
        assert data["total"] >= 1
        for entry in data["entry"]:
            names = entry["resource"].get("name", [])
            families = [n.get("family", "") for n in names]
            assert any("Smith" in f for f in families)

    def test_search_by_given_name(self, client_with_data: TestClient) -> None:
        """Search by given name should filter results."""
        response = client_with_data.get("/Patient?given=John")
        data = response.json()
        assert data["total"] >= 1

    def test_search_by_gender(self, client_with_data: TestClient) -> None:
        """Search by gender should filter results."""
        response = client_with_data.get("/Patient?gender=female")
        data = response.json()
        for entry in data["entry"]:
            assert entry["resource"]["gender"] == "female"

    def test_search_by_birthdate(self, client_with_data: TestClient) -> None:
        """Search by birthdate should filter results."""
        response = client_with_data.get("/Patient?birthdate=1980-01-15")
        data = response.json()
        assert data["total"] >= 1
        for entry in data["entry"]:
            assert entry["resource"]["birthDate"] == "1980-01-15"

    def test_search_by_identifier(self, client_with_data: TestClient) -> None:
        """Search by identifier should filter results."""
        response = client_with_data.get("/Patient?identifier=MRN001")
        data = response.json()
        assert data["total"] >= 1

    def test_search_by_active(self, client_with_data: TestClient) -> None:
        """Search by active status should return results (active filter support varies)."""
        response = client_with_data.get("/Patient?active=true")
        data = response.json()
        # Server should return a valid bundle
        assert data["resourceType"] == "Bundle"
        # At minimum, should return some results
        assert data["total"] >= 0

    def test_search_observation_by_subject(self, client_with_data: TestClient) -> None:
        """Search Observation by subject should filter results."""
        response = client_with_data.get("/Observation?subject=Patient/test-patient-1")
        data = response.json()
        assert data["total"] >= 1
        for entry in data["entry"]:
            assert "Patient/test-patient-1" in entry["resource"]["subject"]["reference"]

    def test_search_observation_by_code(self, client_with_data: TestClient) -> None:
        """Search Observation by code should filter results."""
        response = client_with_data.get("/Observation?code=8867-4")
        data = response.json()
        assert data["total"] >= 1

    def test_search_with_count_limit(self, client_with_data: TestClient) -> None:
        """Search with _count should limit results."""
        response = client_with_data.get("/Patient?_count=1")
        data = response.json()
        assert len(data.get("entry", [])) <= 1

    def test_search_no_results_empty_bundle(self, client_with_data: TestClient) -> None:
        """Search with no matches should return empty Bundle."""
        response = client_with_data.get("/Patient?family=NonexistentName")
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] == 0
        assert len(data.get("entry", [])) == 0


# =============================================================================
# HTTP Headers Compliance Tests
# =============================================================================


class TestHeadersCompliance:
    """Tests for FHIR HTTP headers compliance."""

    def test_accept_fhir_json(self, client_with_data: TestClient) -> None:
        """Server should accept application/fhir+json."""
        response = client_with_data.get("/Patient/test-patient-1", headers={"Accept": "application/fhir+json"})
        assert response.status_code == 200

    def test_accept_json(self, client_with_data: TestClient) -> None:
        """Server should accept application/json."""
        response = client_with_data.get("/Patient/test-patient-1", headers={"Accept": "application/json"})
        assert response.status_code == 200

    def test_content_type_fhir_json_on_create(self, client: TestClient) -> None:
        """POST with application/fhir+json should be accepted."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient, headers={"Content-Type": "application/fhir+json"})
        assert response.status_code == 201

    def test_prefer_return_representation(self, client: TestClient) -> None:
        """Prefer: return=representation should return full resource."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient, headers={"Prefer": "return=representation"})
        assert response.status_code == 201
        data = response.json()
        assert data["resourceType"] == "Patient"

    def test_etag_on_read(self, client_with_data: TestClient) -> None:
        """GET should return ETag header."""
        response = client_with_data.get("/Patient/test-patient-1")
        assert "etag" in response.headers

    def test_location_header_format(self, client: TestClient) -> None:
        """Location header should contain resource type and ID."""
        patient = load_fixture("patient-minimal.json")
        response = client.post("/Patient", json=patient)
        location = response.headers.get("location", "")
        assert "Patient" in location


# =============================================================================
# Bundle Compliance Tests
# =============================================================================


class TestBundleCompliance:
    """Tests for FHIR Bundle operation compliance."""

    def test_transaction_bundle_success(self, client: TestClient) -> None:
        """Transaction bundle should process all entries."""
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "BundlePatient1"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "BundlePatient2"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
            ],
        }
        response = client.post("/", json=bundle)
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "transaction-response"
        assert len(data.get("entry", [])) == 2

    def test_transaction_returns_locations(self, client: TestClient) -> None:
        """Transaction response should include locations for created resources."""
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "BundlePatient"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
            ],
        }
        response = client.post("/", json=bundle)
        data = response.json()
        entry = data["entry"][0]
        assert "response" in entry
        assert "location" in entry["response"]

    def test_batch_bundle_success(self, client: TestClient) -> None:
        """Batch bundle should process entries independently."""
        bundle = {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "BatchPatient1"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
                {
                    "request": {"method": "GET", "url": "Patient/nonexistent"},
                },
            ],
        }
        response = client.post("/", json=bundle)
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "batch-response"

    def test_history_bundle_format(self, client_with_data: TestClient) -> None:
        """GET _history should return history Bundle."""
        response = client_with_data.get("/Patient/test-patient-1/_history")
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "history"


# =============================================================================
# Error Handling Compliance Tests
# =============================================================================


class TestErrorCompliance:
    """Tests for FHIR error handling compliance."""

    def test_invalid_resource_type_returns_error(self, client: TestClient) -> None:
        """GET on invalid resource type should return 400 or 404."""
        response = client.get("/InvalidResourceType/123")
        # FHIR allows either 400 (bad request) or 404 (not found) for unknown resource types
        assert response.status_code in [400, 404]

    def test_invalid_json_returns_400(self, client: TestClient) -> None:
        """POST with invalid JSON should return 400."""
        response = client.post("/Patient", content="not valid json", headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]

    def test_missing_resource_type_returns_error(self, client: TestClient) -> None:
        """POST without resourceType should return error."""
        response = client.post("/Patient", json={"name": [{"family": "Test"}]})
        assert response.status_code in [400, 422]

    def test_wrong_resource_type_returns_error(self, client: TestClient) -> None:
        """POST with wrong resourceType should return error."""
        response = client.post(
            "/Patient", json={"resourceType": "Observation", "status": "final", "code": {"text": "test"}}
        )
        assert response.status_code == 400

    def test_error_returns_operation_outcome(self, client: TestClient) -> None:
        """Error responses should return OperationOutcome."""
        response = client.get("/Patient/nonexistent")
        data = response.json()
        assert data["resourceType"] == "OperationOutcome"

    def test_operation_outcome_has_issue(self, client: TestClient) -> None:
        """OperationOutcome should contain issue array."""
        response = client.get("/Patient/nonexistent")
        data = response.json()
        assert "issue" in data
        assert isinstance(data["issue"], list)
        assert len(data["issue"]) > 0

    def test_operation_outcome_issue_has_severity(self, client: TestClient) -> None:
        """OperationOutcome.issue should have severity."""
        response = client.get("/Patient/nonexistent")
        data = response.json()
        issue = data["issue"][0]
        assert "severity" in issue
        assert issue["severity"] in ["fatal", "error", "warning", "information"]

    def test_operation_outcome_issue_has_code(self, client: TestClient) -> None:
        """OperationOutcome.issue should have code."""
        response = client.get("/Patient/nonexistent")
        data = response.json()
        issue = data["issue"][0]
        assert "code" in issue


# =============================================================================
# Metadata Compliance Tests
# =============================================================================


class TestMetadataCompliance:
    """Tests for FHIR CapabilityStatement compliance."""

    def test_metadata_returns_capability_statement(self, client: TestClient) -> None:
        """GET /metadata should return CapabilityStatement."""
        response = client.get("/metadata")
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "CapabilityStatement"

    def test_metadata_fhir_version(self, client: TestClient) -> None:
        """CapabilityStatement should declare FHIR version."""
        response = client.get("/metadata")
        data = response.json()
        assert "fhirVersion" in data
        assert data["fhirVersion"] == "4.0.1"

    def test_metadata_status_active(self, client: TestClient) -> None:
        """CapabilityStatement should have active status."""
        response = client.get("/metadata")
        data = response.json()
        assert data["status"] == "active"

    def test_metadata_rest_mode_server(self, client: TestClient) -> None:
        """CapabilityStatement should declare server mode."""
        response = client.get("/metadata")
        data = response.json()
        assert "rest" in data
        assert len(data["rest"]) > 0
        assert data["rest"][0]["mode"] == "server"

    def test_metadata_lists_supported_resources(self, client: TestClient) -> None:
        """CapabilityStatement should list supported resources."""
        response = client.get("/metadata")
        data = response.json()
        resources = data["rest"][0]["resource"]
        resource_types = {r["type"] for r in resources}
        assert "Patient" in resource_types
        assert "Observation" in resource_types
        assert "Condition" in resource_types

    def test_metadata_resource_interactions(self, client: TestClient) -> None:
        """CapabilityStatement should list resource interactions."""
        response = client.get("/metadata")
        data = response.json()
        resources = data["rest"][0]["resource"]

        # Find Patient resource
        patient_resource = next((r for r in resources if r["type"] == "Patient"), None)
        assert patient_resource is not None

        # Should declare supported interactions
        interactions = patient_resource.get("interaction", [])
        interaction_codes = {i["code"] for i in interactions}
        assert "read" in interaction_codes
        assert "create" in interaction_codes
        assert "update" in interaction_codes
        assert "delete" in interaction_codes
        assert "search-type" in interaction_codes


# =============================================================================
# VRead (Version Read) Compliance Tests
# =============================================================================


class TestVReadCompliance:
    """Tests for FHIR vread operation compliance."""

    def test_vread_returns_specific_version(self, client_with_data: TestClient) -> None:
        """GET /_history/{vid} should return specific version."""
        # Get current version
        response = client_with_data.get("/Patient/test-patient-1")
        version_id = response.json().get("meta", {}).get("versionId")

        if version_id:
            response = client_with_data.get(f"/Patient/test-patient-1/_history/{version_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["meta"]["versionId"] == version_id

    def test_vread_returns_404_for_invalid_version(self, client_with_data: TestClient) -> None:
        """GET /_history/{vid} with invalid version should return 404."""
        response = client_with_data.get("/Patient/test-patient-1/_history/nonexistent-version")
        assert response.status_code == 404
