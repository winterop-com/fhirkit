"""Tests for FHIR server REST API."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store():
    """Create a fresh FHIR store."""
    return FHIRStore()


@pytest.fixture
def client(store):
    """Create a test client with empty store."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


@pytest.fixture
def client_with_data(store):
    """Create a test client with preloaded data."""
    # Add some test resources
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "Smith", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1980-01-15",
        }
    )
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-2",
            "name": [{"family": "Doe", "given": ["Jane"]}],
            "gender": "female",
            "birthDate": "1990-05-20",
        }
    )
    store.create(
        {
            "resourceType": "Condition",
            "id": "test-condition-1",
            "subject": {"reference": "Patient/test-patient-1"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
        }
    )

    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


class TestMetadata:
    """Tests for CapabilityStatement endpoint."""

    def test_get_metadata(self, client):
        """Test GET /metadata returns CapabilityStatement."""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "CapabilityStatement"
        assert data["fhirVersion"] == "4.0.1"
        assert data["status"] == "active"
        assert "rest" in data

    def test_metadata_lists_resources(self, client):
        """Test that metadata lists supported resources."""
        response = client.get("/metadata")
        data = response.json()

        resources = data["rest"][0]["resource"]
        resource_types = {r["type"] for r in resources}

        assert "Patient" in resource_types
        assert "Condition" in resource_types
        assert "Observation" in resource_types


class TestCRUDOperations:
    """Tests for CRUD operations."""

    def test_create_patient(self, client):
        """Test creating a patient via POST."""
        patient = {
            "resourceType": "Patient",
            "name": [{"family": "Test", "given": ["User"]}],
            "gender": "male",
        }

        response = client.post("/Patient", json=patient)
        assert response.status_code == 201

        data = response.json()
        assert data["resourceType"] == "Patient"
        assert "id" in data
        assert data["name"][0]["family"] == "Test"

    def test_create_with_wrong_type(self, client):
        """Test that POST validates resource type."""
        patient = {
            "resourceType": "Observation",  # Wrong type for /Patient endpoint
            "status": "final",
        }

        response = client.post("/Patient", json=patient)
        assert response.status_code == 400

    def test_read_patient(self, client_with_data):
        """Test reading a patient by ID."""
        response = client_with_data.get("/Patient/test-patient-1")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Patient"
        assert data["id"] == "test-patient-1"
        assert data["name"][0]["family"] == "Smith"

    def test_read_not_found(self, client):
        """Test reading a non-existent patient."""
        response = client.get("/Patient/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert data["resourceType"] == "OperationOutcome"

    def test_update_patient(self, client_with_data):
        """Test updating a patient via PUT."""
        updated = {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "Smith-Updated", "given": ["John"]}],
            "gender": "male",
        }

        response = client_with_data.put("/Patient/test-patient-1", json=updated)
        assert response.status_code == 200

        data = response.json()
        assert data["name"][0]["family"] == "Smith-Updated"

    def test_delete_patient(self, client_with_data):
        """Test deleting a patient."""
        response = client_with_data.delete("/Patient/test-patient-1")
        assert response.status_code == 204

        # Verify it's gone
        response = client_with_data.get("/Patient/test-patient-1")
        assert response.status_code == 404


