"""Tests for FHIR operations ($everything, _include, _revinclude, compartment search)."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store_with_related_data() -> FHIRStore:
    """Create store with patient and related resources."""
    store = FHIRStore()

    # Create patients
    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-1",
            "name": [{"family": "Smith", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1990-01-15",
        }
    )
    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-2",
            "name": [{"family": "Doe", "given": ["Jane"]}],
            "gender": "female",
            "birthDate": "1985-06-20",
        }
    )

    # Create practitioner
    store.create(
        {
            "resourceType": "Practitioner",
            "id": "practitioner-1",
            "name": [{"family": "Wilson", "given": ["Dr. Sarah"]}],
        }
    )

    # Create encounter for patient-1
    store.create(
        {
            "resourceType": "Encounter",
            "id": "encounter-1",
            "status": "finished",
            "class": {"code": "AMB"},
            "subject": {"reference": "Patient/patient-1"},
        }
    )

    # Create conditions for patient-1
    store.create(
        {
            "resourceType": "Condition",
            "id": "condition-1",
            "subject": {"reference": "Patient/patient-1"},
            "code": {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes mellitus type 2"}
                ]
            },
            "clinicalStatus": {"coding": [{"code": "active"}]},
        }
    )
    store.create(
        {
            "resourceType": "Condition",
            "id": "condition-2",
            "subject": {"reference": "Patient/patient-1"},
            "code": {
                "coding": [{"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertensive disorder"}]
            },
            "clinicalStatus": {"coding": [{"code": "active"}]},
        }
    )

    # Create condition for patient-2
    store.create(
        {
            "resourceType": "Condition",
            "id": "condition-3",
            "subject": {"reference": "Patient/patient-2"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "195967001", "display": "Asthma"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
        }
    )

    # Create observations for patient-1
    store.create(
        {
            "resourceType": "Observation",
            "id": "obs-1",
            "status": "final",
            "subject": {"reference": "Patient/patient-1"},
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 72, "unit": "beats/minute"},
        }
    )
    store.create(
        {
            "resourceType": "Observation",
            "id": "obs-2",
            "status": "final",
            "subject": {"reference": "Patient/patient-1"},
            "code": {
                "coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]
            },
            "valueQuantity": {"value": 120, "unit": "mmHg"},
        }
    )

    # Create medication request for patient-1
    store.create(
        {
            "resourceType": "MedicationRequest",
            "id": "medrx-1",
            "status": "active",
            "intent": "order",
            "subject": {"reference": "Patient/patient-1"},
            "medicationCodeableConcept": {
                "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975"}]
            },
        }
    )

    # Create procedure for patient-1
    store.create(
        {
            "resourceType": "Procedure",
            "id": "procedure-1",
            "status": "completed",
            "subject": {"reference": "Patient/patient-1"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "80146002", "display": "Appendectomy"}]},
        }
    )

    return store


@pytest.fixture
def client(store_with_related_data: FHIRStore) -> TestClient:
    """Create test client with pre-populated store."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store_with_related_data)
    return TestClient(app)


