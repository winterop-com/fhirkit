"""Tests for FHIR Bulk Data Export."""

import time

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.api.bulk import resources_to_ndjson
from fhirkit.server.config.settings import FHIRServerSettings


@pytest.fixture
def client():
    """Create a test client."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings)
    return TestClient(app)


class TestResourcesToNdjson:
    """Unit tests for NDJSON conversion."""

    def test_empty_list(self):
        """Test empty list returns empty string."""
        result = resources_to_ndjson([])
        assert result == ""

    def test_single_resource(self):
        """Test single resource conversion."""
        resources = [{"resourceType": "Patient", "id": "1"}]
        result = resources_to_ndjson(resources)
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert '"resourceType":"Patient"' in lines[0]
        assert '"id":"1"' in lines[0]

    def test_multiple_resources(self):
        """Test multiple resources conversion."""
        resources = [
            {"resourceType": "Patient", "id": "1"},
            {"resourceType": "Patient", "id": "2"},
            {"resourceType": "Patient", "id": "3"},
        ]
        result = resources_to_ndjson(resources)
        lines = result.strip().split("\n")
        assert len(lines) == 3
        for i, line in enumerate(lines, 1):
            assert f'"id":"{i}"' in line


class TestSystemExport:
    """Tests for system-level $export."""

    def test_export_without_prefer_header(self, client):
        """Test export without required Prefer header returns 400."""
        response = client.get("/$export")
        assert response.status_code == 400
        outcome = response.json()
        assert "Prefer" in outcome["issue"][0]["diagnostics"]

    def test_export_starts_job(self, client):
        """Test export with correct headers starts a job."""
        response = client.get(
            "/$export",
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 202
        assert "Content-Location" in response.headers
        assert "/bulk-status/" in response.headers["Content-Location"]

    def test_export_with_type_filter(self, client):
        """Test export with _type filter."""
        response = client.get(
            "/$export",
            params={"_type": "Patient,Observation"},
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 202


class TestPatientExport:
    """Tests for patient-level $export."""

    def test_patient_export_starts_job(self, client):
        """Test Patient $export starts a job."""
        response = client.get(
            "/Patient/$export",
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 202
        assert "Content-Location" in response.headers


class TestGroupExport:
    """Tests for group-level $export."""

    def test_group_export_group_not_found(self, client):
        """Test Group $export with non-existent group returns 404."""
        response = client.get(
            "/Group/nonexistent/$export",
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 404

    def test_group_export_empty_group(self, client):
        """Test Group $export with empty group returns 422."""
        # Create an empty group
        group_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "member": [],
            },
        )
        group_id = group_response.json()["id"]

        response = client.get(
            f"/Group/{group_id}/$export",
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 422
        assert "no Patient members" in response.json()["issue"][0]["diagnostics"]

    def test_group_export_with_patients(self, client):
        """Test Group $export with patients starts job."""
        # Create patients
        patient_ids = []
        for i in range(2):
            r = client.post(
                "/Patient",
                json={"resourceType": "Patient", "name": [{"family": f"Export{i}"}]},
            )
            patient_ids.append(r.json()["id"])

        # Create group with patients
        group_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "member": [{"entity": {"reference": f"Patient/{pid}"}} for pid in patient_ids],
            },
        )
        group_id = group_response.json()["id"]

        response = client.get(
            f"/Group/{group_id}/$export",
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        assert response.status_code == 202


class TestExportStatus:
    """Tests for bulk-status endpoint."""

    def test_status_job_not_found(self, client):
        """Test status for non-existent job returns 404."""
        response = client.get("/bulk-status/nonexistent")
        assert response.status_code == 404

    def test_status_returns_manifest_when_complete(self, client):
        """Test status returns manifest when job completes."""
        # Create some data
        client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "StatusTest"}]},
        )

        # Start export
        export_response = client.get(
            "/$export",
            params={"_type": "Patient"},
            headers={
                "Accept": "application/fhir+ndjson",
                "Prefer": "respond-async",
            },
        )
        status_url = export_response.headers["Content-Location"]
        job_id = status_url.split("/bulk-status/")[1]

        # Poll for completion (with timeout)
        max_attempts = 20
        for _ in range(max_attempts):
            status_response = client.get(f"/bulk-status/{job_id}")
            if status_response.status_code == 200:
                break
            time.sleep(0.1)

        assert status_response.status_code == 200
        manifest = status_response.json()
        assert "transactionTime" in manifest
        assert "output" in manifest
        assert manifest["requiresAccessToken"] is False


class TestExportOutput:
    """Tests for bulk-output endpoint."""

    def test_output_job_not_found(self, client):
        """Test output for non-existent job returns 404."""
        response = client.get("/bulk-output/nonexistent/Patient.ndjson")
        assert response.status_code == 404

    def test_output_invalid_filename(self, client):
        """Test output with invalid filename returns 400."""
        # Start and wait for export
        client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "OutputTest"}]},
        )
        export_response = client.get(
            "/$export",
            params={"_type": "Patient"},
            headers={"Prefer": "respond-async"},
        )
        job_id = export_response.headers["Content-Location"].split("/bulk-status/")[1]

        # Wait for completion
        for _ in range(20):
            if client.get(f"/bulk-status/{job_id}").status_code == 200:
                break
            time.sleep(0.1)

        # Try invalid filename
        response = client.get(f"/bulk-output/{job_id}/invalid.txt")
        assert response.status_code == 400

    def test_output_returns_ndjson(self, client):
        """Test output returns valid NDJSON."""
        # Create patient
        client.post(
            "/Patient",
            json={"resourceType": "Patient", "name": [{"family": "NDJSONTest"}]},
        )

        # Start export
        export_response = client.get(
            "/$export",
            params={"_type": "Patient"},
            headers={"Prefer": "respond-async"},
        )
        job_id = export_response.headers["Content-Location"].split("/bulk-status/")[1]

        # Wait for completion
        for _ in range(20):
            status_response = client.get(f"/bulk-status/{job_id}")
            if status_response.status_code == 200:
                break
            time.sleep(0.1)

        # Get output
        output_response = client.get(f"/bulk-output/{job_id}/Patient.ndjson")
        assert output_response.status_code == 200
        assert output_response.headers["content-type"] == "application/fhir+ndjson"

        # Verify NDJSON format - each line should be valid JSON
        import json

        content = output_response.text
        lines = [line for line in content.strip().split("\n") if line]
        assert len(lines) >= 1
        for line in lines:
            resource = json.loads(line)
            assert resource["resourceType"] == "Patient"


class TestDeleteExport:
    """Tests for bulk-status DELETE endpoint."""

    def test_delete_job_not_found(self, client):
        """Test deleting non-existent job returns 404."""
        response = client.delete("/bulk-status/nonexistent")
        assert response.status_code == 404

    def test_delete_job_success(self, client):
        """Test deleting existing job returns 204."""
        # Start export
        export_response = client.get(
            "/$export",
            params={"_type": "Patient"},
            headers={"Prefer": "respond-async"},
        )
        job_id = export_response.headers["Content-Location"].split("/bulk-status/")[1]

        # Delete it
        delete_response = client.delete(f"/bulk-status/{job_id}")
        assert delete_response.status_code == 204

        # Verify it's gone
        status_response = client.get(f"/bulk-status/{job_id}")
        assert status_response.status_code == 404


class TestSinceFilter:
    """Tests for _since parameter."""

    def test_invalid_since_format(self, client):
        """Test invalid _since format returns 400."""
        response = client.get(
            "/$export",
            params={"_since": "invalid-date"},
            headers={"Prefer": "respond-async"},
        )
        assert response.status_code == 400
        assert "_since" in response.json()["issue"][0]["diagnostics"]

    def test_valid_since_format(self, client):
        """Test valid _since format is accepted."""
        response = client.get(
            "/$export",
            params={"_since": "2024-01-01T00:00:00Z"},
            headers={"Prefer": "respond-async"},
        )
        assert response.status_code == 202
