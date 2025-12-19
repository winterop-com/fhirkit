"""Tests for the FHIR GraphQL endpoint.

These tests verify the GraphQL API functionality including:
- Single resource queries
- List queries with search parameters
- Connection pagination
- Reference resolution
- Mutations (Create, Update, Delete)
"""

import pytest
from starlette.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store():
    """Create a fresh FHIR store for each test."""
    return FHIRStore()


@pytest.fixture
def app(store):
    """Create a test app with the store."""
    from fhirkit.server.config.settings import FHIRServerSettings

    settings = FHIRServerSettings(patients=0, enable_ui=False)
    return create_app(settings=settings, store=store)


@pytest.fixture
def client(app):
    """Create a sync test client."""
    return TestClient(app)


class TestSingleResourceQueries:
    """Tests for single resource queries (e.g., patient(id: "123"))."""

    def test_query_patient_by_id(self, client, store):
        """Test fetching a single Patient by ID."""
        patient = store.create(
            {
                "resourceType": "Patient",
                "name": [{"family": "Smith", "given": ["John"]}],
                "gender": "male",
            }
        )
        patient_id = patient["id"]

        query = f"""
        {{
            patient(id: "{patient_id}") {{
                id
                resourceType
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["patient"]["id"] == patient_id
        assert data["data"]["patient"]["resourceType"] == "Patient"
        assert data["data"]["patient"]["data"]["name"][0]["family"] == "Smith"

    def test_query_nonexistent_patient(self, client, store):
        """Test that querying a nonexistent patient returns null."""
        query = """
        {
            patient(id: "nonexistent-id") {
                id
                resourceType
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["patient"] is None

    def test_generic_resource_query(self, client, store):
        """Test the generic resource query for any type."""
        obs = store.create(
            {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "Heart Rate"},
            }
        )

        query = f"""
        {{
            resource(resourceType: "Observation", id: "{obs["id"]}") {{
                id
                resourceType
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["resource"]["resourceType"] == "Observation"


class TestListQueries:
    """Tests for list queries with search parameters."""

    def test_patient_list_basic(self, client, store):
        """Test basic patient list query."""
        store.create({"resourceType": "Patient", "name": [{"family": "Smith"}], "gender": "male"})
        store.create({"resourceType": "Patient", "name": [{"family": "Jones"}], "gender": "female"})

        query = """
        {
            patients(_count: 10) {
                id
                resourceType
                data
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert len(data["data"]["patients"]) == 2

    def test_patient_list_with_gender_filter(self, client, store):
        """Test patient list query with gender filter."""
        store.create({"resourceType": "Patient", "name": [{"family": "Smith"}], "gender": "male"})
        store.create({"resourceType": "Patient", "name": [{"family": "Jones"}], "gender": "female"})
        store.create({"resourceType": "Patient", "name": [{"family": "Doe"}], "gender": "male"})

        query = """
        {
            patients(gender: "male") {
                id
                data
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["patients"]) == 2
        for patient in data["data"]["patients"]:
            assert patient["data"]["gender"] == "male"

    def test_patient_list_with_count_limit(self, client, store):
        """Test patient list query with _count limit."""
        for i in range(5):
            store.create({"resourceType": "Patient", "name": [{"family": f"Patient{i}"}]})

        query = """
        {
            patients(_count: 3) {
                id
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["patients"]) == 3

    def test_observation_list_with_patient_filter(self, client, store):
        """Test observation list query with patient filter."""
        patient = store.create({"resourceType": "Patient", "name": [{"family": "Test"}]})
        patient_ref = f"Patient/{patient['id']}"

        store.create(
            {
                "resourceType": "Observation",
                "status": "final",
                "subject": {"reference": patient_ref},
                "code": {"text": "BP"},
            }
        )
        store.create(
            {
                "resourceType": "Observation",
                "status": "final",
                "subject": {"reference": patient_ref},
                "code": {"text": "HR"},
            }
        )
        store.create(
            {
                "resourceType": "Observation",
                "status": "final",
                "subject": {"reference": "Patient/other"},
                "code": {"text": "Temp"},
            }
        )

        query = f"""
        {{
            observations(patient: "{patient_ref}") {{
                id
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["observations"]) == 2


class TestConnectionQueries:
    """Tests for connection queries with cursor-based pagination."""

    def test_patient_connection_basic(self, client, store):
        """Test basic patient connection query."""
        for i in range(5):
            store.create({"resourceType": "Patient", "name": [{"family": f"Patient{i}"}]})

        query = """
        {
            patientConnection(first: 3) {
                edges {
                    cursor
                    node {
                        id
                        data
                    }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
                total
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        connection = data["data"]["patientConnection"]
        assert len(connection["edges"]) == 3
        assert connection["total"] == 5
        assert connection["pageInfo"]["hasNextPage"] is True
        assert connection["pageInfo"]["hasPreviousPage"] is False

    def test_patient_connection_pagination(self, client, store):
        """Test connection pagination with after cursor."""
        for i in range(5):
            store.create({"resourceType": "Patient", "name": [{"family": f"Patient{i}"}]})

        # Get first page
        query = """
        {
            patientConnection(first: 2) {
                edges {
                    cursor
                    node { id }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})
        data = response.json()
        first_page = data["data"]["patientConnection"]
        end_cursor = first_page["pageInfo"]["endCursor"]

        # Get second page
        query = f"""
        {{
            patientConnection(first: 2, after: "{end_cursor}") {{
                edges {{
                    cursor
                    node {{ id }}
                }}
                pageInfo {{
                    hasNextPage
                    hasPreviousPage
                }}
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})
        data = response.json()
        second_page = data["data"]["patientConnection"]
        assert len(second_page["edges"]) == 2
        assert second_page["pageInfo"]["hasPreviousPage"] is True
        assert second_page["pageInfo"]["hasNextPage"] is True


class TestMutations:
    """Tests for GraphQL mutations."""

    def test_patient_create(self, client, store):
        """Test creating a patient via mutation."""
        # Use variables to pass JSON data properly
        mutation = """
        mutation CreatePatient($data: JSON!) {
            createPatient(data: $data) {
                id
                resourceType
                data
            }
        }
        """
        variables = {
            "data": {"resourceType": "Patient", "name": [{"family": "New", "given": ["Test"]}], "gender": "female"}
        }
        response = client.post("/baseR4/$graphql", json={"query": mutation, "variables": variables})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        created = data["data"]["createPatient"]
        assert created["id"] is not None
        assert created["resourceType"] == "Patient"
        assert created["data"]["name"][0]["family"] == "New"

        # Verify it was stored
        stored = store.read("Patient", created["id"])
        assert stored is not None
        assert stored["name"][0]["family"] == "New"

    def test_patient_update(self, client, store):
        """Test updating a patient via mutation."""
        patient = store.create(
            {
                "resourceType": "Patient",
                "name": [{"family": "Original"}],
                "gender": "male",
            }
        )

        # Use variables to pass JSON data properly
        mutation = """
        mutation UpdatePatient($id: String!, $data: JSON!) {
            updatePatient(id: $id, data: $data) {
                id
                data
            }
        }
        """
        variables = {
            "id": patient["id"],
            "data": {"resourceType": "Patient", "name": [{"family": "Updated"}], "gender": "male"},
        }
        response = client.post("/baseR4/$graphql", json={"query": mutation, "variables": variables})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        updated = data["data"]["updatePatient"]
        assert updated["data"]["name"][0]["family"] == "Updated"

    def test_patient_delete(self, client, store):
        """Test deleting a patient via mutation."""
        patient = store.create(
            {
                "resourceType": "Patient",
                "name": [{"family": "ToDelete"}],
            }
        )
        patient_id = patient["id"]

        mutation = f"""
        mutation {{
            deletePatient(id: "{patient_id}") {{
                id
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": mutation})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        deleted = data["data"]["deletePatient"]
        assert deleted["id"] == patient_id

    def test_generic_resource_create(self, client, store):
        """Test creating a resource via generic mutation."""
        # Use variables to pass JSON data properly
        mutation = """
        mutation CreateResource($resourceType: String!, $data: JSON!) {
            resourceCreate(resourceType: $resourceType, data: $data) {
                id
                resourceType
                data
            }
        }
        """
        variables = {
            "resourceType": "Observation",
            "data": {"resourceType": "Observation", "status": "final", "code": {"text": "Test Observation"}},
        }
        response = client.post("/baseR4/$graphql", json={"query": mutation, "variables": variables})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        created = data["data"]["resourceCreate"]
        assert created["resourceType"] == "Observation"
        assert created["data"]["status"] == "final"


class TestGraphiQL:
    """Tests for GraphiQL playground."""

    def test_graphiql_loads(self, client):
        """Test that GraphiQL playground loads."""
        response = client.get("/baseR4/$graphql")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_resource_type_generic_query(self, client):
        """Test querying with invalid resource type."""
        query = """
        {
            resource(resourceType: "InvalidType", id: "123") {
                id
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["resource"] is None

    def test_invalid_resource_type_generic_mutation(self, client):
        """Test creating with invalid resource type."""
        mutation = """
        mutation {
            resourceCreate(resourceType: "InvalidType", data: {}) {
                id
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": mutation})

        assert response.status_code == 200
        data = response.json()
        assert "errors" in data


class TestMultipleResourceTypes:
    """Tests for various resource types."""

    def test_query_condition(self, client, store):
        """Test querying a Condition resource."""
        condition = store.create(
            {
                "resourceType": "Condition",
                "clinicalStatus": {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
                },
                "code": {"text": "Diabetes"},
            }
        )

        query = f"""
        {{
            condition(id: "{condition["id"]}") {{
                id
                resourceType
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["condition"]["data"]["code"]["text"] == "Diabetes"

    def test_query_encounter(self, client, store):
        """Test querying an Encounter resource."""
        encounter = store.create(
            {
                "resourceType": "Encounter",
                "status": "finished",
                "class": {"code": "AMB"},
            }
        )

        query = f"""
        {{
            encounter(id: "{encounter["id"]}") {{
                id
                data
            }}
        }}
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["encounter"]["data"]["status"] == "finished"

    def test_condition_list_with_filters(self, client, store):
        """Test conditions with clinical status filter."""
        store.create(
            {
                "resourceType": "Condition",
                "clinicalStatus": {"coding": [{"code": "active"}]},
                "code": {"text": "Condition1"},
            }
        )
        store.create(
            {
                "resourceType": "Condition",
                "clinicalStatus": {"coding": [{"code": "resolved"}]},
                "code": {"text": "Condition2"},
            }
        )

        # Use clinicalStatus (camelCase) as defined in the GraphQL schema
        query = """
        {
            conditions(clinicalStatus: "active") {
                id
                data
            }
        }
        """
        response = client.post("/baseR4/$graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["conditions"]) >= 1
