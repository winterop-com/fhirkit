"""Tests for FHIR contained resource handling."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.api.contained import (
    ContainedResourceError,
    add_contained_resource,
    create_internal_reference,
    extract_contained_resources,
    find_internal_references,
    get_contained_by_type,
    normalize_contained_ids,
    remove_contained_resource,
    replace_contained_resource,
    resolve_contained_reference,
    validate_contained_resources,
)
from fhirkit.server.config.settings import FHIRServerSettings


@pytest.fixture
def client():
    """Create a test client."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings)
    return TestClient(app)


class TestValidateContainedResources:
    """Tests for validate_contained_resources function."""

    def test_no_contained(self):
        """Test resource with no contained."""
        resource = {"resourceType": "MedicationRequest", "id": "1"}
        issues = validate_contained_resources(resource)
        assert issues == []

    def test_valid_contained(self):
        """Test valid contained resources."""
        resource = {
            "resourceType": "MedicationRequest",
            "id": "1",
            "contained": [
                {"resourceType": "Medication", "id": "med1"},
                {"resourceType": "Practitioner", "id": "prac1"},
            ],
            "medicationReference": {"reference": "#med1"},
        }
        issues = validate_contained_resources(resource)
        assert issues == []

    def test_missing_resource_type(self):
        """Test contained without resourceType."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"id": "med1"}],
        }
        issues = validate_contained_resources(resource)
        assert len(issues) == 1
        assert "missing resourceType" in issues[0]

    def test_missing_id(self):
        """Test contained without id."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication"}],
        }
        issues = validate_contained_resources(resource)
        assert len(issues) == 1
        assert "missing id" in issues[0]

    def test_duplicate_ids(self):
        """Test duplicate contained IDs."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [
                {"resourceType": "Medication", "id": "med1"},
                {"resourceType": "Medication", "id": "med1"},
            ],
        }
        issues = validate_contained_resources(resource)
        assert len(issues) == 1
        assert "Duplicate" in issues[0]

    def test_invalid_reference(self):
        """Test internal reference to non-existent contained."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
            "medicationReference": {"reference": "#med2"},  # med2 doesn't exist
        }
        issues = validate_contained_resources(resource)
        assert len(issues) == 1
        assert "#med2" in issues[0]
        assert "not found" in issues[0]


class TestFindInternalReferences:
    """Tests for find_internal_references function."""

    def test_no_references(self):
        """Test resource with no internal references."""
        resource = {"resourceType": "Patient", "id": "1"}
        refs = find_internal_references(resource)
        assert refs == []

    def test_simple_reference(self):
        """Test simple internal reference."""
        resource = {
            "resourceType": "MedicationRequest",
            "medicationReference": {"reference": "#med1"},
        }
        refs = find_internal_references(resource)
        assert len(refs) == 1
        assert refs[0] == ("medicationReference.reference", "#med1")

    def test_nested_reference(self):
        """Test reference in nested structure."""
        resource = {
            "resourceType": "Condition",
            "evidence": [{"detail": [{"reference": "#obs1"}]}],
        }
        refs = find_internal_references(resource)
        assert len(refs) == 1
        assert "#obs1" in refs[0][1]

    def test_multiple_references(self):
        """Test multiple internal references."""
        resource = {
            "resourceType": "MedicationRequest",
            "medicationReference": {"reference": "#med1"},
            "requester": {"reference": "#prac1"},
        }
        refs = find_internal_references(resource)
        assert len(refs) == 2


class TestNormalizeContainedIds:
    """Tests for normalize_contained_ids function."""

    def test_no_contained(self):
        """Test resource with no contained."""
        resource = {"resourceType": "Patient", "id": "1"}
        result = normalize_contained_ids(resource)
        assert result == resource

    def test_ids_without_hash(self):
        """Test IDs without # prefix stay unchanged."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
        }
        result = normalize_contained_ids(resource)
        assert result["contained"][0]["id"] == "med1"

    def test_ids_with_hash(self):
        """Test IDs with # prefix are normalized."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "#med1"}],
        }
        result = normalize_contained_ids(resource)
        assert result["contained"][0]["id"] == "med1"


