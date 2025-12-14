"""Tests for _elements and _summary search parameters."""

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
    """Populate store with test data."""
    # Create patient with all fields
    patient = {
        "resourceType": "Patient",
        "id": "patient-1",
        "identifier": [{"system": "http://example.org", "value": "12345"}],
        "active": True,
        "name": [{"family": "Smith", "given": ["John"]}],
        "telecom": [{"system": "phone", "value": "555-1234"}],
        "gender": "male",
        "birthDate": "1980-01-01",
        "address": [{"city": "Boston", "state": "MA"}],
        "text": {
            "status": "generated",
            "div": "<div>John Smith</div>",
        },
    }
    client.put("/Patient/patient-1", json=patient)

    # Create patient 2
    patient2 = {
        "resourceType": "Patient",
        "id": "patient-2",
        "identifier": [{"system": "http://example.org", "value": "67890"}],
        "active": True,
        "name": [{"family": "Jones", "given": ["Jane"]}],
        "gender": "female",
        "birthDate": "1990-05-15",
    }
    client.put("/Patient/patient-2", json=patient2)

    # Create condition
    condition = {
        "resourceType": "Condition",
        "id": "condition-1",
        "identifier": [{"value": "cond-123"}],
        "clinicalStatus": {"coding": [{"code": "active"}]},
        "verificationStatus": {"coding": [{"code": "confirmed"}]},
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": "73211009", "display": "Diabetes"}]},
        "subject": {"reference": "Patient/patient-1"},
        "onsetDateTime": "2020-01-15",
        "text": {
            "status": "generated",
            "div": "<div>Diabetes condition</div>",
        },
    }
    client.put("/Condition/condition-1", json=condition)

    # Create observation
    observation = {
        "resourceType": "Observation",
        "id": "obs-1",
        "identifier": [{"value": "obs-123"}],
        "status": "final",
        "category": [{"coding": [{"code": "laboratory"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "HbA1c"}]},
        "subject": {"reference": "Patient/patient-1"},
        "effectiveDateTime": "2024-01-15",
        "valueQuantity": {"value": 7.2, "unit": "%"},
    }
    client.put("/Observation/obs-1", json=observation)

    return store


class TestElementsSearch:
    """Tests for _elements parameter."""

    def test_elements_single_field(self, client, populated_store):
        """Test _elements with a single field."""
        response = client.get("/Patient?_elements=name")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["resourceType"] == "Bundle"
        assert bundle["total"] == 2

        # Check that only requested fields are present
        for entry in bundle["entry"]:
            resource = entry["resource"]
            assert resource["resourceType"] == "Patient"
            assert "id" in resource  # Always included
            assert "name" in resource
            # Other fields should not be present
            assert "gender" not in resource
            assert "birthDate" not in resource
            assert "address" not in resource

    def test_elements_multiple_fields(self, client, populated_store):
        """Test _elements with multiple fields."""
        response = client.get("/Patient?_elements=name,birthDate,gender")
        assert response.status_code == 200

        bundle = response.json()
        for entry in bundle["entry"]:
            resource = entry["resource"]
            assert "name" in resource
            assert "birthDate" in resource
            assert "gender" in resource
            # Other fields should not be present
            assert "address" not in resource
            assert "telecom" not in resource

    def test_elements_with_spaces(self, client, populated_store):
        """Test _elements with spaces around field names."""
        response = client.get("/Patient?_elements=name, birthDate , gender")
        assert response.status_code == 200

        bundle = response.json()
        for entry in bundle["entry"]:
            resource = entry["resource"]
            assert "name" in resource
            assert "birthDate" in resource
            assert "gender" in resource

    def test_elements_preserves_mandatory_fields(self, client, populated_store):
        """Test that resourceType, id, and meta are always included."""
        response = client.get("/Patient?_elements=name")
        assert response.status_code == 200

        bundle = response.json()
        for entry in bundle["entry"]:
            resource = entry["resource"]
            assert resource["resourceType"] == "Patient"
            assert "id" in resource

    def test_elements_on_condition(self, client, populated_store):
        """Test _elements on Condition resource."""
        response = client.get("/Condition?_elements=code,subject")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 1

        resource = bundle["entry"][0]["resource"]
        assert "code" in resource
        assert "subject" in resource
        assert "clinicalStatus" not in resource
        assert "onsetDateTime" not in resource


class TestSummarySearch:
    """Tests for _summary parameter."""

    def test_summary_true(self, client, populated_store):
        """Test _summary=true returns summary elements only."""
        response = client.get("/Patient?_summary=true")
        assert response.status_code == 200

        bundle = response.json()
        for entry in bundle["entry"]:
            resource = entry["resource"]
            assert resource["resourceType"] == "Patient"
            # Summary elements should be present (if they exist in the resource)
            # Text should not be present in summary
            assert "text" not in resource

    def test_summary_text(self, client, populated_store):
        """Test _summary=text returns only text narrative."""
        response = client.get("/Patient/patient-1?_summary=text")
        # Note: read endpoint doesn't support _summary, using search
        response = client.get("/Patient?_id=patient-1&_summary=text")
        assert response.status_code == 200

        bundle = response.json()
        resource = bundle["entry"][0]["resource"]
        # Should have resourceType, id, meta, and text only
        assert resource["resourceType"] == "Patient"
        assert "id" in resource
        # Text should be present if it exists
        if "text" in resource:
            assert "div" in resource["text"]
        # Other fields should not be present
        assert "name" not in resource
        assert "gender" not in resource

    def test_summary_data(self, client, populated_store):
        """Test _summary=data removes text element."""
        response = client.get("/Patient?_id=patient-1&_summary=data")
        assert response.status_code == 200

        bundle = response.json()
        resource = bundle["entry"][0]["resource"]
        # Text should not be present
        assert "text" not in resource
        # Other data should be present
        assert "name" in resource
        assert "gender" in resource

    def test_summary_count(self, client, populated_store):
        """Test _summary=count returns count only."""
        response = client.get("/Patient?_summary=count")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "searchset"
        assert bundle["total"] == 2
        # No entries should be present
        assert "entry" not in bundle

    def test_summary_false(self, client, populated_store):
        """Test _summary=false returns full resources."""
        response = client.get("/Patient?_id=patient-1&_summary=false")
        assert response.status_code == 200

        bundle = response.json()
        resource = bundle["entry"][0]["resource"]
        # All fields should be present
        assert "name" in resource
        assert "gender" in resource
        assert "birthDate" in resource

    def test_summary_on_condition(self, client, populated_store):
        """Test _summary=true on Condition resource."""
        response = client.get("/Condition?_summary=true")
        assert response.status_code == 200

        bundle = response.json()
        resource = bundle["entry"][0]["resource"]
        # Summary should include clinical status, code, subject
        assert resource["resourceType"] == "Condition"
        # Text should not be in summary
        assert "text" not in resource


class TestElementsWithPagination:
    """Tests for _elements combined with pagination."""

    def test_elements_with_count(self, client, populated_store):
        """Test _elements works with _count."""
        response = client.get("/Patient?_elements=name&_count=1")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 2
        assert len(bundle["entry"]) == 1

        resource = bundle["entry"][0]["resource"]
        assert "name" in resource
        assert "gender" not in resource


class TestSummaryWithPagination:
    """Tests for _summary combined with pagination."""

    def test_summary_count_ignores_pagination(self, client, populated_store):
        """Test _summary=count returns total count regardless of _count."""
        response = client.get("/Patient?_summary=count&_count=1")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 2  # Total, not paginated


class TestElementsOnCompartmentSearch:
    """Tests for _elements on compartment search."""

    def test_elements_compartment_search(self, client, populated_store):
        """Test _elements on Patient compartment search."""
        response = client.get("/Patient/patient-1/Condition?_elements=code")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 1

        resource = bundle["entry"][0]["resource"]
        assert "code" in resource
        assert "clinicalStatus" not in resource

    def test_summary_count_compartment(self, client, populated_store):
        """Test _summary=count on compartment search."""
        response = client.get("/Patient/patient-1/Observation?_summary=count")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] == 1
        assert "entry" not in bundle


