"""CDS Hooks card builder."""

import re
from typing import Any
from uuid import uuid4

from jinja2 import BaseLoader, Environment

from ..config.settings import CardTemplate, CDSServiceConfig
from ..models.response import Action, Card, CDSResponse, Link, Source, Suggestion


class CardBuilder:
    """Builds CDS Cards from CQL evaluation results."""

    def __init__(self):
        self._jinja_env = Environment(loader=BaseLoader(), autoescape=False)

    def build_response(
        self,
        service: CDSServiceConfig,
        results: dict[str, Any],
    ) -> CDSResponse:
        """Build CDS response from evaluation results.

        Args:
            service: Service configuration with card templates
            results: CQL evaluation results

        Returns:
            CDSResponse with generated cards
        """
        cards = []

        for template in service.cards:
            card = self._build_card(template, results)
            if card:
                cards.append(card)

        return CDSResponse(cards=cards)

    def _build_card(
        self,
        template: CardTemplate,
        results: dict[str, Any],
    ) -> Card | None:
        """Build a single card from template and results."""

        # Check condition if specified
        if template.condition:
            condition_result = self._evaluate_condition(template.condition, results)
            if not condition_result:
                return None

        # Build template context
        context = self._build_template_context(results)

        # Render summary
        summary = self._render_template(template.summary, context)

        # Render detail if provided
        detail = None
        if template.detail:
            detail = self._render_template(template.detail, context)

        # Build source
        source = Source(
            label=template.source,
            url=template.sourceUrl,
        )

        # Build suggestions
        suggestions = []
        for sugg_config in template.suggestions:
            suggestion = self._build_suggestion(sugg_config, context)
            if suggestion:
                suggestions.append(suggestion)

        # Build links
        links = []
        for link_config in template.links:
            link = self._build_link(link_config, context)
            if link:
                links.append(link)

        return Card(
            uuid=str(uuid4()),
            summary=summary,
            detail=detail,
            indicator=template.indicator,  # type: ignore
            source=source,
            suggestions=suggestions,
            links=links,
        )

    def _evaluate_condition(self, condition: str, results: dict[str, Any]) -> bool:
        """Evaluate a condition against results."""
        # Handle simple definition reference
        if condition in results:
            value = results[condition]
            # Skip error results
            if isinstance(value, dict) and "_error" in value:
                return False
            if isinstance(value, bool):
                return value
            if isinstance(value, list):
                return len(value) > 0
            return value is not None

        # Handle compound conditions (simple parsing)
        if " and " in condition:
            parts = condition.split(" and ")
            return all(self._evaluate_condition(p.strip(), results) for p in parts)

        if " or " in condition:
            parts = condition.split(" or ")
            return any(self._evaluate_condition(p.strip(), results) for p in parts)

        if condition.startswith("not "):
            return not self._evaluate_condition(condition[4:].strip(), results)

        # Handle comparison expressions like "Count > 0"
        match = re.match(r"(\w+)\s*(>=|<=|>|<|==|!=)\s*(\d+)", condition)
        if match:
            var_name, op, value = match.groups()
            var_value = results.get(var_name)
            if var_value is not None and isinstance(var_value, (int, float)):
                num_value = int(value)
                if op == ">":
                    return var_value > num_value
                elif op == ">=":
                    return var_value >= num_value
                elif op == "<":
                    return var_value < num_value
                elif op == "<=":
                    return var_value <= num_value
                elif op == "==":
                    return var_value == num_value
                elif op == "!=":
                    return var_value != num_value

        return False

    def _build_template_context(self, results: dict[str, Any]) -> dict[str, Any]:
        """Build Jinja2 template context from results."""
        context: dict[str, Any] = {}

        for key, value in results.items():
            if key.startswith("_"):
                continue
            context[key] = value

        # Add some convenience aliases
        if "ActiveDrugInteractions" in results:
            context["interactions"] = results["ActiveDrugInteractions"]
        if "ActiveContraindications" in results:
            context["contraindications"] = results["ActiveContraindications"]
        if "ActiveRiskAlerts" in results:
            context["alerts"] = results["ActiveRiskAlerts"]

        return context

    def _render_template(self, template_str: str, context: dict[str, Any]) -> str:
        """Render a Jinja2 template string."""
        try:
            template = self._jinja_env.from_string(template_str)
            return template.render(**context)
        except Exception:
            # Fallback: simple variable substitution
            result = template_str
            for key, value in context.items():
                placeholder = "{{" + key + "}}"
                if placeholder in result:
                    if isinstance(value, list):
                        result = result.replace(placeholder, str(len(value)))
                    else:
                        result = result.replace(placeholder, str(value))
            return result

    def _build_suggestion(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> Suggestion | None:
        """Build a suggestion from configuration."""
        label = config.get("label", "")
        if not label:
            return None

        label = self._render_template(label, context)

        actions = []
        for action_config in config.get("actions", []):
            action = Action(
                type=action_config.get("type", "create"),
                description=self._render_template(action_config.get("description", ""), context),
                resource=action_config.get("resource"),
            )
            actions.append(action)

        return Suggestion(
            label=label,
            uuid=str(uuid4()),
            isRecommended=config.get("isRecommended", False),
            actions=actions,
        )

    def _build_link(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> Link | None:
        """Build a link from configuration."""
        label = config.get("label", "")
        url = config.get("url", "")
        if not label or not url:
            return None

        label = self._render_template(label, context)
        url = self._render_template(url, context)

        return Link(
            label=label,
            url=url,
            type=config.get("type", "absolute"),
            appContext=config.get("appContext"),
        )
