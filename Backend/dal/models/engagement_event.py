import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from Backend.dal.models.base import Base, utcnow


class EngagementEvent(Base):
    __tablename__ = "engagement_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Nullable in the diagram, so anonymous (not logged in) events are possible.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    story_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id")
    )
    article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id")
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    active_duration_ms: Mapped[int | None] = mapped_column(Integer)
    # "metadata" is reserved on SQLAlchemy models (Base.metadata holds the table
    # definitions), so the Python attribute is event_metadata while the DB
    # column keeps the name "metadata".
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
