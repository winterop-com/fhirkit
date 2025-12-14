"""Tests for $evaluate-measure operation."""

import base64

import pytest
from fastapi.testclient import TestClient

from fhir_cql.server.api.app import create_app
from fhir_cql.server.storage.fhir_store import FHIRStore


# Simple CQL for testing
SIMPLE_CQL = """library TestMeasure version '1.0.0'

using FHIR version '4.0.1'

context Patient

define "Initial Population":
    exists([Condition] C
        where C.clinicalStatus ~ 'active')

define "Denominator":
    "Initial Population"

define "Denominator Exclusions":
    false

define "Numerator":
    exists([Observation] O
        where O.status = 'final')
"""


@pytest.fixture
def store():
    """Create a fresh FHIR store for testing."""
    return FHIRStore()


@pytest.fixture
def client(store):
    """Create a test client with the FHIR app."""
    app = create_app(store=store)
    return TestClient(app)


@pytest.fixture
def populated_store(store, client):
    """Populate store with test data for measure evaluation."""
    # Create Library with CQL
    library = {
        "resourceType": "Library",
        "id": "library-test",
        "url": "http://example.org/fhir/Library/TestMeasure",
        "name": "TestMeasure",
        "status": "active",
        "type": {
            "coding": [{"code": "logic-library"}]
        },
        "content": [{
            "contentType": "text/cql",
            "data": base64.b64encode(SIMPLE_CQL.encode("utf-8")).decode("utf-8"),
        }],
    }
    client.put("/Library/library-test", json=library)

    # Create Measure referencing the Library
    measure = {
        "resourceType": "Measure",
        "id": "measure-test",
        "url": "http://example.org/fhir/Measure/TestMeasure",
        "name": "TestMeasure",
        "status": "active",
        "library": ["http://example.org/fhir/Library/TestMeasure"],
        "scoring": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/measure-scoring",
                "code": "proportion",
            }]
        },
        "effectivePeriod": {
            "start": "2024-01-01",
            "end": "2024-12-31",
        },
        "improvementNotation": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation",
                "code": "increase",
            }]
        },
        "group": [{
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
        }],
    }
    client.put("/Measure/measure-test", json=measure)

    # Create patients
    patient1 = {
        "resourceType": "Patient",
        "id": "patient-1",
        "name": [{"family": "Smith", "given": ["John"]}],
        "active": True,
    }
    patient2 = {
        "resourceType": "Patient",
        "id": "patient-2",
        "name": [{"family": "Jones", "given": ["Jane"]}],
        "active": True,
    }
    client.put("/Patient/patient-1", json=patient1)
    client.put("/Patient/patient-2", json=patient2)

    # Create condition for patient-1 (puts them in initial population)
    condition = {
        "resourceType": "Condition",
        "id": "condition-1",
        "subject": {"reference": "Patient/patient-1"},
        "clinicalStatus": {
            "coding": [{"code": "active"}]
        },
        "code": {
            "coding": [{"code": "test"}]
        },
    }
    client.put("/Condition/condition-1", json=condition)

    # Create observation for patient-1 (puts them in numerator)
    observation = {
        "resourceType": "Observation",
        "id": "obs-1",
        "status": "final",
        "subject": {"reference": "Patient/patient-1"},
        "code": {
            "coding": [{"code": "test"}]
        },
    }
    client.put("/Observation/obs-1", json=observation)

    return store


