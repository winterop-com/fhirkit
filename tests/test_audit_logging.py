"""Tests for FHIR server audit logging functionality."""

from unittest.mock import MagicMock

import pytest

from fhirkit.server.audit.service import (
    REST_SUBTYPES,
    AuditAction,
    AuditOutcome,
    AuditService,
)
from fhirkit.server.storage.fhir_store import FHIRStore


class TestAuditService:
    """Tests for AuditService class."""

    @pytest.fixture
    def store(self):
        """Create a test FHIR store."""
        return FHIRStore()

    @pytest.fixture
    def audit_service(self, store):
        """Create an audit service with logging enabled."""
        return AuditService(store, enabled=True, exclude_reads=False)

    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request."""
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers = {
            "User-Agent": "TestClient/1.0",
            "X-Forwarded-For": None,
        }
        request.url = MagicMock()
        request.url.query = ""
        return request

    def test_audit_service_disabled(self, store, mock_request):
        """Test that disabled audit service returns None."""
        audit = AuditService(store, enabled=False)
        result = audit.log_create(
            request=mock_request,
            resource={"resourceType": "Patient", "id": "test-123"},
        )
        assert result is None

    def test_audit_service_excludes_reads_by_default(self, store, mock_request):
        """Test that reads are excluded by default."""
        audit = AuditService(store, enabled=True, exclude_reads=True)
        result = audit.log_read(
            request=mock_request,
            resource_type="Patient",
            resource_id="test-123",
        )
        assert result is None

    def test_log_create_operation(self, audit_service, mock_request):
        """Test logging a create operation."""
        resource = {
            "resourceType": "Patient",
            "id": "patient-001",
            "name": [{"family": "Smith"}],
        }

        result = audit_service.log_create(request=mock_request, resource=resource)

        assert result is not None
        assert result["resourceType"] == "AuditEvent"
        assert result["action"] == "C"
        assert result["outcome"] == "0"

    def test_log_read_operation(self, audit_service, mock_request):
        """Test logging a read operation."""
        result = audit_service.log_read(
            request=mock_request,
            resource_type="Patient",
            resource_id="patient-001",
        )

        assert result is not None
        assert result["resourceType"] == "AuditEvent"
        assert result["action"] == "R"

    def test_log_update_operation(self, audit_service, mock_request):
        """Test logging an update operation."""
        resource = {
            "resourceType": "Patient",
            "id": "patient-001",
            "name": [{"family": "Jones"}],
        }

        result = audit_service.log_update(request=mock_request, resource=resource)

        assert result is not None
        assert result["resourceType"] == "AuditEvent"
        assert result["action"] == "U"

    def test_log_delete_operation(self, audit_service, mock_request):
        """Test logging a delete operation."""
        result = audit_service.log_delete(
            request=mock_request,
            resource_type="Patient",
            resource_id="patient-001",
        )

        assert result is not None
        assert result["resourceType"] == "AuditEvent"
        assert result["action"] == "D"

    def test_log_search_operation(self, audit_service, mock_request):
        """Test logging a search operation."""
        mock_request.url.query = "name=Smith&gender=male"

        result = audit_service.log_search(
            request=mock_request,
            resource_type="Patient",
        )

        assert result is not None
        assert result["resourceType"] == "AuditEvent"
        assert result["action"] == "R"
        # Check that query is captured in entity
        entities = result.get("entity", [])
        assert len(entities) > 0

    def test_audit_event_structure(self, audit_service, mock_request):
        """Test that audit events have correct FHIR structure."""
        resource = {"resourceType": "Patient", "id": "patient-001"}

        result = audit_service.log_create(request=mock_request, resource=resource)

        # Check required fields
        assert "type" in result
        assert result["type"]["code"] == "rest"
        assert "subtype" in result
        assert "recorded" in result
        assert "agent" in result
        assert len(result["agent"]) > 0
        assert "source" in result
        assert "entity" in result

    def test_agent_captures_client_ip(self, audit_service, mock_request):
        """Test that agent captures client IP address."""
        resource = {"resourceType": "Patient", "id": "patient-001"}

        result = audit_service.log_create(request=mock_request, resource=resource)

        agent = result["agent"][0]
        assert "network" in agent
        assert agent["network"]["address"] == "192.168.1.100"
        assert agent["network"]["type"] == "2"  # IP Address

    def test_agent_captures_forwarded_ip(self, audit_service, mock_request):
        """Test that agent captures X-Forwarded-For header."""
        mock_request.headers["X-Forwarded-For"] = "10.0.0.1, 192.168.1.1"
        resource = {"resourceType": "Patient", "id": "patient-001"}

        result = audit_service.log_create(request=mock_request, resource=resource)

        agent = result["agent"][0]
        assert agent["network"]["address"] == "10.0.0.1"

    def test_agent_captures_user_agent(self, audit_service, mock_request):
        """Test that agent captures User-Agent header."""
        resource = {"resourceType": "Patient", "id": "patient-001"}

        result = audit_service.log_create(request=mock_request, resource=resource)

        agent = result["agent"][0]
        assert "who" in agent
        assert agent["who"]["display"] == "TestClient/1.0"

    def test_outcome_failure_captured(self, audit_service, mock_request):
        """Test that failure outcomes are captured."""
        result = audit_service.log_operation(
            request=mock_request,
            action=AuditAction.CREATE,
            subtype="create",
            resource_type="Patient",
            outcome=AuditOutcome.SERIOUS_FAILURE,
            outcome_desc="Validation error: missing required field",
        )

        assert result["outcome"] == "8"
        assert result["outcomeDesc"] == "Validation error: missing required field"

    def test_patient_reference_extracted(self, audit_service, mock_request):
        """Test that patient reference is extracted from resources."""
        resource = {
            "resourceType": "Observation",
            "id": "obs-001",
            "subject": {"reference": "Patient/patient-001"},
        }

        result = audit_service.log_create(request=mock_request, resource=resource)

        entities = result.get("entity", [])
        patient_entity = next(
            (e for e in entities if e.get("what", {}).get("reference", "").startswith("Patient/")),
            None,
        )
        assert patient_entity is not None
        assert patient_entity["what"]["reference"] == "Patient/patient-001"

    def test_patient_reference_from_patient_resource(self, audit_service, mock_request):
        """Test patient reference extraction from Patient resource."""
        resource = {
            "resourceType": "Patient",
            "id": "patient-001",
        }

        result = audit_service.log_create(request=mock_request, resource=resource)

        entities = result.get("entity", [])
        patient_entity = next(
            (e for e in entities if e.get("what", {}).get("reference") == "Patient/patient-001"),
            None,
        )
        assert patient_entity is not None

    def test_no_audit_for_audit_events(self, audit_service, mock_request):
        """Test that AuditEvent operations are not audited (prevent loops)."""
        resource = {
            "resourceType": "AuditEvent",
            "id": "audit-001",
        }

        result = audit_service.log_create(request=mock_request, resource=resource)

        assert result is None

    def test_rest_subtypes_defined(self):
        """Test that all REST subtypes are defined."""
        expected_subtypes = ["create", "read", "vread", "update", "delete", "search", "history", "batch", "transaction"]
        for subtype in expected_subtypes:
            assert subtype in REST_SUBTYPES
            assert "system" in REST_SUBTYPES[subtype]
            assert "code" in REST_SUBTYPES[subtype]

    def test_audit_action_enum(self):
        """Test AuditAction enum values."""
        assert AuditAction.CREATE.value == "C"
        assert AuditAction.READ.value == "R"
        assert AuditAction.UPDATE.value == "U"
        assert AuditAction.DELETE.value == "D"
        assert AuditAction.EXECUTE.value == "E"

    def test_audit_outcome_enum(self):
        """Test AuditOutcome enum values."""
        assert AuditOutcome.SUCCESS.value == "0"
        assert AuditOutcome.MINOR_FAILURE.value == "4"
        assert AuditOutcome.SERIOUS_FAILURE.value == "8"
        assert AuditOutcome.MAJOR_FAILURE.value == "12"


class TestAuditServiceIntegration:
    """Integration tests for audit logging."""

    @pytest.fixture
    def store(self):
        """Create a test FHIR store."""
        return FHIRStore()

    @pytest.fixture
    def audit_service(self, store):
        """Create an audit service."""
        return AuditService(store, enabled=True, exclude_reads=False)

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {"User-Agent": "Test"}
        request.url = MagicMock()
        request.url.query = ""
        return request

    def test_audit_events_persisted(self, store, audit_service, mock_request):
        """Test that audit events are persisted to store."""
        resource = {"resourceType": "Patient", "id": "test-patient"}

        audit_service.log_create(request=mock_request, resource=resource)

        # Search for audit events
        results, total = store.search("AuditEvent", {})
        assert total >= 1

    def test_audit_events_searchable(self, store, audit_service, mock_request):
        """Test that audit events can be searched."""
        resource = {"resourceType": "Patient", "id": "test-patient"}

        audit_service.log_create(request=mock_request, resource=resource)
        audit_service.log_update(request=mock_request, resource=resource)

        # Search by action
        results, total = store.search("AuditEvent", {"action": "C"})
        assert total >= 1

    def test_multiple_operations_logged(self, store, audit_service, mock_request):
        """Test logging multiple operations."""
        resource = {"resourceType": "Patient", "id": "multi-test"}

        audit_service.log_create(request=mock_request, resource=resource)
        audit_service.log_read(
            request=mock_request,
            resource_type="Patient",
            resource_id="multi-test",
        )
        audit_service.log_update(request=mock_request, resource=resource)
        audit_service.log_delete(
            request=mock_request,
            resource_type="Patient",
            resource_id="multi-test",
        )

        results, total = store.search("AuditEvent", {})
        assert total >= 4
