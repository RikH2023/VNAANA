import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from Backend.Dal.models.base import Base


class StoryReaction(Base):
    """A user's current like/dislike on a story (design doc D2).

    One row per user and story; the latest tap overwrites it, unliking
    deletes it. NOTE: must match the migration Hanh is writing. If her
    commit brings its own model, keep hers and remove this file.
    """

    __tablename__ = "story_reactions"
    __table_args__ = (
        CheckConstraint("reaction IN ('like', 'dislike')", name="ck_story_reactions_reaction"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True
    )
    reaction: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
