import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.dal.models.base import Base, utcnow

if TYPE_CHECKING:
    from Backend.dal.models.article import Article
    from Backend.dal.models.story import Story


class StoryArticle(Base):
    """Links an article (one source's coverage) to a story (the event)."""

    __tablename__ = "story_articles"

    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id"), primary_key=True
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), primary_key=True
    )
    similarity_score: Mapped[Decimal | None] = mapped_column(Numeric)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    story: Mapped["Story"] = relationship(back_populates="articles")
    article: Mapped["Article"] = relationship(back_populates="stories", lazy="joined")
