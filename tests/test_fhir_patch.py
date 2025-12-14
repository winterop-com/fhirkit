"""Tests for FHIR PATCH operations (JSON Patch RFC 6902)."""

import pytest
from fastapi.testclient import TestClient

from fhir_cql.server.api.app import create_app
from fhir_cql.server.api.patch import PatchError, apply_json_patch
from fhir_cql.server.config.settings import FHIRServerSettings
from fhir_cql.server.storage.fhir_store import FHIRStore

# =============================================================================
# Unit Tests for apply_json_patch
# =============================================================================


class TestApplyJsonPatch:
    """Unit tests for the apply_json_patch function."""

    def test_add_simple_field(self):
        """Test adding a new field to the root object."""
        resource = {"resourceType": "Patient", "id": "123"}
        operations = [{"op": "add", "path": "/active", "value": True}]

        result = apply_json_patch(resource, operations)

        assert result["active"] is True
        assert result["id"] == "123"

    def test_add_to_array_end(self):
        """Test adding to end of array with '-' index."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith"}],
        }
        operations = [{"op": "add", "path": "/name/-", "value": {"family": "Jones"}}]

        result = apply_json_patch(resource, operations)

        assert len(result["name"]) == 2
        assert result["name"][1]["family"] == "Jones"

    def test_add_to_array_index(self):
        """Test inserting at a specific array index."""
        resource = {
            "resourceType": "Patient",
            "telecom": [
                {"system": "phone", "value": "555-1234"},
                {"system": "email", "value": "test@example.com"},
            ],
        }
        operations = [{"op": "add", "path": "/telecom/1", "value": {"system": "fax", "value": "555-9999"}}]

        result = apply_json_patch(resource, operations)

        assert len(result["telecom"]) == 3
        assert result["telecom"][1]["system"] == "fax"
        assert result["telecom"][2]["system"] == "email"

    def test_add_nested_field(self):
        """Test adding a nested field."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith"}],
        }
        operations = [{"op": "add", "path": "/name/0/given", "value": ["John"]}]

        result = apply_json_patch(resource, operations)

        assert result["name"][0]["given"] == ["John"]

    def test_remove_field(self):
        """Test removing a field."""
        resource = {
            "resourceType": "Patient",
            "active": True,
            "gender": "male",
        }
        operations = [{"op": "remove", "path": "/active"}]

        result = apply_json_patch(resource, operations)

        assert "active" not in result
        assert result["gender"] == "male"

    def test_remove_array_element(self):
        """Test removing an element from an array."""
        resource = {
            "resourceType": "Patient",
            "name": [
                {"family": "Smith"},
                {"family": "Jones"},
                {"family": "Williams"},
            ],
        }
        operations = [{"op": "remove", "path": "/name/1"}]

        result = apply_json_patch(resource, operations)

        assert len(result["name"]) == 2
        assert result["name"][0]["family"] == "Smith"
        assert result["name"][1]["family"] == "Williams"

    def test_replace_field(self):
        """Test replacing a field value."""
        resource = {
            "resourceType": "Patient",
            "active": True,
        }
        operations = [{"op": "replace", "path": "/active", "value": False}]

        result = apply_json_patch(resource, operations)

        assert result["active"] is False

    def test_replace_array_element(self):
        """Test replacing an array element."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith"}, {"family": "Jones"}],
        }
        operations = [{"op": "replace", "path": "/name/0/family", "value": "Johnson"}]

        result = apply_json_patch(resource, operations)

        assert result["name"][0]["family"] == "Johnson"

    def test_move_operation(self):
        """Test moving a value from one location to another."""
        resource = {
            "resourceType": "Patient",
            "name": [
                {"family": "Smith", "given": ["John"]},
                {"family": "Jones"},
            ],
        }
        operations = [{"op": "move", "from": "/name/0", "path": "/name/1"}]

        result = apply_json_patch(resource, operations)

        assert len(result["name"]) == 2
        assert result["name"][0]["family"] == "Jones"
        assert result["name"][1]["family"] == "Smith"

    def test_copy_operation(self):
        """Test copying a value from one location to another."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith", "given": ["John"]}],
        }
        operations = [{"op": "copy", "from": "/name/0/given", "path": "/name/0/suffix"}]

        result = apply_json_patch(resource, operations)

        assert result["name"][0]["given"] == ["John"]
        assert result["name"][0]["suffix"] == ["John"]
        # Ensure it's a copy, not a reference
        result["name"][0]["suffix"].append("Jr.")
        assert result["name"][0]["given"] == ["John"]

    def test_test_operation_success(self):
        """Test that 'test' operation passes when values match."""
        resource = {
            "resourceType": "Patient",
            "active": True,
        }
        operations = [
            {"op": "test", "path": "/active", "value": True},
            {"op": "replace", "path": "/active", "value": False},
        ]

        result = apply_json_patch(resource, operations)

        assert result["active"] is False

    def test_test_operation_failure(self):
        """Test that 'test' operation fails when values don't match."""
        resource = {
            "resourceType": "Patient",
            "active": True,
        }
        operations = [
            {"op": "test", "path": "/active", "value": False},
            {"op": "replace", "path": "/active", "value": False},
        ]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "Test failed" in str(exc_info.value)

    def test_multiple_operations(self):
        """Test applying multiple operations in sequence."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith"}],
            "active": True,
        }
        operations = [
            {"op": "add", "path": "/name/0/given", "value": ["John"]},
            {"op": "replace", "path": "/active", "value": False},
            {"op": "add", "path": "/gender", "value": "male"},
        ]

        result = apply_json_patch(resource, operations)

        assert result["name"][0]["given"] == ["John"]
        assert result["active"] is False
        assert result["gender"] == "male"

    def test_invalid_path_no_slash(self):
        """Test that paths not starting with '/' are rejected."""
        resource = {"resourceType": "Patient"}
        operations = [{"op": "add", "path": "active", "value": True}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "must start with '/'" in str(exc_info.value)

    def test_invalid_path_not_found(self):
        """Test that non-existent paths raise errors."""
        resource = {"resourceType": "Patient"}
        operations = [{"op": "remove", "path": "/nonexistent"}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "not found" in str(exc_info.value).lower()

    def test_unknown_operation(self):
        """Test that unknown operations are rejected."""
        resource = {"resourceType": "Patient"}
        operations = [{"op": "invalid", "path": "/active"}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "unknown operation" in str(exc_info.value).lower()

    def test_missing_op_field(self):
        """Test that missing 'op' field raises error."""
        resource = {"resourceType": "Patient"}
        operations = [{"path": "/active", "value": True}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "missing 'op'" in str(exc_info.value).lower()

    def test_add_missing_value(self):
        """Test that 'add' without 'value' raises error."""
        resource = {"resourceType": "Patient"}
        operations = [{"op": "add", "path": "/active"}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "requires 'value'" in str(exc_info.value).lower()

    def test_array_index_out_of_bounds(self):
        """Test that out-of-bounds array index raises error."""
        resource = {
            "resourceType": "Patient",
            "name": [{"family": "Smith"}],
        }
        operations = [{"op": "remove", "path": "/name/5"}]

        with pytest.raises(PatchError) as exc_info:
            apply_json_patch(resource, operations)

        assert "out of bounds" in str(exc_info.value).lower()

    def test_original_not_modified(self):
        """Test that the original resource is not modified."""
        resource = {
            "resourceType": "Patient",
            "active": True,
        }
        original_active = resource["active"]
        operations = [{"op": "replace", "path": "/active", "value": False}]

        result = apply_json_patch(resource, operations)

        assert resource["active"] == original_active
        assert result["active"] is False


# =============================================================================
# Integration Tests for PATCH endpoint
# =============================================================================


class TestPatchEndpoint:
    """Integration tests for the PATCH REST endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client with FHIR server."""
        settings = FHIRServerSettings(patients=0, enable_ui=False, api_base_path="")
        store = FHIRStore()
        app = create_app(settings=settings, store=store)
        return TestClient(app)

    @pytest.fixture
    def patient(self, client):
        """Create a test patient."""
        patient_data = {
            "resourceType": "Patient",
            "name": [{"family": "Smith", "given": ["John"]}],
            "active": True,
            "gender": "male",
            "telecom": [{"system": "phone", "value": "555-1234"}],
        }
        response = client.post("/Patient", json=patient_data)
        assert response.status_code == 201
        return response.json()

    def test_patch_replace_field(self, client, patient):
        """Test patching a single field."""
        patient_id = patient["id"]
        patch = [{"op": "replace", "path": "/active", "value": False}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["active"] is False
        assert result["meta"]["versionId"] == "2"

    def test_patch_add_telecom(self, client, patient):
        """Test adding a telecom entry."""
        patient_id = patient["id"]
        patch = [{"op": "add", "path": "/telecom/-", "value": {"system": "email", "value": "john@example.com"}}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["telecom"]) == 2
        assert result["telecom"][1]["system"] == "email"

    def test_patch_remove_field(self, client, patient):
        """Test removing a field."""
        patient_id = patient["id"]
        patch = [{"op": "remove", "path": "/gender"}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert "gender" not in result

    def test_patch_multiple_operations(self, client, patient):
        """Test multiple patch operations."""
        patient_id = patient["id"]
        patch = [
            {"op": "replace", "path": "/name/0/family", "value": "Johnson"},
            {"op": "add", "path": "/name/0/given/-", "value": "William"},
            {"op": "replace", "path": "/active", "value": False},
        ]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["name"][0]["family"] == "Johnson"
        assert "William" in result["name"][0]["given"]
        assert result["active"] is False

    def test_patch_test_success(self, client, patient):
        """Test patch with test operation that succeeds."""
        patient_id = patient["id"]
        patch = [
            {"op": "test", "path": "/active", "value": True},
            {"op": "replace", "path": "/active", "value": False},
        ]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["active"] is False

    def test_patch_test_failure(self, client, patient):
        """Test patch with test operation that fails."""
        patient_id = patient["id"]
        patch = [
            {"op": "test", "path": "/active", "value": False},  # Will fail
            {"op": "replace", "path": "/active", "value": False},
        ]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 409  # Conflict
        result = response.json()
        assert result["resourceType"] == "OperationOutcome"

    def test_patch_not_found(self, client):
        """Test patching a non-existent resource."""
        patch = [{"op": "replace", "path": "/active", "value": False}]

        response = client.patch(
            "/Patient/nonexistent",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 404

    def test_patch_invalid_path(self, client, patient):
        """Test patching with invalid path."""
        patient_id = patient["id"]
        patch = [{"op": "remove", "path": "/nonexistent/field"}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 422
        result = response.json()
        assert result["resourceType"] == "OperationOutcome"

    def test_patch_cannot_modify_id(self, client, patient):
        """Test that patching cannot modify resource id."""
        patient_id = patient["id"]
        patch = [{"op": "replace", "path": "/id", "value": "different-id"}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 422
        result = response.json()
        assert "Cannot modify resource id" in result["issue"][0]["diagnostics"]

    def test_patch_cannot_modify_resource_type(self, client, patient):
        """Test that patching cannot modify resourceType."""
        patient_id = patient["id"]
        patch = [{"op": "replace", "path": "/resourceType", "value": "Observation"}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 422
        result = response.json()
        assert "Cannot modify resourceType" in result["issue"][0]["diagnostics"]

    def test_patch_invalid_json(self, client, patient):
        """Test patching with invalid JSON body."""
        patient_id = patient["id"]

        response = client.patch(
            f"/Patient/{patient_id}",
            content="not valid json",
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 400

    def test_patch_non_array_body(self, client, patient):
        """Test patching with non-array body."""
        patient_id = patient["id"]
        patch = {"op": "replace", "path": "/active", "value": False}  # Object, not array

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 400
        result = response.json()
        assert "JSON array" in result["issue"][0]["diagnostics"]

    def test_patch_unsupported_resource_type(self, client):
        """Test patching an unsupported resource type."""
        patch = [{"op": "replace", "path": "/active", "value": False}]

        response = client.patch(
            "/UnsupportedType/123",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 400

    def test_patch_returns_etag(self, client, patient):
        """Test that PATCH returns ETag header."""
        patient_id = patient["id"]
        patch = [{"op": "replace", "path": "/active", "value": False}]

        response = client.patch(
            f"/Patient/{patient_id}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        assert "etag" in response.headers
        assert 'W/"2"' in response.headers["etag"]

    def test_patch_observation(self, client):
        """Test patching an Observation resource."""
        # Create observation
        obs_data = {
            "resourceType": "Observation",
            "status": "preliminary",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
        }
        response = client.post("/Observation", json=obs_data)
        assert response.status_code == 201
        obs = response.json()

        # Patch it
        patch = [{"op": "replace", "path": "/status", "value": "final"}]
        response = client.patch(
            f"/Observation/{obs['id']}",
            json=patch,
            headers={"Content-Type": "application/json-patch+json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "final"
