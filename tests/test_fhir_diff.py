"""Tests for FHIR $diff operation."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.api.diff import compute_diff, diff_to_parameters
from fhirkit.server.config.settings import FHIRServerSettings


@pytest.fixture
def client():
    """Create a test client."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings)
    return TestClient(app)


class TestComputeDiff:
    """Unit tests for compute_diff function."""

    def test_identical_resources(self):
        """Test diff of identical resources returns empty list."""
        resource = {"resourceType": "Patient", "id": "1", "name": [{"family": "Test"}]}
        diff = compute_diff(resource, resource.copy())
        assert diff == []

    def test_added_field(self):
        """Test diff detects added fields."""
        source = {"resourceType": "Patient", "id": "1"}
        target = {"resourceType": "Patient", "id": "1", "gender": "female"}
        diff = compute_diff(source, target)
        assert len(diff) == 1
        assert diff[0]["op"] == "add"
        assert diff[0]["path"] == "/gender"
        assert diff[0]["value"] == "female"

    def test_removed_field(self):
        """Test diff detects removed fields."""
        source = {"resourceType": "Patient", "id": "1", "gender": "male"}
        target = {"resourceType": "Patient", "id": "1"}
        diff = compute_diff(source, target)
        assert len(diff) == 1
        assert diff[0]["op"] == "remove"
        assert diff[0]["path"] == "/gender"

    def test_replaced_field(self):
        """Test diff detects replaced fields."""
        source = {"resourceType": "Patient", "id": "1", "gender": "male"}
        target = {"resourceType": "Patient", "id": "1", "gender": "female"}
        diff = compute_diff(source, target)
        assert len(diff) == 1
        assert diff[0]["op"] == "replace"
        assert diff[0]["path"] == "/gender"
        assert diff[0]["value"] == "female"

    def test_nested_changes(self):
        """Test diff handles nested object changes."""
        source = {"resourceType": "Patient", "name": [{"family": "Old"}]}
        target = {"resourceType": "Patient", "name": [{"family": "New"}]}
        diff = compute_diff(source, target)
        assert len(diff) == 1
        assert diff[0]["path"] == "/name/0/family"
        assert diff[0]["op"] == "replace"
        assert diff[0]["value"] == "New"

    def test_array_element_added(self):
        """Test diff detects added array elements."""
        source = {"identifier": [{"value": "a"}]}
        target = {"identifier": [{"value": "a"}, {"value": "b"}]}
        diff = compute_diff(source, target)
        assert any(op["op"] == "add" and "/identifier/1" in op["path"] for op in diff)

    def test_array_element_removed(self):
        """Test diff detects removed array elements."""
        source = {"identifier": [{"value": "a"}, {"value": "b"}]}
        target = {"identifier": [{"value": "a"}]}
        diff = compute_diff(source, target)
        assert any(op["op"] == "remove" and op["path"] == "/identifier/1" for op in diff)

    def test_type_mismatch(self):
        """Test diff handles type mismatches."""
        source = {"value": "string"}
        target = {"value": 123}
        diff = compute_diff(source, target)
        assert len(diff) == 1
        assert diff[0]["op"] == "replace"
        assert diff[0]["value"] == 123

    def test_multiple_changes(self):
        """Test diff with multiple changes."""
        source = {"a": 1, "b": 2, "c": 3}
        target = {"a": 1, "b": 99, "d": 4}
        diff = compute_diff(source, target)
        # Should have: replace /b, remove /c, add /d
        ops_by_type = {op["path"]: op["op"] for op in diff}
        assert ops_by_type["/b"] == "replace"
        assert ops_by_type["/c"] == "remove"
        assert ops_by_type["/d"] == "add"


class TestDiffToParameters:
    """Tests for diff_to_parameters function."""

    def test_empty_diff(self):
        """Test empty diff returns empty Parameters."""
        result = diff_to_parameters([])
        assert result["resourceType"] == "Parameters"
        assert result["parameter"] == []

    def test_diff_with_operations(self):
        """Test diff operations are converted to Parameters."""
        operations = [
            {"op": "add", "path": "/gender", "value": "female"},
            {"op": "remove", "path": "/birthDate"},
        ]
        result = diff_to_parameters(operations)
        assert result["resourceType"] == "Parameters"
        assert len(result["parameter"]) == 2

        # Check first operation (add)
        add_op = result["parameter"][0]
        assert add_op["name"] == "operation"
        parts = {p["name"]: p for p in add_op["part"]}
        assert parts["type"]["valueCode"] == "add"
        assert parts["path"]["valueString"] == "/gender"
        assert parts["value"]["valueString"] == "female"

        # Check second operation (remove)
        remove_op = result["parameter"][1]
        parts = {p["name"]: p for p in remove_op["part"]}
        assert parts["type"]["valueCode"] == "remove"
        assert "value" not in parts  # Remove has no value

    def test_diff_with_various_value_types(self):
        """Test different value types are handled correctly."""
        operations = [
            {"op": "add", "path": "/active", "value": True},
            {"op": "add", "path": "/count", "value": 42},
            {"op": "add", "path": "/score", "value": 3.14},
            {"op": "add", "path": "/complex", "value": {"nested": "object"}},
        ]
        result = diff_to_parameters(operations)
        params = result["parameter"]

        # Boolean value
        assert params[0]["part"][2]["valueBoolean"] is True

        # Integer value
        assert params[1]["part"][2]["valueInteger"] == 42

        # Float value
        assert params[2]["part"][2]["valueDecimal"] == 3.14

        # Complex value (serialized as JSON string)
        assert "valueString" in params[3]["part"][2]


