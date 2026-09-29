import uuid
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, Field

from Backend.Presentation.schemas.common import ORMModel, TagRead


class UserCreate(BaseModel):
    age_band: str | None = Field(default=None, examples=["18-24"])
    language: str | None = Field(default=None, max_length=5, examples=["nl"])
    region: str | None = Field(default=None, examples=["Noord-Brabant"])
    preferences: dict[str, Any] | None = None
    analytics_consent: bool = False


class UserUpdate(BaseModel):
    """Profile fields only. Consent has its own endpoint so it always gets a timestamp."""

    age_band: str | None = None
    language: str | None = Field(default=None, max_length=5)
    region: str | None = None
    preferences: dict[str, Any] | None = None


class ConsentUpdate(BaseModel):
    analytics_consent: bool


class UserRead(ORMModel):
    id: uuid.UUID
    age_band: str | None
    language: str | None
    region: str | None
    preferences: dict[str, Any] | None
    analytics_consent: bool
    consent_updated_at: datetime | None


class UserTagsUpdate(BaseModel):
    tag_ids: list[uuid.UUID] = Field(default_factory=list)


class UserTagRead(ORMModel):
    tag: TagRead
    updated_at: datetime


class EngagementEventCreate(BaseModel):
    session_id: uuid.UUID
    story_id: uuid.UUID | None = None
    article_id: uuid.UUID | None = None
    event_type: str = Field(min_length=1, max_length=50, examples=["story_open"])
    occurred_at: datetime | None = None
    active_duration_ms: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] | None = None


class EngagementEventRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    session_id: uuid.UUID
    story_id: uuid.UUID | None
    article_id: uuid.UUID | None
    event_type: str
    occurred_at: datetime
    active_duration_ms: int | None
    # The ORM attribute is event_metadata (see the model), the API field is metadata.
    metadata: dict[str, Any] | None = Field(
        validation_alias=AliasChoices("event_metadata", "metadata")
    )