class TestElementsOnPatientEverything:
    """Tests for _elements on $everything operation."""

    def test_elements_patient_everything(self, client, populated_store):
        """Test _elements on Patient/$everything."""
        response = client.get("/Patient/patient-1/$everything?_elements=name,code")
        assert response.status_code == 200

        bundle = response.json()
        # Patient should have name but not other fields
        patient_entry = bundle["entry"][0]
        patient = patient_entry["resource"]
        assert patient["resourceType"] == "Patient"
        assert "name" in patient
        assert "gender" not in patient

    def test_summary_count_patient_everything(self, client, populated_store):
        """Test _summary=count on Patient/$everything."""
        response = client.get("/Patient/patient-1/$everything?_summary=count")
        assert response.status_code == 200

        bundle = response.json()
        assert bundle["total"] >= 1  # At least the patient
        assert "entry" not in bundle


class TestElementsWithInclude:
    """Tests for _elements with _include."""

    def test_elements_with_include(self, client, populated_store):
        """Test _elements applies to included resources."""
        response = client.get("/Condition?_include=Condition:subject&_elements=code,name")
        assert response.status_code == 200

        bundle = response.json()
        # Both main and included resources should be filtered
        for entry in bundle["entry"]:
            resource = entry["resource"]
            if resource["resourceType"] == "Condition":
                assert "code" in resource
                assert "clinicalStatus" not in resource
            elif resource["resourceType"] == "Patient":
                assert "name" in resource
                assert "gender" not in resource