class TestPatientEverything:
    """Tests for Patient $everything operation."""

    def test_everything_returns_patient_and_related(self, client: TestClient) -> None:
        """Test $everything returns patient and all related resources."""
        response = client.get("/Patient/patient-1/$everything")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"

        # Count expected resources:
        # 1 Patient + 1 Encounter + 2 Conditions + 2 Observations + 1 MedicationRequest + 1 Procedure = 8
        assert data["total"] == 8

        # Check resource types in results
        types = [e["resource"]["resourceType"] for e in data["entry"]]
        assert "Patient" in types
        assert types.count("Condition") == 2
        assert types.count("Observation") == 2
        assert types.count("Encounter") == 1
        assert types.count("MedicationRequest") == 1
        assert types.count("Procedure") == 1

        # First entry should be the patient with mode="match"
        assert data["entry"][0]["resource"]["resourceType"] == "Patient"
        assert data["entry"][0]["search"]["mode"] == "match"

        # Other entries should have mode="include"
        for entry in data["entry"][1:]:
            assert entry["search"]["mode"] == "include"

    def test_everything_patient_not_found(self, client: TestClient) -> None:
        """Test $everything returns 404 for non-existent patient."""
        response = client.get("/Patient/nonexistent/$everything")
        assert response.status_code == 404

        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "not-found"

    def test_everything_pagination(self, client: TestClient) -> None:
        """Test $everything pagination."""
        response = client.get("/Patient/patient-1/$everything", params={"_count": 3})
        assert response.status_code == 200

        data = response.json()
        assert len(data["entry"]) == 3
        assert data["total"] == 8

        # Should have next link
        links = {link["relation"]: link["url"] for link in data["link"]}
        assert "next" in links
        assert "_offset=3" in links["next"]
        assert "_count=3" in links["next"]

    def test_everything_pagination_offset(self, client: TestClient) -> None:
        """Test $everything with offset."""
        response = client.get("/Patient/patient-1/$everything", params={"_count": 3, "_offset": 3})
        assert response.status_code == 200

        data = response.json()
        assert len(data["entry"]) == 3
        assert data["total"] == 8

        # Should have both previous and next links
        links = {link["relation"]: link["url"] for link in data["link"]}
        assert "previous" in links
        assert "next" in links

    def test_everything_empty_compartment(self, client: TestClient) -> None:
        """Test $everything for patient with no related resources."""
        # Create patient with no related resources
        response = client.post(
            "/Patient",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Empty", "given": ["Test"]}],
            },
        )
        assert response.status_code == 201
        patient_id = response.json()["id"]

        # Get everything
        response = client.get(f"/Patient/{patient_id}/$everything")
        assert response.status_code == 200

        data = response.json()
        # Should only have the patient
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["resourceType"] == "Patient"


class TestIncludeRevinclude:
    """Tests for _include and _revinclude parameters."""

    def test_include_patient_from_condition(self, client: TestClient) -> None:
        """Test _include follows reference from Condition to Patient."""
        response = client.get("/Condition", params={"_include": "Condition:subject"})
        assert response.status_code == 200

        data = response.json()

        # Find entries by search mode
        matches = [e for e in data["entry"] if e.get("search", {}).get("mode") == "match"]
        includes = [e for e in data["entry"] if e.get("search", {}).get("mode") == "include"]

        # Should have 3 conditions as matches
        assert len(matches) == 3

        # Should have 2 patients as includes (patient-1 and patient-2)
        assert len(includes) == 2
        for inc in includes:
            assert inc["resource"]["resourceType"] == "Patient"

    def test_revinclude_conditions_for_patient(self, client: TestClient) -> None:
        """Test _revinclude finds Conditions that reference Patient."""
        response = client.get("/Patient", params={"_id": "patient-1", "_revinclude": "Condition:patient"})
        assert response.status_code == 200

        data = response.json()

        matches = [e for e in data["entry"] if e.get("search", {}).get("mode") == "match"]
        includes = [e for e in data["entry"] if e.get("search", {}).get("mode") == "include"]

        # One patient match
        assert len(matches) == 1
        assert matches[0]["resource"]["resourceType"] == "Patient"
        assert matches[0]["resource"]["id"] == "patient-1"

        # Two condition includes
        assert len(includes) == 2
        for inc in includes:
            assert inc["resource"]["resourceType"] == "Condition"
            assert inc["resource"]["subject"]["reference"] == "Patient/patient-1"

    def test_include_with_target_type(self, client: TestClient) -> None:
        """Test _include with target type filter."""
        response = client.get("/Condition", params={"_include": "Condition:subject:Patient"})
        assert response.status_code == 200

        data = response.json()
        includes = [e for e in data["entry"] if e.get("search", {}).get("mode") == "include"]

        # All includes should be Patient
        assert len(includes) > 0
        for inc in includes:
            assert inc["resource"]["resourceType"] == "Patient"

    def test_multiple_includes(self, client: TestClient) -> None:
        """Test multiple _include parameters."""
        # This tests that multiple includes work together
        response = client.get("/Condition", params={"_include": ["Condition:subject", "Condition:encounter"]})
        assert response.status_code == 200

        data = response.json()
        # Should succeed without error
        assert data["resourceType"] == "Bundle"

    def test_revinclude_observations_for_patient(self, client: TestClient) -> None:
        """Test _revinclude with Observations."""
        response = client.get("/Patient", params={"_id": "patient-1", "_revinclude": "Observation:patient"})
        assert response.status_code == 200

        data = response.json()
        includes = [e for e in data["entry"] if e.get("search", {}).get("mode") == "include"]

        # Should have 2 observation includes for patient-1
        assert len(includes) == 2
        for inc in includes:
            assert inc["resource"]["resourceType"] == "Observation"

    def test_include_deduplication(self, client: TestClient) -> None:
        """Test that included resources are deduplicated."""
        # Both conditions for patient-1 reference the same patient
        response = client.get(
            "/Condition",
            params={"subject": "Patient/patient-1", "_include": "Condition:subject"},
        )
        assert response.status_code == 200

        data = response.json()
        includes = [e for e in data["entry"] if e.get("search", {}).get("mode") == "include"]

        # Should only have 1 patient even though 2 conditions reference it
        assert len(includes) == 1
        assert includes[0]["resource"]["id"] == "patient-1"