class TestResolveContainedReference:
    """Tests for resolve_contained_reference function."""

    def test_resolve_existing(self):
        """Test resolving existing contained resource."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1", "code": {"text": "Aspirin"}}],
        }
        result = resolve_contained_reference(resource, "#med1")
        assert result is not None
        assert result["resourceType"] == "Medication"
        assert result["code"]["text"] == "Aspirin"

    def test_resolve_non_existent(self):
        """Test resolving non-existent reference."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
        }
        result = resolve_contained_reference(resource, "#med2")
        assert result is None

    def test_resolve_non_internal(self):
        """Test non-internal reference returns None."""
        resource = {"resourceType": "MedicationRequest", "contained": []}
        result = resolve_contained_reference(resource, "Medication/123")
        assert result is None


class TestExtractContainedResources:
    """Tests for extract_contained_resources function."""

    def test_no_contained(self):
        """Test resource with no contained."""
        resource = {"resourceType": "Patient", "id": "p1"}
        result = extract_contained_resources(resource)
        assert result == []

    def test_extract_with_context(self):
        """Test extraction adds parent context."""
        resource = {
            "resourceType": "MedicationRequest",
            "id": "mr1",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
        }
        result = extract_contained_resources(resource)
        assert len(result) == 1
        assert result[0]["resourceType"] == "Medication"
        assert result[0]["_containedIn"]["resourceType"] == "MedicationRequest"
        assert result[0]["_containedIn"]["id"] == "mr1"


class TestGetContainedByType:
    """Tests for get_contained_by_type function."""

    def test_filter_by_type(self):
        """Test filtering by resource type."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [
                {"resourceType": "Medication", "id": "med1"},
                {"resourceType": "Practitioner", "id": "prac1"},
                {"resourceType": "Medication", "id": "med2"},
            ],
        }
        medications = get_contained_by_type(resource, "Medication")
        assert len(medications) == 2
        practitioners = get_contained_by_type(resource, "Practitioner")
        assert len(practitioners) == 1


class TestAddContainedResource:
    """Tests for add_contained_resource function."""

    def test_add_to_empty(self):
        """Test adding to resource with no contained."""
        resource = {"resourceType": "MedicationRequest", "id": "1"}
        contained = {"resourceType": "Medication", "id": "med1"}
        result, contained_id = add_contained_resource(resource, contained)
        assert "contained" in result
        assert len(result["contained"]) == 1
        assert contained_id == "med1"

    def test_add_to_existing(self):
        """Test adding to resource with existing contained."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
        }
        contained = {"resourceType": "Practitioner", "id": "prac1"}
        result, _ = add_contained_resource(resource, contained)
        assert len(result["contained"]) == 2

    def test_auto_generate_id(self):
        """Test auto-generating ID."""
        resource = {"resourceType": "MedicationRequest"}
        contained = {"resourceType": "Medication"}
        result, contained_id = add_contained_resource(resource, contained, auto_id=True)
        assert contained_id == "medication-1"

    def test_duplicate_id_error(self):
        """Test error on duplicate ID."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
        }
        contained = {"resourceType": "Medication", "id": "med1"}
        with pytest.raises(ContainedResourceError) as exc:
            add_contained_resource(resource, contained)
        assert "Duplicate" in str(exc.value)


class TestReplaceContainedResource:
    """Tests for replace_contained_resource function."""

    def test_replace_existing(self):
        """Test replacing existing contained resource."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1", "code": {"text": "Old"}}],
        }
        new_contained = {"resourceType": "Medication", "code": {"text": "New"}}
        result = replace_contained_resource(resource, "med1", new_contained)
        assert result["contained"][0]["code"]["text"] == "New"
        assert result["contained"][0]["id"] == "med1"

    def test_replace_non_existent(self):
        """Test error when replacing non-existent."""
        resource = {"resourceType": "MedicationRequest", "contained": []}
        with pytest.raises(ContainedResourceError):
            replace_contained_resource(resource, "med1", {"resourceType": "Medication"})


