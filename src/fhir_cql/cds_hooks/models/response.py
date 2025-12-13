"""CDS Hooks service response models."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class Coding(BaseModel):
    """FHIR Coding element."""

    system: str | None = None
    code: str | None = None
    display: str | None = None


class Source(BaseModel):
    """Card source information.

    See: https://cds-hooks.hl7.org/2.0/#card-attributes
    """

    label: str = Field(..., description="Short display label")
    url: str | None = None
    icon: str | None = None
    topic: Coding | None = None


class Action(BaseModel):
    """Suggestion action to modify EHR state.

    See: https://cds-hooks.hl7.org/2.0/#action
    """

    type: Literal["create", "update", "delete"] = Field(
        ...,
        description="Type of action",
    )
    description: str = Field(
        ...,
        description="Human-readable action description",
    )
    resource: dict[str, Any] | None = Field(
        None,
        description="FHIR resource for create/update",
    )
    resourceId: str | None = Field(
        None,
        description="Resource ID for delete",
    )

    model_config = {"populate_by_name": True}


class Suggestion(BaseModel):
    """Suggested action for the user.

    See: https://cds-hooks.hl7.org/2.0/#suggestion
    """

    label: str = Field(
        ...,
        description="Human-readable label (<= 80 chars)",
    )
    uuid: str | None = None
    isRecommended: bool | None = Field(None)
    actions: list[Action] = Field(default_factory=list)

    @field_validator("label")
    @classmethod
    def validate_label_length(cls, v: str) -> str:
        if len(v) > 80:
            return v[:77] + "..."
        return v

    model_config = {"populate_by_name": True}


class Link(BaseModel):
    """Link to external resource or SMART app.

    See: https://cds-hooks.hl7.org/2.0/#link
    """

    label: str = Field(..., description="Link text")
    url: str = Field(..., description="Target URL")
    type: Literal["absolute", "smart"] = Field(
        ...,
        description="Link type",
    )
    appContext: str | None = Field(None)

    model_config = {"populate_by_name": True}


class Card(BaseModel):
    """CDS decision support card.

    See: https://cds-hooks.hl7.org/2.0/#cds-service-response
    """

    uuid: str | None = None
    summary: str = Field(
        ...,
        description="One-line summary (<= 140 chars)",
    )
    detail: str | None = Field(
        None,
        description="Detailed markdown content",
    )
    indicator: Literal["info", "warning", "critical"] = Field(
        ...,
        description="Card urgency indicator",
    )
    source: Source = Field(
        ...,
        description="Source of the decision support",
    )
    suggestions: list[Suggestion] = Field(default_factory=list)
    selectionBehavior: Literal["at-most-one", "any"] | None = Field(None)
    overrideReasons: list[Coding] | None = Field(None)
    links: list[Link] = Field(default_factory=list)

    @field_validator("summary")
    @classmethod
    def validate_summary_length(cls, v: str) -> str:
        if len(v) > 140:
            return v[:137] + "..."
        return v

    model_config = {"populate_by_name": True}


class CDSResponse(BaseModel):
    """CDS Service response.

    See: https://cds-hooks.hl7.org/2.0/#http-response
    """

    cards: list[Card] = Field(default_factory=list)
    systemActions: list[Action] | None = Field(None)

    model_config = {"populate_by_name": True}
