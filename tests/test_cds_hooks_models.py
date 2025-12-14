"""Tests for CDS Hooks Pydantic models."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from fhirkit.cds_hooks.models.discovery import CDSServiceDescriptor, DiscoveryResponse
from fhirkit.cds_hooks.models.feedback import (
    AcceptedSuggestion,
    FeedbackEntry,
    FeedbackRequest,
    OverrideReason,
)
from fhirkit.cds_hooks.models.request import CDSRequest, FHIRAuthorization
from fhirkit.cds_hooks.models.response import (
    Action,
    Card,
    CDSResponse,
    Coding,
    Link,
    Source,
    Suggestion,
)

# =============================================================================
# CDSServiceDescriptor Tests
# =============================================================================


class TestCDSServiceDescriptor:
    """Tests for CDSServiceDescriptor model."""

    def test_valid_descriptor(self) -> None:
        """Test creating a valid service descriptor."""
        descriptor = CDSServiceDescriptor(
            hook="patient-view",
            id="test-service",
            description="A test service",
        )
        assert descriptor.hook == "patient-view"
        assert descriptor.id == "test-service"
        assert descriptor.description == "A test service"

    def test_descriptor_with_all_fields(self) -> None:
        """Test descriptor with all optional fields."""
        descriptor = CDSServiceDescriptor(
            hook="order-sign",
            id="med-safety",
            title="Medication Safety",
            description="Checks for drug interactions",
            prefetch={"patient": "Patient/{{context.patientId}}"},
            usageRequirements="Requires medication data",
        )
        assert descriptor.title == "Medication Safety"
        assert descriptor.prefetch == {"patient": "Patient/{{context.patientId}}"}
        assert descriptor.usageRequirements == "Requires medication data"

    def test_valid_id_patterns(self) -> None:
        """Test that valid ID patterns are accepted."""
        valid_ids = [
            "service",
            "service-name",
            "service_name",
            "Service123",
            "my-cds-service-v2",
            "CDS_Service_1",
        ]
        for id_val in valid_ids:
            descriptor = CDSServiceDescriptor(
                hook="patient-view",
                id=id_val,
                description="Test",
            )
            assert descriptor.id == id_val

    def test_invalid_id_patterns(self) -> None:
        """Test that invalid ID patterns are rejected."""
        invalid_ids = [
            "service name",  # space
            "service.name",  # dot
            "service@name",  # special char
            "service/name",  # slash
        ]
        for id_val in invalid_ids:
            with pytest.raises(ValidationError):
                CDSServiceDescriptor(
                    hook="patient-view",
                    id=id_val,
                    description="Test",
                )

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise errors."""
        with pytest.raises(ValidationError):
            CDSServiceDescriptor(hook="patient-view", id="test")  # missing description

        with pytest.raises(ValidationError):
            CDSServiceDescriptor(hook="patient-view", description="test")  # missing id

        with pytest.raises(ValidationError):
            CDSServiceDescriptor(id="test", description="test")  # missing hook

    def test_json_serialization(self) -> None:
        """Test JSON serialization."""
        descriptor = CDSServiceDescriptor(
            hook="patient-view",
            id="test-service",
            title="Test",
            description="A test",
        )
        json_data = descriptor.model_dump()
        assert json_data["hook"] == "patient-view"
        assert json_data["id"] == "test-service"
        assert json_data["title"] == "Test"


class TestDiscoveryResponse:
    """Tests for DiscoveryResponse model."""

    def test_empty_services(self) -> None:
        """Test discovery response with no services."""
        response = DiscoveryResponse()
        assert response.services == []

    def test_with_services(self) -> None:
        """Test discovery response with services."""
        descriptor = CDSServiceDescriptor(
            hook="patient-view",
            id="test",
            description="Test service",
        )
        response = DiscoveryResponse(services=[descriptor])
        assert len(response.services) == 1
        assert response.services[0].id == "test"

    def test_multiple_services(self) -> None:
        """Test discovery response with multiple services."""
        services = [
            CDSServiceDescriptor(hook="patient-view", id="svc1", description="Service 1"),
            CDSServiceDescriptor(hook="order-sign", id="svc2", description="Service 2"),
        ]
        response = DiscoveryResponse(services=services)
        assert len(response.services) == 2


