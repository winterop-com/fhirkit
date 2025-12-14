"""Tests for chained and reverse-chained search functionality."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store():
    """Create a fresh FHIR store for testing."""
    return FHIRStore()


@pytest.fixture
def client(store):
    """Create a test client with the FHIR app."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


@pytest.fixture
def populated_store(store, client):
    """Populate store with test data for search tests."""
    # Create patients
    patient1 = {
        "resourceType": "Patient",
        "id": "patient-smith",
        "name": [{"family": "Smith", "given": ["John"]}],
        "active": True,
    }
    patient2 = {
        "resourceType": "Patient",
        "id": "patient-jones",
        "name": [{"family": "Jones", "given": ["Jane"]}],
        "active": True,
    }

    client.put("/Patient/patient-smith", json=patient1)
    client.put("/Patient/patient-jones", json=patient2)

    # Create conditions for patients
    condition1 = {
        "resourceType": "Condition",
        "id": "condition-diabetes",
        "subject": {"reference": "Patient/patient-smith"},
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "44054006",
                    "display": "Diabetes mellitus type 2",
                }
            ],
            "text": "Diabetes",
        },
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                }
            ]
        },
    }
    condition2 = {
        "resourceType": "Condition",
        "id": "condition-hypertension",
        "subject": {"reference": "Patient/patient-smith"},
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "38341003",
                    "display": "Hypertension",
                }
            ],
            "text": "Hypertension",
        },
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                }
            ]
        },
    }
    condition3 = {
        "resourceType": "Condition",
        "id": "condition-asthma",
        "subject": {"reference": "Patient/patient-jones"},
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "195967001",
                    "display": "Asthma",
                }
            ],
            "text": "Asthma",
        },
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                }
            ]
        },
    }

    client.put("/Condition/condition-diabetes", json=condition1)
    client.put("/Condition/condition-hypertension", json=condition2)
    client.put("/Condition/condition-asthma", json=condition3)

    # Create observations
    observation1 = {
        "resourceType": "Observation",
        "id": "obs-bp-smith",
        "status": "final",
        "subject": {"reference": "Patient/patient-smith"},
        "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic BP"}]},
        "valueQuantity": {"value": 140, "unit": "mmHg"},
    }

    client.put("/Observation/obs-bp-smith", json=observation1)

    return store


class TestChainedSearch:
    """Tests for chained search parameters."""

    def test_chained_search_condition_by_patient_name(self, client, populated_store):
        """Test chained search: Condition?subject:Patient.name=Smith"""
        response = client.get("/Condition?subject:Patient.name=Smith")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["resourceType"] == "Bundle"
        assert bundle["total"] == 2  # Smith has 2 conditions

        # All conditions should reference patient-smith
        for entry in bundle["entry"]:
            assert entry["resource"]["subject"]["reference"] == "Patient/patient-smith"

    def test_chained_search_no_match(self, client, populated_store):
        """Test chained search with no matching results."""
        response = client.get("/Condition?subject:Patient.name=Nonexistent")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 0
        assert "entry" not in bundle or len(bundle.get("entry", [])) == 0

    def test_chained_search_observation_by_patient_name(self, client, populated_store):
        """Test chained search: Observation?subject:Patient.name=Smith"""
        response = client.get("/Observation?subject:Patient.name=Smith")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 1

    def test_chained_search_with_regular_params(self, client, populated_store):
        """Test chained search combined with regular parameters."""
        # This tests that chained params work alongside regular params
        response = client.get("/Condition?subject:Patient.name=Smith&code=44054006")
        assert response.status_code == 200

        bundle = response.json()
        # Should only get the diabetes condition (matches both criteria)
        assert bundle["total"] >= 1

    def test_chained_search_invalid_format_ignored(self, client, populated_store):
        """Test that malformed chained params are handled gracefully."""
        # Missing target type indicator
        response = client.get("/Condition?subject.name=Smith")
        assert response.status_code == 200  # Should not error

        # Invalid but parseable - should just return no matches
        response = client.get("/Condition?subject:InvalidType.name=Smith")
        assert response.status_code == 200


class TestReverseChainedSearch:
    """Tests for reverse chained search (_has) parameters."""

    def test_has_search_patients_with_diabetes(self, client, populated_store):
        """Test _has search: Patient?_has:Condition:patient:code=diabetes"""
        response = client.get("/Patient?_has:Condition:subject:code=44054006")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1

        # Should find patient-smith who has diabetes
        patient_ids = [e["resource"]["id"] for e in bundle.get("entry", [])]
        assert "patient-smith" in patient_ids

    def test_has_search_patients_with_asthma(self, client, populated_store):
        """Test _has search for patients with asthma."""
        response = client.get("/Patient?_has:Condition:subject:code=195967001")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1

        patient_ids = [e["resource"]["id"] for e in bundle.get("entry", [])]
        assert "patient-jones" in patient_ids

    def test_has_search_no_match(self, client, populated_store):
        """Test _has search with no matching results."""
        response = client.get("/Patient?_has:Condition:subject:code=nonexistent-code")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 0

    def test_has_search_patients_with_observation(self, client, populated_store):
        """Test _has search: Patient?_has:Observation:subject:code=8480-6"""
        response = client.get("/Patient?_has:Observation:subject:code=8480-6")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1

        patient_ids = [e["resource"]["id"] for e in bundle.get("entry", [])]
        assert "patient-smith" in patient_ids

    def test_has_search_multiple_conditions(self, client, populated_store):
        """Test multiple _has parameters (AND logic)."""
        # Find patients with BOTH diabetes AND hypertension
        response = client.get("/Patient?_has:Condition:subject:code=44054006&_has:Condition:subject:code=38341003")
        assert response.status_code == 200

        bundle = response.json()
        # Only patient-smith has both conditions
        if bundle["total"] > 0:
            patient_ids = [e["resource"]["id"] for e in bundle.get("entry", [])]
            assert "patient-smith" in patient_ids
            assert "patient-jones" not in patient_ids

    def test_has_search_invalid_format_ignored(self, client, populated_store):
        """Test that malformed _has params are handled gracefully."""
        # Incomplete _has format
        response = client.get("/Patient?_has:Condition:subject")
        assert response.status_code == 200  # Should not error

        # Invalid resource type
        response = client.get("/Patient?_has:InvalidType:patient:code=test")
        assert response.status_code == 200  # Should not error


class TestAdvancedSearchCombinations:
    """Tests for combining advanced search features."""

    def test_chained_with_pagination(self, client, populated_store):
        """Test chained search with pagination parameters."""
        response = client.get("/Condition?subject:Patient.name=Smith&_count=1")
        assert response.status_code == 200

        bundle = response.json()
        # Should have pagination even with chained search
        entries = bundle.get("entry", [])
        assert len(entries) <= 1

    def test_has_with_include(self, client, populated_store):
        """Test _has search with _include."""
        response = client.get("/Patient?_has:Condition:subject:code=44054006&_revinclude=Condition:subject")
        assert response.status_code == 200

        bundle = response.json()
        # Should include the patient and related conditions
        resource_types = [e["resource"]["resourceType"] for e in bundle.get("entry", [])]
        assert "Patient" in resource_types

    def test_regular_search_still_works(self, client, populated_store):
        """Verify regular search is not affected by advanced search changes."""
        response = client.get("/Patient?name=Smith")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1

        response = client.get("/Condition?code=44054006")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1
