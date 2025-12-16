"""Tests for Questionnaire and QuestionnaireResponse REST API."""

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
def client_with_questionnaire(store):
    """Create a test client with preloaded questionnaire data."""
    # Add a patient for QuestionnaireResponse
    store.create(
        {
            "resourceType": "Patient",
            "id": "test-patient-1",
            "name": [{"family": "Smith", "given": ["John"]}],
        }
    )

    # Add a Questionnaire
    store.create(
        {
            "resourceType": "Questionnaire",
            "id": "phq-9",
            "url": "http://example.org/fhir/Questionnaire/phq-9",
            "name": "PHQ9",
            "title": "Patient Health Questionnaire - 9 Item",
            "status": "active",
            "publisher": "FHIRKit",
            "description": "Depression screening questionnaire",
            "item": [
                {
                    "linkId": "q1",
                    "text": "Little interest or pleasure in doing things?",
                    "type": "choice",
                    "answerOption": [
                        {"valueCoding": {"code": "0", "display": "Not at all"}},
                        {"valueCoding": {"code": "1", "display": "Several days"}},
                        {"valueCoding": {"code": "2", "display": "More than half the days"}},
                        {"valueCoding": {"code": "3", "display": "Nearly every day"}},
                    ],
                }
            ],
        }
    )

    # Add a QuestionnaireResponse
    store.create(
        {
            "resourceType": "QuestionnaireResponse",
            "id": "response-1",
            "questionnaire": "Questionnaire/phq-9",
            "status": "completed",
            "subject": {"reference": "Patient/test-patient-1"},
            "authored": "2025-01-15T10:30:00Z",
            "item": [
                {
                    "linkId": "q1",
                    "answer": [{"valueCoding": {"code": "1", "display": "Several days"}}],
                }
            ],
        }
    )

    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


class TestQuestionnaireCRUD:
    """Tests for Questionnaire CRUD operations."""

    def test_create_questionnaire(self, client):
        """Test creating a questionnaire via POST."""
        questionnaire = {
            "resourceType": "Questionnaire",
            "url": "http://example.org/fhir/Questionnaire/test",
            "name": "TestQuestionnaire",
            "title": "Test Questionnaire",
            "status": "draft",
            "item": [
                {
                    "linkId": "q1",
                    "text": "What is your name?",
                    "type": "string",
                }
            ],
        }

        response = client.post("/Questionnaire", json=questionnaire)
        assert response.status_code == 201

        data = response.json()
        assert data["resourceType"] == "Questionnaire"
        assert "id" in data
        assert data["name"] == "TestQuestionnaire"

    def test_read_questionnaire(self, client_with_questionnaire):
        """Test reading a questionnaire by ID."""
        response = client_with_questionnaire.get("/Questionnaire/phq-9")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Questionnaire"
        assert data["id"] == "phq-9"
        assert data["title"] == "Patient Health Questionnaire - 9 Item"

    def test_search_questionnaire_by_name(self, client_with_questionnaire):
        """Test searching questionnaires by name."""
        response = client_with_questionnaire.get("/Questionnaire?name=PHQ9")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_search_questionnaire_by_url(self, client_with_questionnaire):
        """Test searching questionnaires by url."""
        response = client_with_questionnaire.get("/Questionnaire?url=http://example.org/fhir/Questionnaire/phq-9")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_search_questionnaire_by_status(self, client_with_questionnaire):
        """Test searching questionnaires by status."""
        response = client_with_questionnaire.get("/Questionnaire?status=active")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_update_questionnaire(self, client_with_questionnaire):
        """Test updating a questionnaire via PUT."""
        updated = {
            "resourceType": "Questionnaire",
            "id": "phq-9",
            "url": "http://example.org/fhir/Questionnaire/phq-9",
            "name": "PHQ9Updated",
            "title": "Patient Health Questionnaire - 9 Item (Updated)",
            "status": "active",
            "item": [],
        }

        response = client_with_questionnaire.put("/Questionnaire/phq-9", json=updated)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Patient Health Questionnaire - 9 Item (Updated)"

    def test_delete_questionnaire(self, client_with_questionnaire):
        """Test deleting a questionnaire."""
        response = client_with_questionnaire.delete("/Questionnaire/phq-9")
        assert response.status_code == 204

        # Verify it's gone
        response = client_with_questionnaire.get("/Questionnaire/phq-9")
        assert response.status_code == 404