# =============================================================================
# FHIRAuthorization Tests
# =============================================================================


class TestFHIRAuthorization:
    """Tests for FHIRAuthorization model."""

    def test_valid_authorization(self) -> None:
        """Test creating valid authorization."""
        auth = FHIRAuthorization(
            access_token="abc123",
            token_type="Bearer",
            expires_in=3600,
            scope="patient/*.read",
            subject="user-123",
        )
        assert auth.access_token == "abc123"
        assert auth.token_type == "Bearer"
        assert auth.expires_in == 3600

    def test_default_token_type(self) -> None:
        """Test default token type is Bearer."""
        auth = FHIRAuthorization(
            access_token="token",
            expires_in=3600,
            scope="patient/*.read",
            subject="user",
        )
        assert auth.token_type == "Bearer"

    def test_optional_patient(self) -> None:
        """Test optional patient field."""
        auth = FHIRAuthorization(
            access_token="token",
            expires_in=3600,
            scope="patient/*.read",
            subject="user",
            patient="Patient/123",
        )
        assert auth.patient == "Patient/123"

    def test_json_alias(self) -> None:
        """Test field aliasing for JSON."""
        auth = FHIRAuthorization(
            access_token="token",
            token_type="Bearer",
            expires_in=3600,
            scope="patient/*.read",
            subject="user",
        )
        json_data = auth.model_dump(by_alias=True)
        assert "access_token" in json_data
        assert "token_type" in json_data
        assert "expires_in" in json_data


# =============================================================================
# CDSRequest Tests
# =============================================================================


