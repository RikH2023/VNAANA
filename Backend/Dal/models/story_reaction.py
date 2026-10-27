import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.Dal.models.base import Base

if TYPE_CHECKING: 
    from Backend.Dal.models.user import User
    from Backend.Dal.models.story import Story

class StoryReaction(Base):
    __tablename__ = "story_reactions"

    __table_args__ = (
        CheckConstraint(
            "reaction IN ('like', 'dislike')",
            name="ck_story_reactions_reaction",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stories.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    reaction: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship()
    story: Mapped["Story"] = relationship()