class TestQuestionnaireResponseCRUD:
    """Tests for QuestionnaireResponse CRUD operations."""

    def test_create_questionnaire_response(self, client_with_questionnaire):
        """Test creating a questionnaire response via POST."""
        response_resource = {
            "resourceType": "QuestionnaireResponse",
            "questionnaire": "Questionnaire/phq-9",
            "status": "completed",
            "subject": {"reference": "Patient/test-patient-1"},
            "authored": "2025-01-15T11:00:00Z",
            "item": [
                {
                    "linkId": "q1",
                    "answer": [{"valueCoding": {"code": "2", "display": "More than half the days"}}],
                }
            ],
        }

        response = client_with_questionnaire.post("/QuestionnaireResponse", json=response_resource)
        assert response.status_code == 201

        data = response.json()
        assert data["resourceType"] == "QuestionnaireResponse"
        assert "id" in data
        assert data["status"] == "completed"

    def test_read_questionnaire_response(self, client_with_questionnaire):
        """Test reading a questionnaire response by ID."""
        response = client_with_questionnaire.get("/QuestionnaireResponse/response-1")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "QuestionnaireResponse"
        assert data["id"] == "response-1"
        assert data["status"] == "completed"

    def test_search_response_by_questionnaire(self, client_with_questionnaire):
        """Test searching responses by questionnaire reference."""
        response = client_with_questionnaire.get("/QuestionnaireResponse?questionnaire=Questionnaire/phq-9")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_search_response_by_patient(self, client_with_questionnaire):
        """Test searching responses by patient."""
        response = client_with_questionnaire.get("/QuestionnaireResponse?patient=Patient/test-patient-1")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_search_response_by_status(self, client_with_questionnaire):
        """Test searching responses by status."""
        response = client_with_questionnaire.get("/QuestionnaireResponse?status=completed")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_search_response_by_authored(self, client_with_questionnaire):
        """Test searching responses by authored date."""
        response = client_with_questionnaire.get("/QuestionnaireResponse?authored=2025-01-15")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] >= 1

    def test_update_questionnaire_response(self, client_with_questionnaire):
        """Test updating a questionnaire response via PUT."""
        updated = {
            "resourceType": "QuestionnaireResponse",
            "id": "response-1",
            "questionnaire": "Questionnaire/phq-9",
            "status": "amended",
            "subject": {"reference": "Patient/test-patient-1"},
            "authored": "2025-01-15T10:30:00Z",
            "item": [
                {
                    "linkId": "q1",
                    "answer": [{"valueCoding": {"code": "3", "display": "Nearly every day"}}],
                }
            ],
        }

        response = client_with_questionnaire.put("/QuestionnaireResponse/response-1", json=updated)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "amended"

    def test_delete_questionnaire_response(self, client_with_questionnaire):
        """Test deleting a questionnaire response."""
        response = client_with_questionnaire.delete("/QuestionnaireResponse/response-1")
        assert response.status_code == 204

        # Verify it's gone
        response = client_with_questionnaire.get("/QuestionnaireResponse/response-1")
        assert response.status_code == 404


class TestQuestionnaireInMetadata:
    """Test that Questionnaire resources appear in CapabilityStatement."""

    def test_questionnaire_in_capability_statement(self, client):
        """Test that Questionnaire and QuestionnaireResponse are listed."""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        resources = data["rest"][0]["resource"]
        resource_types = {r["type"] for r in resources}

        assert "Questionnaire" in resource_types
        assert "QuestionnaireResponse" in resource_types
