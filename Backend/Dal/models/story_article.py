import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, func, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.Dal.models.base import Base

if TYPE_CHECKING:
    from Backend.Dal.models.article import Article
    from Backend.Dal.models.story import Story


class StoryArticle(Base):
    """Links an article (one source's coverage) to a story (the event)."""

    __tablename__ = "story_articles"

    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    similarity_score: Mapped[Decimal | None] = mapped_column(Numeric)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    story: Mapped["Story"] = relationship(back_populates="articles")
    article: Mapped["Article"] = relationship(back_populates="stories", lazy="joined")