class TestDiffVersionsEndpoint:
    """Tests for GET /{resource_type}/{id}/$diff endpoint."""

    def test_diff_versions_shows_changes(self, client):
        """Test diff between versions shows changes."""
        # Create a patient
        create_response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Original"}],
            },
        )
        assert create_response.status_code == 201
        patient = create_response.json()
        patient_id = patient["id"]

        # Update the patient
        patient["name"][0]["family"] = "Updated"
        update_response = client.put(f"/Patient/{patient_id}", json=patient)
        assert update_response.status_code == 200

        # Get diff between version 1 and current
        diff_response = client.get(f"/Patient/{patient_id}/$diff?version=1")
        assert diff_response.status_code == 200

        result = diff_response.json()
        assert result["resourceType"] == "Parameters"
        # Should have changes for name and meta/versionId
        assert len(result["parameter"]) > 0

    def test_diff_resource_not_found(self, client):
        """Test diff with non-existent resource returns 404."""
        response = client.get("/Patient/nonexistent/$diff?version=1")
        assert response.status_code == 404

    def test_diff_version_not_found(self, client):
        """Test diff with non-existent version returns 404."""
        # Create a patient
        create_response = client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "Test"}]},
        )
        patient_id = create_response.json()["id"]

        # Try to diff with non-existent version
        response = client.get(f"/Patient/{patient_id}/$diff?version=999")
        assert response.status_code == 404
        outcome = response.json()
        assert "999" in outcome["issue"][0]["diagnostics"]

    def test_diff_same_version(self, client):
        """Test diff of same version returns empty diff."""
        # Create a patient
        create_response = client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "Test"}]},
        )
        patient_id = create_response.json()["id"]

        # Diff version 1 with itself (which is still current)
        response = client.get(f"/Patient/{patient_id}/$diff?version=1")
        assert response.status_code == 200
        result = response.json()
        # No changes between v1 and v1
        assert result["parameter"] == []


class TestDiffResourcesEndpoint:
    """Tests for POST /{resource_type}/$diff endpoint."""

    def test_diff_two_resources(self, client):
        """Test diff between two resources provided in body."""
        response = client.post(
            "/Patient/$diff",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "source",
                        "resource": {
                            "resourceType": "Patient",
                            "id": "1",
                            "name": [{"family": "Original"}],
                        },
                    },
                    {
                        "name": "target",
                        "resource": {
                            "resourceType": "Patient",
                            "id": "1",
                            "name": [{"family": "Modified"}],
                        },
                    },
                ],
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["resourceType"] == "Parameters"
        # Should detect the name change
        assert len(result["parameter"]) > 0

    def test_diff_identical_resources(self, client):
        """Test diff of identical resources returns empty."""
        patient = {"resourceType": "Patient", "id": "1", "name": [{"family": "Same"}]}
        response = client.post(
            "/Patient/$diff",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "source", "resource": patient},
                    {"name": "target", "resource": patient},
                ],
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["parameter"] == []

    def test_diff_missing_source(self, client):
        """Test diff without source parameter returns error."""
        response = client.post(
            "/Patient/$diff",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "target",
                        "resource": {"resourceType": "Patient", "id": "1"},
                    },
                ],
            },
        )
        assert response.status_code == 400
        outcome = response.json()
        assert "source" in outcome["issue"][0]["diagnostics"].lower()

    def test_diff_missing_target(self, client):
        """Test diff without target parameter returns error."""
        response = client.post(
            "/Patient/$diff",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "source",
                        "resource": {"resourceType": "Patient", "id": "1"},
                    },
                ],
            },
        )
        assert response.status_code == 400
        outcome = response.json()
        assert "target" in outcome["issue"][0]["diagnostics"].lower()

    def test_diff_wrong_resource_type(self, client):
        """Test diff with wrong resourceType in source/target."""
        response = client.post(
            "/Patient/$diff",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "source",
                        "resource": {"resourceType": "Observation", "id": "1"},
                    },
                    {
                        "name": "target",
                        "resource": {"resourceType": "Patient", "id": "1"},
                    },
                ],
            },
        )
        assert response.status_code == 400
