"""Tests for Group + $evaluate-measure functionality."""

import base64

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings


@pytest.fixture
def client():
    """Create a test client."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings)
    return TestClient(app)


# Sample CQL for a simple cohort measure
SAMPLE_CQL = """
library TestMeasure version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "Initial Population":
    AgeInYears() >= 18

define "Denominator":
    "Initial Population"

define "Numerator":
    "Initial Population"
"""


class TestGroupResource:
    """Basic Group resource CRUD tests."""

    def test_create_group(self, client):
        """Test creating a Group resource."""
        response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Test Patient Group",
            },
        )
        assert response.status_code == 201
        group = response.json()
        assert group["resourceType"] == "Group"
        assert "id" in group

    def test_read_group(self, client):
        """Test reading a Group resource."""
        # Create a group
        create_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Read Test Group",
            },
        )
        group_id = create_response.json()["id"]

        # Read it
        read_response = client.get(f"/Group/{group_id}")
        assert read_response.status_code == 200
        group = read_response.json()
        assert group["name"] == "Read Test Group"

    def test_update_group(self, client):
        """Test updating a Group resource."""
        # Create a group
        create_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Original Name",
            },
        )
        group = create_response.json()
        group_id = group["id"]

        # Update it
        group["name"] = "Updated Name"
        update_response = client.put(f"/Group/{group_id}", json=group)
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "Updated Name"

    def test_delete_group(self, client):
        """Test deleting a Group resource."""
        # Create a group
        create_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "To Delete",
            },
        )
        group_id = create_response.json()["id"]

        # Delete it
        delete_response = client.delete(f"/Group/{group_id}")
        assert delete_response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/Group/{group_id}")
        assert get_response.status_code == 404


class TestGroupMeasureEvaluation:
    """Tests for Group-based measure evaluation."""

    def _create_test_setup(self, client):
        """Create the test Measure, Library, and Patients."""
        # Create Library with CQL
        library_response = client.post(
            "/Library",
            json={
                "resourceType": "Library",
                "url": "http://example.org/Library/TestMeasure",
                "name": "TestMeasure",
                "status": "active",
                "type": {"coding": [{"code": "logic-library"}]},
                "content": [
                    {
                        "contentType": "text/cql",
                        "data": base64.b64encode(SAMPLE_CQL.encode()).decode(),
                    }
                ],
            },
        )
        assert library_response.status_code == 201

        # Create Measure
        measure_response = client.post(
            "/Measure",
            json={
                "resourceType": "Measure",
                "url": "http://example.org/Measure/TestMeasure",
                "name": "TestMeasure",
                "status": "active",
                "library": ["http://example.org/Library/TestMeasure"],
                "scoring": {"coding": [{"code": "proportion"}]},
                "group": [
                    {
                        "population": [
                            {
                                "code": {"coding": [{"code": "initial-population"}]},
                                "criteria": {"expression": "Initial Population"},
                            },
                            {
                                "code": {"coding": [{"code": "denominator"}]},
                                "criteria": {"expression": "Denominator"},
                            },
                            {
                                "code": {"coding": [{"code": "numerator"}]},
                                "criteria": {"expression": "Numerator"},
                            },
                        ]
                    }
                ],
            },
        )
        assert measure_response.status_code == 201
        measure_id = measure_response.json()["id"]

        # Create test patients
        patient_ids = []
        for i in range(3):
            patient_response = client.post(
                "/Patient",
                json={
                    "resourceType": "Patient",
                    "name": [{"family": f"GroupPatient{i}"}],
                    "birthDate": "1980-01-01",  # Adult for measure criteria
                },
            )
            assert patient_response.status_code == 201
            patient_ids.append(patient_response.json()["id"])

        return measure_id, patient_ids

    def test_evaluate_measure_with_group(self, client):
        """Test measure evaluation with a Group subject."""
        measure_id, patient_ids = self._create_test_setup(client)

        # Create a Group with the patients as members
        group_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Test Measure Group",
                "member": [{"entity": {"reference": f"Patient/{pid}"}} for pid in patient_ids],
            },
        )
        assert group_response.status_code == 201
        group_id = group_response.json()["id"]

        # Evaluate measure with Group subject
        eval_response = client.get(
            f"/Measure/{measure_id}/$evaluate-measure",
            params={
                "subject": f"Group/{group_id}",
                "periodStart": "2024-01-01",
                "periodEnd": "2024-12-31",
            },
        )

        assert eval_response.status_code == 200
        report = eval_response.json()
        assert report["resourceType"] == "MeasureReport"

    def test_evaluate_measure_group_not_found(self, client):
        """Test measure evaluation with non-existent Group returns 404."""
        measure_id, _ = self._create_test_setup(client)

        eval_response = client.get(
            f"/Measure/{measure_id}/$evaluate-measure",
            params={
                "subject": "Group/nonexistent",
                "periodStart": "2024-01-01",
                "periodEnd": "2024-12-31",
            },
        )

        assert eval_response.status_code == 404
        outcome = eval_response.json()
        assert outcome["resourceType"] == "OperationOutcome"

    def test_evaluate_measure_empty_group(self, client):
        """Test measure evaluation with Group having no Patient members."""
        measure_id, _ = self._create_test_setup(client)

        # Create a Group with no members
        group_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Empty Group",
                "member": [],
            },
        )
        group_id = group_response.json()["id"]

        # Evaluate measure
        eval_response = client.get(
            f"/Measure/{measure_id}/$evaluate-measure",
            params={
                "subject": f"Group/{group_id}",
                "periodStart": "2024-01-01",
                "periodEnd": "2024-12-31",
            },
        )

        # Should return 422 as no patients to evaluate
        assert eval_response.status_code == 422
        outcome = eval_response.json()
        assert "no Patient members" in outcome["issue"][0]["diagnostics"]

    def test_evaluate_measure_group_with_non_patient_members(self, client):
        """Test measure evaluation with Group containing non-Patient members."""
        measure_id, patient_ids = self._create_test_setup(client)

        # Create a Group with mixed members (Practitioner won't be evaluated)
        # First create a practitioner
        prac_response = client.post(
            "/Practitioner",
            json={
                "resourceType": "Practitioner",
                "name": [{"family": "TestPractitioner"}],
            },
        )
        prac_id = prac_response.json()["id"]

        group_response = client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Mixed Group",
                "member": [
                    {"entity": {"reference": f"Patient/{patient_ids[0]}"}},
                    {"entity": {"reference": f"Practitioner/{prac_id}"}},  # Should be ignored
                ],
            },
        )
        group_id = group_response.json()["id"]

        # Evaluate measure - should work but only evaluate the patient
        eval_response = client.get(
            f"/Measure/{measure_id}/$evaluate-measure",
            params={
                "subject": f"Group/{group_id}",
                "periodStart": "2024-01-01",
                "periodEnd": "2024-12-31",
            },
        )

        assert eval_response.status_code == 200
        report = eval_response.json()
        assert report["resourceType"] == "MeasureReport"

    def test_evaluate_measure_single_patient(self, client):
        """Test that single patient evaluation still works."""
        measure_id, patient_ids = self._create_test_setup(client)

        # Evaluate for single patient
        eval_response = client.get(
            f"/Measure/{measure_id}/$evaluate-measure",
            params={
                "subject": f"Patient/{patient_ids[0]}",
                "periodStart": "2024-01-01",
                "periodEnd": "2024-12-31",
                "reportType": "individual",
            },
        )

        assert eval_response.status_code == 200
        report = eval_response.json()
        assert report["resourceType"] == "MeasureReport"
        assert report.get("type") == "individual"

    def test_search_group_resources(self, client):
        """Test searching for Group resources."""
        # Create a couple of groups
        client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "person",
                "actual": True,
                "name": "Search Test Group A",
            },
        )
        client.post(
            "/Group",
            json={
                "resourceType": "Group",
                "type": "device",
                "actual": True,
                "name": "Search Test Group B",
            },
        )

        # Search for all groups
        search_response = client.get("/Group")
        assert search_response.status_code == 200
        bundle = search_response.json()
        assert bundle["resourceType"] == "Bundle"
        assert bundle["total"] >= 2