class TestCDSRequest:
    """Tests for CDSRequest model."""

    def test_valid_request(self) -> None:
        """Test creating a valid CDS request."""
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={"patientId": "123", "userId": "456"},
        )
        assert request.hook == "patient-view"
        assert isinstance(request.hookInstance, UUID)
        assert request.context["patientId"] == "123"

    def test_with_fhir_server(self) -> None:
        """Test request with FHIR server."""
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={},
            fhirServer="https://fhir.example.org",
        )
        assert request.fhirServer == "https://fhir.example.org"

    def test_with_authorization(self) -> None:
        """Test request with FHIR authorization."""
        auth = FHIRAuthorization(
            access_token="token",
            expires_in=3600,
            scope="patient/*.read",
            subject="user",
        )
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={},
            fhirAuthorization=auth,
        )
        assert request.fhirAuthorization is not None
        assert request.fhirAuthorization.access_token == "token"

    def test_with_prefetch(self) -> None:
        """Test request with prefetch data."""
        prefetch = {
            "patient": {"resourceType": "Patient", "id": "123"},
            "conditions": {"resourceType": "Bundle", "entry": []},
        }
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid4(),
            context={},
            prefetch=prefetch,
        )
        assert request.prefetch is not None
        assert request.prefetch["patient"]["resourceType"] == "Patient"

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise errors."""
        with pytest.raises(ValidationError):
            CDSRequest(hook="patient-view", context={})  # missing hookInstance

        with pytest.raises(ValidationError):
            CDSRequest(hookInstance=uuid4(), context={})  # missing hook

    def test_uuid_string_conversion(self) -> None:
        """Test that UUID strings are converted."""
        uuid_str = "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea"
        request = CDSRequest(
            hook="patient-view",
            hookInstance=uuid_str,  # type: ignore
            context={},
        )
        assert isinstance(request.hookInstance, UUID)
        assert str(request.hookInstance) == uuid_str


# =============================================================================
# Coding Tests
# =============================================================================


class TestCoding:
    """Tests for Coding model."""

    def test_full_coding(self) -> None:
        """Test coding with all fields."""
        coding = Coding(
            system="http://snomed.info/sct",
            code="12345",
            display="Test Concept",
        )
        assert coding.system == "http://snomed.info/sct"
        assert coding.code == "12345"
        assert coding.display == "Test Concept"

    def test_partial_coding(self) -> None:
        """Test coding with only code."""
        coding = Coding(code="12345")
        assert coding.code == "12345"
        assert coding.system is None
        assert coding.display is None

    def test_empty_coding(self) -> None:
        """Test coding with no fields."""
        coding = Coding()
        assert coding.system is None
        assert coding.code is None
        assert coding.display is None


# =============================================================================
# Source Tests
# =============================================================================


class TestSource:
    """Tests for Source model."""

    def test_required_label(self) -> None:
        """Test that label is required."""
        source = Source(label="My CDS Service")
        assert source.label == "My CDS Service"

    def test_with_url(self) -> None:
        """Test source with URL."""
        source = Source(label="CDS", url="https://example.org")
        assert source.url == "https://example.org"

    def test_with_icon(self) -> None:
        """Test source with icon."""
        source = Source(label="CDS", icon="https://example.org/icon.png")
        assert source.icon == "https://example.org/icon.png"

    def test_with_topic(self) -> None:
        """Test source with topic coding."""
        source = Source(
            label="CDS",
            topic=Coding(code="medication-safety"),
        )
        assert source.topic is not None
        assert source.topic.code == "medication-safety"

    def test_missing_label(self) -> None:
        """Test that missing label raises error."""
        with pytest.raises(ValidationError):
            Source()  # type: ignore


# =============================================================================
# Action Tests
# =============================================================================


class TestAction:
    """Tests for Action model."""

    def test_create_action(self) -> None:
        """Test create action."""
        action = Action(
            type="create",
            description="Create a medication order",
            resource={"resourceType": "MedicationRequest"},
        )
        assert action.type == "create"
        assert action.description == "Create a medication order"
        assert action.resource is not None

    def test_update_action(self) -> None:
        """Test update action."""
        action = Action(
            type="update",
            description="Update the order",
            resourceId="MedicationRequest/123",
        )
        assert action.type == "update"
        assert action.resourceId == "MedicationRequest/123"

    def test_delete_action(self) -> None:
        """Test delete action."""
        action = Action(
            type="delete",
            description="Delete the order",
        )
        assert action.type == "delete"

    def test_invalid_action_type(self) -> None:
        """Test that invalid action type raises error."""
        with pytest.raises(ValidationError):
            Action(type="invalid", description="Test")  # type: ignore


# =============================================================================
# Suggestion Tests
# =============================================================================


class TestSuggestion:
    """Tests for Suggestion model."""

    def test_basic_suggestion(self) -> None:
        """Test basic suggestion."""
        suggestion = Suggestion(label="Review medication")
        assert suggestion.label == "Review medication"
        assert suggestion.uuid is None
        assert suggestion.isRecommended is None

    def test_recommended_suggestion(self) -> None:
        """Test recommended suggestion."""
        suggestion = Suggestion(
            label="Accept recommendation",
            isRecommended=True,
        )
        assert suggestion.isRecommended is True

    def test_suggestion_with_actions(self) -> None:
        """Test suggestion with actions."""
        action = Action(type="create", description="Create task")
        suggestion = Suggestion(
            label="Create follow-up",
            actions=[action],
        )
        assert len(suggestion.actions) == 1

    def test_label_truncation(self) -> None:
        """Test that long labels are truncated to 80 chars."""
        long_label = "A" * 100  # 100 characters
        suggestion = Suggestion(label=long_label)
        assert len(suggestion.label) <= 80
        assert suggestion.label.endswith("...")

    def test_label_at_limit(self) -> None:
        """Test that label at exactly 80 chars is not truncated."""
        label = "A" * 80
        suggestion = Suggestion(label=label)
        assert suggestion.label == label
        assert not suggestion.label.endswith("...")


# =============================================================================
# Link Tests
# =============================================================================


class TestLink:
    """Tests for Link model."""

    def test_absolute_link(self) -> None:
        """Test absolute link."""
        link = Link(
            label="More info",
            url="https://example.org/info",
            type="absolute",
        )
        assert link.type == "absolute"
        assert link.url == "https://example.org/info"

    def test_smart_link(self) -> None:
        """Test SMART app link."""
        link = Link(
            label="Launch app",
            url="https://smart.example.org/launch",
            type="smart",
            appContext='{"patient":"123"}',
        )
        assert link.type == "smart"
        assert link.appContext is not None

    def test_invalid_link_type(self) -> None:
        """Test that invalid link type raises error."""
        with pytest.raises(ValidationError):
            Link(label="Test", url="https://example.org", type="invalid")  # type: ignore

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise error."""
        with pytest.raises(ValidationError):
            Link(label="Test", type="absolute")  # type: ignore # missing url

        with pytest.raises(ValidationError):
            Link(url="https://example.org", type="absolute")  # type: ignore # missing label