class TestRemoveContainedResource:
    """Tests for remove_contained_resource function."""

    def test_remove_existing(self):
        """Test removing existing contained resource."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [
                {"resourceType": "Medication", "id": "med1"},
                {"resourceType": "Medication", "id": "med2"},
            ],
        }
        result = remove_contained_resource(resource, "med1")
        assert len(result["contained"]) == 1
        assert result["contained"][0]["id"] == "med2"

    def test_remove_still_referenced(self):
        """Test error when removing still-referenced resource."""
        resource = {
            "resourceType": "MedicationRequest",
            "contained": [{"resourceType": "Medication", "id": "med1"}],
            "medicationReference": {"reference": "#med1"},
        }
        with pytest.raises(ContainedResourceError) as exc:
            remove_contained_resource(resource, "med1")
        assert "still referenced" in str(exc.value)


class TestCreateInternalReference:
    """Tests for create_internal_reference function."""

    def test_create_reference(self):
        """Test creating internal reference."""
        ref = create_internal_reference("med1")
        assert ref == {"reference": "#med1"}

    def test_create_reference_strips_hash(self):
        """Test creating reference strips existing hash."""
        ref = create_internal_reference("#med1")
        assert ref == {"reference": "#med1"}


class TestContainedResourcesInCRUD:
    """Integration tests for contained resources in CRUD operations."""

    def test_create_with_valid_contained(self, client):
        """Test creating resource with valid contained."""
        response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [
                    {
                        "resourceType": "Medication",
                        "id": "med1",
                        "code": {"text": "Aspirin"},
                    }
                ],
                "medicationReference": {"reference": "#med1"},
                "subject": {"reference": "Patient/123"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "contained" in data
        assert len(data["contained"]) == 1

    def test_create_with_missing_contained_id(self, client):
        """Test creating resource with contained missing ID."""
        response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [{"resourceType": "Medication"}],  # Missing ID
                "subject": {"reference": "Patient/123"},
            },
        )
        assert response.status_code == 400
        outcome = response.json()
        assert "missing id" in outcome["issue"][0]["diagnostics"]

    def test_create_with_invalid_reference(self, client):
        """Test creating resource with invalid internal reference."""
        response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [{"resourceType": "Medication", "id": "med1"}],
                "medicationReference": {"reference": "#med2"},  # med2 doesn't exist
                "subject": {"reference": "Patient/123"},
            },
        )
        assert response.status_code == 400
        outcome = response.json()
        assert "#med2" in outcome["issue"][0]["diagnostics"]

    def test_create_with_duplicate_contained_ids(self, client):
        """Test creating resource with duplicate contained IDs."""
        response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [
                    {"resourceType": "Medication", "id": "med1"},
                    {"resourceType": "Medication", "id": "med1"},  # Duplicate
                ],
                "subject": {"reference": "Patient/123"},
            },
        )
        assert response.status_code == 400
        outcome = response.json()
        assert "Duplicate" in outcome["issue"][0]["diagnostics"]

    def test_update_with_valid_contained(self, client):
        """Test updating resource with valid contained."""
        # Create first
        create_response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "subject": {"reference": "Patient/123"},
            },
        )
        assert create_response.status_code == 201
        resource_id = create_response.json()["id"]

        # Update with contained
        update_response = client.put(
            f"/MedicationRequest/{resource_id}",
            json={
                "resourceType": "MedicationRequest",
                "id": resource_id,
                "status": "active",
                "intent": "order",
                "contained": [{"resourceType": "Medication", "id": "med1"}],
                "medicationReference": {"reference": "#med1"},
                "subject": {"reference": "Patient/123"},
            },
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert "contained" in data

    def test_read_returns_contained(self, client):
        """Test reading resource returns contained resources."""
        # Create with contained
        create_response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [{"resourceType": "Medication", "id": "med1", "code": {"text": "Test"}}],
                "medicationReference": {"reference": "#med1"},
                "subject": {"reference": "Patient/123"},
            },
        )
        resource_id = create_response.json()["id"]

        # Read
        read_response = client.get(f"/MedicationRequest/{resource_id}")
        assert read_response.status_code == 200
        data = read_response.json()
        assert "contained" in data
        assert data["contained"][0]["code"]["text"] == "Test"

    def test_contained_id_normalized(self, client):
        """Test that contained IDs with # prefix are normalized."""
        response = client.post(
            "/MedicationRequest",
            json={
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "contained": [{"resourceType": "Medication", "id": "#med1"}],  # Has # prefix
                "medicationReference": {"reference": "#med1"},
                "subject": {"reference": "Patient/123"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        # ID should be normalized (no # prefix in storage)
        assert data["contained"][0]["id"] == "med1"
