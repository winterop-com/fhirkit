"""CDS Hooks feedback endpoint models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .response import Coding


class OverrideReason(BaseModel):
    """Reason for overriding a card."""

    reason: Coding | None = None
    userComment: str | None = Field(None)

    model_config = {"populate_by_name": True}


class AcceptedSuggestion(BaseModel):
    """Reference to an accepted suggestion."""

    id: str


class FeedbackEntry(BaseModel):
    """Single feedback entry for a card.

    See: https://cds-hooks.hl7.org/2.0/#feedback
    """

    card: str = Field(..., description="UUID of the card")
    outcome: Literal["accepted", "overridden"] = Field(
        ...,
        description="User's action on the card",
    )
    acceptedSuggestions: list[AcceptedSuggestion] | None = Field(None)
    overrideReason: OverrideReason | None = Field(None)
    outcomeTimestamp: datetime = Field(...)

    model_config = {"populate_by_name": True}


class FeedbackRequest(BaseModel):
    """Feedback request body.

    See: https://cds-hooks.hl7.org/2.0/#feedback
    """

    feedback: list[FeedbackEntry]