# =============================================================================
# Card Tests
# =============================================================================


class TestCard:
    """Tests for Card model."""

    def test_minimal_card(self) -> None:
        """Test card with minimal required fields."""
        card = Card(
            summary="Drug interaction detected",
            indicator="warning",
            source=Source(label="CDS Service"),
        )
        assert card.summary == "Drug interaction detected"
        assert card.indicator == "warning"
        assert card.source.label == "CDS Service"

    def test_full_card(self) -> None:
        """Test card with all fields."""
        card = Card(
            uuid="card-123",
            summary="Alert",
            detail="Detailed **markdown** content",
            indicator="critical",
            source=Source(label="CDS"),
            suggestions=[Suggestion(label="Review")],
            selectionBehavior="at-most-one",
            overrideReasons=[Coding(code="patient-preference")],
            links=[Link(label="More", url="https://example.org", type="absolute")],
        )
        assert card.uuid == "card-123"
        assert card.detail is not None
        assert len(card.suggestions) == 1
        assert card.selectionBehavior == "at-most-one"
        assert len(card.overrideReasons) == 1
        assert len(card.links) == 1

    def test_valid_indicators(self) -> None:
        """Test all valid indicator values."""
        for indicator in ["info", "warning", "critical"]:
            card = Card(
                summary="Test",
                indicator=indicator,  # type: ignore
                source=Source(label="CDS"),
            )
            assert card.indicator == indicator

    def test_invalid_indicator(self) -> None:
        """Test that invalid indicator raises error."""
        with pytest.raises(ValidationError):
            Card(
                summary="Test",
                indicator="error",  # type: ignore
                source=Source(label="CDS"),
            )

    def test_summary_truncation(self) -> None:
        """Test that long summaries are truncated to 140 chars."""
        long_summary = "A" * 200  # 200 characters
        card = Card(
            summary=long_summary,
            indicator="info",
            source=Source(label="CDS"),
        )
        assert len(card.summary) <= 140
        assert card.summary.endswith("...")

    def test_summary_at_limit(self) -> None:
        """Test that summary at exactly 140 chars is not truncated."""
        summary = "A" * 140
        card = Card(
            summary=summary,
            indicator="info",
            source=Source(label="CDS"),
        )
        assert card.summary == summary
        assert not card.summary.endswith("...")

    def test_selection_behavior_values(self) -> None:
        """Test valid selection behavior values."""
        for behavior in ["at-most-one", "any"]:
            card = Card(
                summary="Test",
                indicator="info",
                source=Source(label="CDS"),
                selectionBehavior=behavior,  # type: ignore
            )
            assert card.selectionBehavior == behavior


# =============================================================================
# CDSResponse Tests
# =============================================================================