class TestSearch:
    """Tests for search operations."""

    def test_search_all_patients(self, client_with_data):
        """Test searching for all patients."""
        response = client_with_data.get("/Patient")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert data["total"] == 2

    def test_search_by_id(self, client_with_data):
        """Test searching by _id parameter."""
        response = client_with_data.get("/Patient", params={"_id": "test-patient-1"})
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["id"] == "test-patient-1"

    def test_search_by_family_name(self, client_with_data):
        """Test searching by family name."""
        response = client_with_data.get("/Patient", params={"family": "Smith"})
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["name"][0]["family"] == "Smith"

    def test_search_by_gender(self, client_with_data):
        """Test searching by gender."""
        response = client_with_data.get("/Patient", params={"gender": "female"})
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["gender"] == "female"

    def test_search_conditions_by_patient(self, client_with_data):
        """Test searching conditions by patient reference."""
        response = client_with_data.get(
            "/Condition",
            params={"patient": "Patient/test-patient-1"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1

    def test_search_conditions_by_code(self, client_with_data):
        """Test searching conditions by code."""
        response = client_with_data.get(
            "/Condition",
            params={"code": "http://snomed.info/sct|44054006"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1

    def test_search_pagination(self, client_with_data):
        """Test search pagination."""
        response = client_with_data.get("/Patient", params={"_count": 1})
        assert response.status_code == 200

        data = response.json()
        assert len(data.get("entry", [])) == 1
        assert "link" in data  # Should have pagination links


class TestHistory:
    """Tests for history operations."""

    def test_instance_history(self, client, store):
        """Test getting history of a resource."""
        # Create and update a resource
        patient = {
            "resourceType": "Patient",
            "name": [{"family": "Original"}],
        }
        response = client.post("/Patient", json=patient)
        patient_id = response.json()["id"]

        # Update
        updated = {
            "resourceType": "Patient",
            "id": patient_id,
            "name": [{"family": "Updated"}],
        }
        client.put(f"/Patient/{patient_id}", json=updated)

        # Get history
        response = client.get(f"/Patient/{patient_id}/_history")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "history"
        assert data["total"] == 2


class TestBatch:
    """Tests for batch/transaction operations."""

    def test_batch_create(self, client):
        """Test batch creation of resources."""
        batch = {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "Batch1"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "Batch2"}],
                    },
                    "request": {"method": "POST", "url": "Patient"},
                },
            ],
        }

        response = client.post("/", json=batch)
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "batch-response"
        assert len(data["entry"]) == 2


class TestFHIRStore:
    """Tests for FHIRStore."""

    def test_create_generates_id(self):
        """Test that create generates ID if not provided."""
        store = FHIRStore()
        resource = {"resourceType": "Patient", "name": [{"family": "Test"}]}

        created = store.create(resource)
        assert "id" in created
        assert len(created["id"]) > 0

    def test_create_uses_provided_id(self):
        """Test that create uses provided ID."""
        store = FHIRStore()
        resource = {
            "resourceType": "Patient",
            "id": "my-custom-id",
            "name": [{"family": "Test"}],
        }

        created = store.create(resource)
        assert created["id"] == "my-custom-id"

    def test_create_sets_meta(self):
        """Test that create sets meta information."""
        store = FHIRStore()
        resource = {"resourceType": "Patient"}

        created = store.create(resource)
        assert "meta" in created
        assert "versionId" in created["meta"]
        assert "lastUpdated" in created["meta"]

    def test_update_increments_version(self):
        """Test that update increments version."""
        store = FHIRStore()
        resource = {"resourceType": "Patient", "id": "test"}

        created = store.create(resource)
        v1 = created["meta"]["versionId"]

        updated = store.update("Patient", "test", {"resourceType": "Patient", "id": "test"})
        v2 = updated["meta"]["versionId"]

        assert int(v2) > int(v1)

    def test_search_with_params(self):
        """Test search with parameters."""
        store = FHIRStore()
        store.create(
            {
                "resourceType": "Patient",
                "id": "p1",
                "gender": "male",
            }
        )
        store.create(
            {
                "resourceType": "Patient",
                "id": "p2",
                "gender": "female",
            }
        )

        results, total = store.search("Patient", {"gender": "male"})
        assert total == 1
        assert results[0]["id"] == "p1"

    def test_history_returns_versions(self):
        """Test that history returns all versions."""
        store = FHIRStore()
        resource = {"resourceType": "Patient", "id": "test"}

        store.create(resource)
        store.update("Patient", "test", {**resource, "active": True})
        store.update("Patient", "test", {**resource, "active": False})

        history = store.history("Patient", "test")
        assert len(history) == 3