class TestCompartmentSearch:
    """Tests for compartment search."""

    def test_compartment_search_conditions(self, client: TestClient) -> None:
        """Test searching Conditions in Patient compartment."""
        response = client.get("/Patient/patient-1/Condition")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert data["total"] == 2

        # All conditions should be for patient-1
        for entry in data["entry"]:
            assert entry["resource"]["subject"]["reference"] == "Patient/patient-1"

    def test_compartment_search_observations(self, client: TestClient) -> None:
        """Test searching Observations in Patient compartment."""
        response = client.get("/Patient/patient-1/Observation")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2

        for entry in data["entry"]:
            assert entry["resource"]["subject"]["reference"] == "Patient/patient-1"

    def test_compartment_search_medication_requests(self, client: TestClient) -> None:
        """Test searching MedicationRequests in Patient compartment."""
        response = client.get("/Patient/patient-1/MedicationRequest")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["id"] == "medrx-1"

    def test_compartment_search_empty_result(self, client: TestClient) -> None:
        """Test compartment search with no matching resources."""
        # patient-2 has no procedures
        response = client.get("/Patient/patient-2/Procedure")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert len(data.get("entry", [])) == 0

    def test_compartment_search_patient_not_found(self, client: TestClient) -> None:
        """Test compartment search with non-existent patient."""
        response = client.get("/Patient/nonexistent/Condition")
        assert response.status_code == 404

        data = response.json()
        assert data["resourceType"] == "OperationOutcome"
        assert data["issue"][0]["code"] == "not-found"

    def test_compartment_search_unsupported_type(self, client: TestClient) -> None:
        """Test compartment search with unsupported resource type."""
        response = client.get("/Patient/patient-1/UnsupportedType")
        assert response.status_code == 400

        data = response.json()
        assert data["resourceType"] == "OperationOutcome"

    def test_compartment_search_non_compartment_type(self, client: TestClient) -> None:
        """Test compartment search with type not in Patient compartment."""
        # Practitioner is not in Patient compartment
        response = client.get("/Patient/patient-1/Practitioner")
        assert response.status_code == 400

        data = response.json()
        assert "not part of Patient compartment" in data["issue"][0]["diagnostics"]

    def test_compartment_search_with_params(self, client: TestClient) -> None:
        """Test compartment search with additional search parameters."""
        response = client.get(
            "/Patient/patient-1/Condition",
            params={"code": "http://snomed.info/sct|44054006"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["id"] == "condition-1"

    def test_compartment_search_pagination(self, client: TestClient) -> None:
        """Test compartment search pagination."""
        response = client.get("/Patient/patient-1/Condition", params={"_count": 1})
        assert response.status_code == 200

        data = response.json()
        assert len(data["entry"]) == 1
        assert data["total"] == 2

    def test_compartment_search_patient_returns_patient(self, client: TestClient) -> None:
        """Test compartment search for Patient type returns the patient."""
        response = client.get("/Patient/patient-1/Patient")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entry"][0]["resource"]["id"] == "patient-1"


class TestIncludeHandler:
    """Unit tests for IncludeHandler and compartments module."""

    def test_parse_include_param_full(self) -> None:
        """Test parsing full _include parameter."""
        from fhirkit.server.api.include_handler import IncludeHandler

        store = FHIRStore()
        handler = IncludeHandler(store)
        source, param, target = handler.parse_include_param("Condition:subject:Patient")

        assert source == "Condition"
        assert param == "subject"
        assert target == "Patient"

    def test_parse_include_param_no_target(self) -> None:
        """Test parsing _include without target type."""
        from fhirkit.server.api.include_handler import IncludeHandler

        store = FHIRStore()
        handler = IncludeHandler(store)
        source, param, target = handler.parse_include_param("Condition:subject")

        assert source == "Condition"
        assert param == "subject"
        assert target is None

    def test_get_patient_reference_paths(self) -> None:
        """Test getting patient reference paths."""
        from fhirkit.server.api.compartments import get_patient_reference_paths

        paths = get_patient_reference_paths("Condition")
        assert "subject.reference" in paths

    def test_get_reference_from_path(self) -> None:
        """Test extracting reference from path."""
        from fhirkit.server.api.compartments import get_reference_from_path

        resource = {"subject": {"reference": "Patient/123"}}
        ref = get_reference_from_path(resource, "subject.reference")
        assert ref == "Patient/123"

    def test_get_reference_from_nested_path(self) -> None:
        """Test extracting reference from deeply nested path."""
        from fhirkit.server.api.compartments import get_reference_from_path

        resource = {"performer": [{"actor": {"reference": "Practitioner/456"}}]}
        ref = get_reference_from_path(resource, "performer.actor.reference")
        assert ref == "Practitioner/456"

    def test_is_in_patient_compartment(self) -> None:
        """Test checking if resource type is in Patient compartment."""
        from fhirkit.server.api.compartments import is_in_patient_compartment

        assert is_in_patient_compartment("Condition") is True
        assert is_in_patient_compartment("Observation") is True
        assert is_in_patient_compartment("Practitioner") is False


class TestCapabilityStatement:
    """Tests for CapabilityStatement updates."""

    def test_capability_statement_includes_everything(self, client: TestClient) -> None:
        """Test CapabilityStatement includes $everything operation for Patient."""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        patient_resource = None
        for resource in data["rest"][0]["resource"]:
            if resource["type"] == "Patient":
                patient_resource = resource
                break

        assert patient_resource is not None
        # Check for $everything operation
        operation_names = [op["name"] for op in patient_resource.get("operation", [])]
        assert "everything" in operation_names

    def test_capability_statement_includes_search_include(self, client: TestClient) -> None:
        """Test CapabilityStatement includes searchInclude."""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        condition_resource = None
        for resource in data["rest"][0]["resource"]:
            if resource["type"] == "Condition":
                condition_resource = resource
                break

        assert condition_resource is not None
        # Check for searchInclude
        includes = condition_resource.get("searchInclude", [])
        assert "Condition:patient" in includes or "Condition:subject" in includes

    def test_capability_statement_includes_search_rev_include(self, client: TestClient) -> None:
        """Test CapabilityStatement includes searchRevInclude."""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        patient_resource = None
        for resource in data["rest"][0]["resource"]:
            if resource["type"] == "Patient":
                patient_resource = resource
                break

        assert patient_resource is not None
        # Patient should have revinclude for resources that reference it
        rev_includes = patient_resource.get("searchRevInclude", [])
        assert len(rev_includes) > 0