class TestCDSResponse:
    """Tests for CDSResponse model."""

    def test_empty_response(self) -> None:
        """Test response with no cards."""
        response = CDSResponse()
        assert response.cards == []
        assert response.systemActions is None

    def test_response_with_cards(self) -> None:
        """Test response with cards."""
        card = Card(
            summary="Alert",
            indicator="info",
            source=Source(label="CDS"),
        )
        response = CDSResponse(cards=[card])
        assert len(response.cards) == 1

    def test_response_with_system_actions(self) -> None:
        """Test response with system actions."""
        action = Action(type="create", description="Create audit log")
        response = CDSResponse(
            cards=[],
            systemActions=[action],
        )
        assert response.systemActions is not None
        assert len(response.systemActions) == 1


# =============================================================================
# Feedback Model Tests
# =============================================================================


class TestOverrideReason:
    """Tests for OverrideReason model."""

    def test_with_reason(self) -> None:
        """Test override with reason coding."""
        override = OverrideReason(
            reason=Coding(code="patient-declined"),
            userComment="Patient refused medication",
        )
        assert override.reason is not None
        assert override.userComment == "Patient refused medication"

    def test_empty_override(self) -> None:
        """Test override with no fields."""
        override = OverrideReason()
        assert override.reason is None
        assert override.userComment is None


class TestAcceptedSuggestion:
    """Tests for AcceptedSuggestion model."""

    def test_valid_suggestion(self) -> None:
        """Test accepted suggestion with ID."""
        suggestion = AcceptedSuggestion(id="suggestion-123")
        assert suggestion.id == "suggestion-123"

    def test_missing_id(self) -> None:
        """Test that missing ID raises error."""
        with pytest.raises(ValidationError):
            AcceptedSuggestion()  # type: ignore


class TestFeedbackEntry:
    """Tests for FeedbackEntry model."""

    def test_accepted_feedback(self) -> None:
        """Test accepted card feedback."""
        entry = FeedbackEntry(
            card="card-uuid-123",
            outcome="accepted",
            outcomeTimestamp=datetime.now(),
        )
        assert entry.card == "card-uuid-123"
        assert entry.outcome == "accepted"

    def test_overridden_feedback(self) -> None:
        """Test overridden card feedback."""
        entry = FeedbackEntry(
            card="card-uuid-123",
            outcome="overridden",
            overrideReason=OverrideReason(userComment="Not applicable"),
            outcomeTimestamp=datetime.now(),
        )
        assert entry.outcome == "overridden"
        assert entry.overrideReason is not None

    def test_with_accepted_suggestions(self) -> None:
        """Test feedback with accepted suggestions."""
        entry = FeedbackEntry(
            card="card-uuid",
            outcome="accepted",
            acceptedSuggestions=[AcceptedSuggestion(id="sugg-1")],
            outcomeTimestamp=datetime.now(),
        )
        assert entry.acceptedSuggestions is not None
        assert len(entry.acceptedSuggestions) == 1

    def test_invalid_outcome(self) -> None:
        """Test that invalid outcome raises error."""
        with pytest.raises(ValidationError):
            FeedbackEntry(
                card="card",
                outcome="rejected",  # type: ignore
                outcomeTimestamp=datetime.now(),
            )


class TestFeedbackRequest:
    """Tests for FeedbackRequest model."""

    def test_valid_request(self) -> None:
        """Test valid feedback request."""
        entry = FeedbackEntry(
            card="card-1",
            outcome="accepted",
            outcomeTimestamp=datetime.now(),
        )
        request = FeedbackRequest(feedback=[entry])
        assert len(request.feedback) == 1

    def test_multiple_entries(self) -> None:
        """Test feedback request with multiple entries."""
        entries = [
            FeedbackEntry(card="card-1", outcome="accepted", outcomeTimestamp=datetime.now()),
            FeedbackEntry(card="card-2", outcome="overridden", outcomeTimestamp=datetime.now()),
        ]
        request = FeedbackRequest(feedback=entries)
        assert len(request.feedback) == 2

    def test_missing_feedback(self) -> None:
        """Test that missing feedback raises error."""
        with pytest.raises(ValidationError):
            FeedbackRequest()  # type: ignore
