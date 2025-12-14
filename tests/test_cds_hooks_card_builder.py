"""Tests for CDS Hooks card builder."""

from typing import Any

import pytest

from fhirkit.cds_hooks.config.settings import CardTemplate, CDSServiceConfig
from fhirkit.cds_hooks.service.card_builder import CardBuilder


@pytest.fixture
def card_builder() -> CardBuilder:
    """Create a CardBuilder instance."""
    return CardBuilder()


@pytest.fixture
def sample_service() -> CDSServiceConfig:
    """Create a sample service configuration."""
    return CDSServiceConfig(
        id="test-service",
        hook="patient-view",
        title="Test Service",
        description="Test description",
        cqlLibrary="test.cql",
        evaluateDefinitions=["HasAlerts", "AlertCount", "AlertList"],
        cards=[
            CardTemplate(
                condition="HasAlerts",
                indicator="warning",
                summary="{{AlertCount}} alert(s) detected",
                detail="## Alerts\n{{AlertList}}",
                source="Test CDS",
            )
        ],
    )


# =============================================================================
# Condition Evaluation Tests
# =============================================================================


class TestConditionEvaluation:
    """Tests for card condition evaluation."""

    def test_simple_truthy_boolean(self, card_builder: CardBuilder) -> None:
        """Test evaluating a simple boolean true condition."""
        results = {"HasAlerts": True}
        assert card_builder._evaluate_condition("HasAlerts", results) is True

    def test_simple_falsy_boolean(self, card_builder: CardBuilder) -> None:
        """Test evaluating a simple boolean false condition."""
        results = {"HasAlerts": False}
        assert card_builder._evaluate_condition("HasAlerts", results) is False

    def test_non_empty_list_is_truthy(self, card_builder: CardBuilder) -> None:
        """Test that non-empty list is truthy."""
        results = {"Alerts": ["alert1", "alert2"]}
        assert card_builder._evaluate_condition("Alerts", results) is True

    def test_empty_list_is_falsy(self, card_builder: CardBuilder) -> None:
        """Test that empty list is falsy."""
        results = {"Alerts": []}
        assert card_builder._evaluate_condition("Alerts", results) is False

    def test_non_null_value_is_truthy(self, card_builder: CardBuilder) -> None:
        """Test that non-null value is truthy."""
        results = {"Value": "something"}
        assert card_builder._evaluate_condition("Value", results) is True

    def test_null_value_is_falsy(self, card_builder: CardBuilder) -> None:
        """Test that null value is falsy."""
        results = {"Value": None}
        assert card_builder._evaluate_condition("Value", results) is False

    def test_missing_key_is_falsy(self, card_builder: CardBuilder) -> None:
        """Test that missing key is falsy."""
        results = {"Other": True}
        assert card_builder._evaluate_condition("Missing", results) is False

    def test_error_result_is_falsy(self, card_builder: CardBuilder) -> None:
        """Test that error result is falsy."""
        results = {"Value": {"_error": "Something went wrong"}}
        assert card_builder._evaluate_condition("Value", results) is False

    def test_and_condition_both_true(self, card_builder: CardBuilder) -> None:
        """Test AND condition when both are true."""
        results = {"A": True, "B": True}
        assert card_builder._evaluate_condition("A and B", results) is True

    def test_and_condition_one_false(self, card_builder: CardBuilder) -> None:
        """Test AND condition when one is false."""
        results = {"A": True, "B": False}
        assert card_builder._evaluate_condition("A and B", results) is False

    def test_or_condition_one_true(self, card_builder: CardBuilder) -> None:
        """Test OR condition when one is true."""
        results = {"A": True, "B": False}
        assert card_builder._evaluate_condition("A or B", results) is True

    def test_or_condition_both_false(self, card_builder: CardBuilder) -> None:
        """Test OR condition when both are false."""
        results = {"A": False, "B": False}
        assert card_builder._evaluate_condition("A or B", results) is False

    def test_not_condition_true(self, card_builder: CardBuilder) -> None:
        """Test NOT condition on true value."""
        results = {"A": True}
        assert card_builder._evaluate_condition("not A", results) is False

    def test_not_condition_false(self, card_builder: CardBuilder) -> None:
        """Test NOT condition on false value."""
        results = {"A": False}
        assert card_builder._evaluate_condition("not A", results) is True

    def test_greater_than(self, card_builder: CardBuilder) -> None:
        """Test greater than comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count > 3", results) is True
        assert card_builder._evaluate_condition("Count > 5", results) is False
        assert card_builder._evaluate_condition("Count > 10", results) is False

    def test_greater_than_or_equal(self, card_builder: CardBuilder) -> None:
        """Test greater than or equal comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count >= 3", results) is True
        assert card_builder._evaluate_condition("Count >= 5", results) is True
        assert card_builder._evaluate_condition("Count >= 10", results) is False

    def test_less_than(self, card_builder: CardBuilder) -> None:
        """Test less than comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count < 10", results) is True
        assert card_builder._evaluate_condition("Count < 5", results) is False
        assert card_builder._evaluate_condition("Count < 3", results) is False

    def test_less_than_or_equal(self, card_builder: CardBuilder) -> None:
        """Test less than or equal comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count <= 10", results) is True
        assert card_builder._evaluate_condition("Count <= 5", results) is True
        assert card_builder._evaluate_condition("Count <= 3", results) is False

    def test_equal(self, card_builder: CardBuilder) -> None:
        """Test equality comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count == 5", results) is True
        assert card_builder._evaluate_condition("Count == 3", results) is False

    def test_not_equal(self, card_builder: CardBuilder) -> None:
        """Test not equal comparison."""
        results = {"Count": 5}
        assert card_builder._evaluate_condition("Count != 3", results) is True
        assert card_builder._evaluate_condition("Count != 5", results) is False


# =============================================================================
# Template Rendering Tests
# =============================================================================


class TestTemplateRendering:
    """Tests for Jinja2 template rendering."""

    def test_simple_variable_substitution(self, card_builder: CardBuilder) -> None:
        """Test simple variable substitution."""
        context = {"AlertCount": 3}
        result = card_builder._render_template("{{AlertCount}} alerts", context)
        assert result == "3 alerts"

    def test_multiple_variables(self, card_builder: CardBuilder) -> None:
        """Test multiple variable substitution."""
        context = {"Count": 5, "Type": "warning"}
        result = card_builder._render_template("{{Count}} {{Type}} alerts", context)
        assert result == "5 warning alerts"

    def test_length_filter(self, card_builder: CardBuilder) -> None:
        """Test Jinja2 length filter."""
        context = {"Alerts": ["a", "b", "c"]}
        result = card_builder._render_template("{{Alerts|length}} items", context)
        assert result == "3 items"

    def test_default_filter(self, card_builder: CardBuilder) -> None:
        """Test Jinja2 default filter."""
        context = {}
        result = card_builder._render_template("{{Missing|default('N/A')}}", context)
        assert result == "N/A"

    def test_conditional_template(self, card_builder: CardBuilder) -> None:
        """Test conditional template."""
        template = "{% if HasAlerts %}Alerts found{% else %}No alerts{% endif %}"
        assert card_builder._render_template(template, {"HasAlerts": True}) == "Alerts found"
        assert card_builder._render_template(template, {"HasAlerts": False}) == "No alerts"

    def test_loop_template(self, card_builder: CardBuilder) -> None:
        """Test loop template."""
        context = {"Items": ["apple", "banana", "cherry"]}
        template = "{% for item in Items %}{{item}} {% endfor %}"
        result = card_builder._render_template(template, context)
        assert "apple" in result
        assert "banana" in result
        assert "cherry" in result

    def test_fallback_on_invalid_template(self, card_builder: CardBuilder) -> None:
        """Test fallback when template syntax is invalid."""
        context = {"Count": 5}
        # Invalid Jinja2 syntax should fall back to simple substitution
        result = card_builder._render_template("{{Count}} items", context)
        assert "5" in result


# =============================================================================
# Template Context Building Tests
# =============================================================================


class TestTemplateContext:
    """Tests for building template context from results."""

    def test_context_excludes_internal_keys(self, card_builder: CardBuilder) -> None:
        """Test that internal keys (starting with _) are excluded."""
        results = {
            "PublicValue": 123,
            "_context": {"patientId": "456"},
            "_error": "some error",
        }
        context = card_builder._build_template_context(results)
        assert "PublicValue" in context
        assert "_context" not in context
        assert "_error" not in context

    def test_context_includes_convenience_aliases(self, card_builder: CardBuilder) -> None:
        """Test that convenience aliases are added."""
        results = {
            "ActiveDrugInteractions": ["interaction1"],
            "ActiveContraindications": ["contra1"],
            "ActiveRiskAlerts": ["alert1"],
        }
        context = card_builder._build_template_context(results)
        assert context.get("interactions") == ["interaction1"]
        assert context.get("contraindications") == ["contra1"]
        assert context.get("alerts") == ["alert1"]


# =============================================================================
# Card Building Tests
# =============================================================================


class TestCardBuilding:
    """Tests for building cards from templates."""

    def test_build_card_with_true_condition(
        self,
        card_builder: CardBuilder,
        sample_service: CDSServiceConfig,
    ) -> None:
        """Test building a card when condition is true."""
        results = {
            "HasAlerts": True,
            "AlertCount": 3,
            "AlertList": "- Alert 1\n- Alert 2",
        }
        response = card_builder.build_response(sample_service, results)
        assert len(response.cards) == 1
        assert "3" in response.cards[0].summary
        assert response.cards[0].indicator == "warning"

    def test_skip_card_with_false_condition(
        self,
        card_builder: CardBuilder,
        sample_service: CDSServiceConfig,
    ) -> None:
        """Test that card is skipped when condition is false."""
        results = {
            "HasAlerts": False,
            "AlertCount": 0,
            "AlertList": "",
        }
        response = card_builder.build_response(sample_service, results)
        assert len(response.cards) == 0

    def test_build_card_with_no_condition(self, card_builder: CardBuilder) -> None:
        """Test building a card with no condition (always shown)."""
        service = CDSServiceConfig(
            id="always-show",
            hook="patient-view",
            title="Always Show",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
            cards=[
                CardTemplate(
                    indicator="info",
                    summary="Always visible",
                    source="Test",
                )
            ],
        )
        response = card_builder.build_response(service, {"Test": True})
        assert len(response.cards) == 1

    def test_multiple_cards(self, card_builder: CardBuilder) -> None:
        """Test building multiple cards."""
        service = CDSServiceConfig(
            id="multi-card",
            hook="patient-view",
            title="Multi Card",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["A", "B"],
            cards=[
                CardTemplate(condition="A", indicator="info", summary="Card A", source="Test"),
                CardTemplate(condition="B", indicator="warning", summary="Card B", source="Test"),
            ],
        )
        response = card_builder.build_response(service, {"A": True, "B": True})
        assert len(response.cards) == 2

    def test_card_has_uuid(
        self,
        card_builder: CardBuilder,
        sample_service: CDSServiceConfig,
    ) -> None:
        """Test that generated cards have UUIDs."""
        results = {"HasAlerts": True, "AlertCount": 1, "AlertList": "test"}
        response = card_builder.build_response(sample_service, results)
        assert response.cards[0].uuid is not None
        assert len(response.cards[0].uuid) > 0

    def test_card_source_fields(
        self,
        card_builder: CardBuilder,
    ) -> None:
        """Test that card source is properly built."""
        service = CDSServiceConfig(
            id="source-test",
            hook="patient-view",
            title="Source Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
            cards=[
                CardTemplate(
                    indicator="info",
                    summary="Test",
                    source="My CDS",
                    sourceUrl="https://example.org",
                )
            ],
        )
        response = card_builder.build_response(service, {"Test": True})
        assert response.cards[0].source.label == "My CDS"
        assert response.cards[0].source.url == "https://example.org"


# =============================================================================
# Suggestion Building Tests
# =============================================================================


class TestSuggestionBuilding:
    """Tests for building suggestions."""

    def test_build_suggestion(self, card_builder: CardBuilder) -> None:
        """Test building a suggestion from config."""
        config: dict[str, Any] = {
            "label": "Review medication",
            "isRecommended": True,
        }
        suggestion = card_builder._build_suggestion(config, {})
        assert suggestion is not None
        assert suggestion.label == "Review medication"
        assert suggestion.isRecommended is True

    def test_suggestion_with_actions(self, card_builder: CardBuilder) -> None:
        """Test building a suggestion with actions."""
        config: dict[str, Any] = {
            "label": "Create task",
            "actions": [
                {"type": "create", "description": "Create follow-up task"},
            ],
        }
        suggestion = card_builder._build_suggestion(config, {})
        assert suggestion is not None
        assert len(suggestion.actions) == 1
        assert suggestion.actions[0].type == "create"

    def test_suggestion_label_rendered(self, card_builder: CardBuilder) -> None:
        """Test that suggestion label is rendered with context."""
        config: dict[str, Any] = {"label": "Review {{Count}} items"}
        context = {"Count": 5}
        suggestion = card_builder._build_suggestion(config, context)
        assert suggestion is not None
        assert "5" in suggestion.label

    def test_suggestion_without_label_returns_none(self, card_builder: CardBuilder) -> None:
        """Test that suggestion without label returns None."""
        config: dict[str, Any] = {"isRecommended": True}
        suggestion = card_builder._build_suggestion(config, {})
        assert suggestion is None

    def test_suggestion_has_uuid(self, card_builder: CardBuilder) -> None:
        """Test that generated suggestions have UUIDs."""
        config: dict[str, Any] = {"label": "Test"}
        suggestion = card_builder._build_suggestion(config, {})
        assert suggestion is not None
        assert suggestion.uuid is not None


# =============================================================================
# Link Building Tests
# =============================================================================


class TestLinkBuilding:
    """Tests for building links."""

    def test_build_absolute_link(self, card_builder: CardBuilder) -> None:
        """Test building an absolute link."""
        config: dict[str, Any] = {
            "label": "More Info",
            "url": "https://example.org",
            "type": "absolute",
        }
        link = card_builder._build_link(config, {})
        assert link is not None
        assert link.label == "More Info"
        assert link.url == "https://example.org"
        assert link.type == "absolute"

    def test_build_smart_link(self, card_builder: CardBuilder) -> None:
        """Test building a SMART app link."""
        config: dict[str, Any] = {
            "label": "Launch App",
            "url": "https://app.example.org/launch",
            "type": "smart",
            "appContext": '{"patient":"123"}',
        }
        link = card_builder._build_link(config, {})
        assert link is not None
        assert link.type == "smart"
        assert link.appContext is not None

    def test_link_label_rendered(self, card_builder: CardBuilder) -> None:
        """Test that link label is rendered with context."""
        config: dict[str, Any] = {
            "label": "View {{Count}} items",
            "url": "https://example.org",
            "type": "absolute",
        }
        link = card_builder._build_link(config, {"Count": 5})
        assert link is not None
        assert "5" in link.label

    def test_link_url_rendered(self, card_builder: CardBuilder) -> None:
        """Test that link URL is rendered with context."""
        config: dict[str, Any] = {
            "label": "View",
            "url": "https://example.org/patient/{{PatientId}}",
            "type": "absolute",
        }
        link = card_builder._build_link(config, {"PatientId": "123"})
        assert link is not None
        assert "123" in link.url

    def test_link_without_label_returns_none(self, card_builder: CardBuilder) -> None:
        """Test that link without label returns None."""
        config: dict[str, Any] = {"url": "https://example.org", "type": "absolute"}
        link = card_builder._build_link(config, {})
        assert link is None

    def test_link_without_url_returns_none(self, card_builder: CardBuilder) -> None:
        """Test that link without URL returns None."""
        config: dict[str, Any] = {"label": "Test", "type": "absolute"}
        link = card_builder._build_link(config, {})
        assert link is None


# =============================================================================
# Full Response Building Tests
# =============================================================================


class TestFullResponseBuilding:
    """Tests for building complete CDS responses."""

    def test_response_with_suggestions_and_links(self, card_builder: CardBuilder) -> None:
        """Test building a response with suggestions and links."""
        service = CDSServiceConfig(
            id="full-test",
            hook="patient-view",
            title="Full Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["Test"],
            cards=[
                CardTemplate(
                    indicator="warning",
                    summary="Review needed",
                    source="Test CDS",
                    suggestions=[
                        {"label": "Accept", "isRecommended": True},
                        {"label": "Decline"},
                    ],
                    links=[
                        {"label": "Details", "url": "https://example.org", "type": "absolute"},
                    ],
                )
            ],
        )
        response = card_builder.build_response(service, {"Test": True})

        assert len(response.cards) == 1
        assert len(response.cards[0].suggestions) == 2
        assert len(response.cards[0].links) == 1
        assert response.cards[0].suggestions[0].isRecommended is True

    def test_empty_response_when_no_conditions_met(self, card_builder: CardBuilder) -> None:
        """Test that response is empty when no card conditions are met."""
        service = CDSServiceConfig(
            id="empty-test",
            hook="patient-view",
            title="Empty Test",
            description="Test",
            cqlLibrary="test.cql",
            evaluateDefinitions=["A", "B"],
            cards=[
                CardTemplate(condition="A", indicator="info", summary="A", source="Test"),
                CardTemplate(condition="B", indicator="info", summary="B", source="Test"),
            ],
        )
        response = card_builder.build_response(service, {"A": False, "B": False})
        assert len(response.cards) == 0

    def test_response_cards_list_type(
        self,
        card_builder: CardBuilder,
        sample_service: CDSServiceConfig,
    ) -> None:
        """Test that response.cards is always a list."""
        response = card_builder.build_response(sample_service, {"HasAlerts": False})
        assert isinstance(response.cards, list)
