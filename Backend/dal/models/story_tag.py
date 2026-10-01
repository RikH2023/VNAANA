import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.dal.models.base import Base

if TYPE_CHECKING:
    from Backend.dal.models.story import Story
    from Backend.dal.models.tag import Tag


class StoryTag(Base):
    __tablename__ = "story_tags"

    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
    relevance_score: Mapped[Decimal | None] = mapped_column(Numeric)

    story: Mapped["Story"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(lazy="joined")