class TestEvaluateMeasure:
    """Tests for $evaluate-measure operation."""

    def test_evaluate_measure_population(self, client, populated_store):
        """Test population-level measure evaluation."""
        response = client.get("/Measure/measure-test/$evaluate-measure")
        assert response.status_code == 200

        report = response.json()
        assert report["resourceType"] == "MeasureReport"
        assert report["type"] == "summary"
        assert report["status"] == "complete"
        assert "group" in report

    def test_evaluate_measure_individual(self, client, populated_store):
        """Test individual patient measure evaluation."""
        response = client.get(
            "/Measure/measure-test/$evaluate-measure?subject=Patient/patient-1&reportType=individual"
        )
        assert response.status_code == 200

        report = response.json()
        assert report["resourceType"] == "MeasureReport"
        assert report["type"] == "individual"
        assert report["subject"]["reference"] == "Patient/patient-1"

    def test_evaluate_measure_with_period(self, client, populated_store):
        """Test measure evaluation with custom period."""
        response = client.get(
            "/Measure/measure-test/$evaluate-measure?periodStart=2024-01-01&periodEnd=2024-06-30"
        )
        assert response.status_code == 200

        report = response.json()
        assert report["period"]["start"] == "2024-01-01"
        assert report["period"]["end"] == "2024-06-30"

    def test_evaluate_measure_not_found(self, client, populated_store):
        """Test evaluation with non-existent measure."""
        response = client.get("/Measure/nonexistent/$evaluate-measure")
        assert response.status_code == 404

    def test_evaluate_measure_no_library(self, client, populated_store):
        """Test evaluation when measure has no library."""
        # Create measure without library reference
        measure = {
            "resourceType": "Measure",
            "id": "measure-no-lib",
            "url": "http://example.org/fhir/Measure/NoLibrary",
            "name": "NoLibrary",
            "status": "active",
        }
        client.put("/Measure/measure-no-lib", json=measure)

        response = client.get("/Measure/measure-no-lib/$evaluate-measure")
        assert response.status_code == 400
        assert "no associated Library" in response.json()["issue"][0]["diagnostics"]

    def test_evaluate_measure_library_not_found(self, client, populated_store):
        """Test evaluation when library doesn't exist."""
        # Create measure with missing library reference
        measure = {
            "resourceType": "Measure",
            "id": "measure-missing-lib",
            "url": "http://example.org/fhir/Measure/MissingLib",
            "name": "MissingLib",
            "status": "active",
            "library": ["http://example.org/fhir/Library/DoesNotExist"],
        }
        client.put("/Measure/measure-missing-lib", json=measure)

        response = client.get("/Measure/measure-missing-lib/$evaluate-measure")
        assert response.status_code == 400
        assert "Library not found" in response.json()["issue"][0]["diagnostics"]

    def test_evaluate_measure_no_patients(self, client, store):
        """Test evaluation when no patients exist."""
        # Create app with empty store
        app = create_app(store=store)
        empty_client = TestClient(app)

        # Add library and measure but no patients
        library = {
            "resourceType": "Library",
            "id": "library-empty",
            "url": "http://example.org/fhir/Library/Empty",
            "status": "active",
            "content": [{
                "contentType": "text/cql",
                "data": base64.b64encode(SIMPLE_CQL.encode("utf-8")).decode("utf-8"),
            }],
        }
        empty_client.put("/Library/library-empty", json=library)

        measure = {
            "resourceType": "Measure",
            "id": "measure-empty",
            "library": ["http://example.org/fhir/Library/Empty"],
            "status": "active",
        }
        empty_client.put("/Measure/measure-empty", json=measure)

        response = empty_client.get("/Measure/measure-empty/$evaluate-measure")
        assert response.status_code == 400
        assert "No patients found" in response.json()["issue"][0]["diagnostics"]

    def test_evaluate_measure_has_improvement_notation(self, client, populated_store):
        """Test that improvement notation is included in report."""
        response = client.get("/Measure/measure-test/$evaluate-measure")
        assert response.status_code == 200

        report = response.json()
        assert "improvementNotation" in report

    def test_evaluate_measure_has_measure_reference(self, client, populated_store):
        """Test that measure reference is included in report."""
        response = client.get("/Measure/measure-test/$evaluate-measure")
        assert response.status_code == 200

        report = response.json()
        assert report["measure"] == "http://example.org/fhir/Measure/TestMeasure"

    def test_evaluate_measure_post(self, client, populated_store):
        """Test POST method for measure evaluation."""
        response = client.post("/Measure/measure-test/$evaluate-measure")
        assert response.status_code == 200

        report = response.json()
        assert report["resourceType"] == "MeasureReport"


class TestCapabilityStatement:
    """Test that CapabilityStatement includes evaluate-measure."""

    def test_capability_includes_evaluate_measure(self, client, populated_store):
        """Test CapabilityStatement includes $evaluate-measure operation."""
        response = client.get("/metadata")
        assert response.status_code == 200

        capability = response.json()
        resources = capability["rest"][0]["resource"]

        measure_resource = next(
            (r for r in resources if r["type"] == "Measure"), None
        )
        assert measure_resource is not None
        assert "operation" in measure_resource

        operations = measure_resource["operation"]
        op_names = [op["name"] for op in operations]
        assert "evaluate-measure" in op_names