class TestTransaction:
    """Tests for transaction atomicity."""

    def test_transaction_success(self, client):
        """Test successful transaction commits all changes."""
        transaction = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "txn-patient-1",
                        "name": [{"family": "Transaction1"}],
                    },
                    "request": {"method": "PUT", "url": "Patient/txn-patient-1"},
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "txn-patient-2",
                        "name": [{"family": "Transaction2"}],
                    },
                    "request": {"method": "PUT", "url": "Patient/txn-patient-2"},
                },
            ],
        }

        response = client.post("/", json=transaction)
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "transaction-response"

        # Verify both patients were created
        response1 = client.get("/Patient/txn-patient-1")
        assert response1.status_code == 200

        response2 = client.get("/Patient/txn-patient-2")
        assert response2.status_code == 200

    def test_transaction_rollback_on_failure(self, client, store):
        """Test that failed transaction rolls back all changes."""
        # First create a patient
        store.create(
            {
                "resourceType": "Patient",
                "id": "existing-patient",
                "name": [{"family": "Original"}],
            }
        )

        # Transaction with one valid and one invalid entry
        # The invalid entry references a non-existent resource type endpoint
        transaction = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "new-patient",
                        "name": [{"family": "New"}],
                    },
                    "request": {"method": "PUT", "url": "Patient/new-patient"},
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "another-patient",
                        "name": [{"family": "Another"}],
                    },
                    "request": {
                        "method": "GET",
                        "url": "Patient/nonexistent-for-get",
                    },  # GET on non-existent
                },
            ],
        }

        response = client.post("/", json=transaction)
        # Transaction should fail
        assert response.status_code in (400, 404, 500)

        # Verify the new patient was NOT created (rolled back)
        response = client.get("/Patient/new-patient")
        assert response.status_code == 404

    def test_batch_does_not_rollback(self, client):
        """Test that batch processes independently without rollback."""
        batch = {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "batch-patient-1",
                        "name": [{"family": "Batch1"}],
                    },
                    "request": {"method": "PUT", "url": "Patient/batch-patient-1"},
                },
                {
                    "request": {"method": "GET", "url": "Patient/nonexistent"},
                },  # This will fail
            ],
        }

        response = client.post("/", json=batch)
        # Batch should succeed overall
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "batch-response"

        # First entry should have succeeded
        response = client.get("/Patient/batch-patient-1")
        assert response.status_code == 200

    def test_store_transaction_context_manager(self):
        """Test FHIRStore transaction context manager."""
        store = FHIRStore()

        # Create initial resource
        store.create(
            {
                "resourceType": "Patient",
                "id": "ctx-patient",
                "name": [{"family": "Original"}],
            }
        )

        # Test successful transaction
        with store.transaction():
            store.update(
                "Patient",
                "ctx-patient",
                {
                    "resourceType": "Patient",
                    "id": "ctx-patient",
                    "name": [{"family": "Updated"}],
                },
            )

        # Should be updated
        patient = store.read("Patient", "ctx-patient")
        assert patient["name"][0]["family"] == "Updated"

    def test_store_transaction_rollback(self):
        """Test FHIRStore transaction rollback on exception."""
        store = FHIRStore()

        # Create initial resource
        store.create(
            {
                "resourceType": "Patient",
                "id": "rollback-patient",
                "name": [{"family": "Original"}],
            }
        )

        # Test failed transaction
        try:
            with store.transaction():
                store.update(
                    "Patient",
                    "rollback-patient",
                    {
                        "resourceType": "Patient",
                        "id": "rollback-patient",
                        "name": [{"family": "Modified"}],
                    },
                )
                raise ValueError("Simulated failure")
        except Exception:
            pass

        # Should be rolled back to original
        patient = store.read("Patient", "rollback-patient")
        assert patient["name"][0]["family"] == "Original"
