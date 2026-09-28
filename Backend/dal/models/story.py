import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.dal.models.base import Base, utcnow

if TYPE_CHECKING:
    from Backend.dal.models.story_article import StoryArticle
    from Backend.dal.models.story_tag import StoryTag


class StoryStatus(str, enum.Enum):
    # NOTE: the diagram only shows the type name (story_status), not its values.
    # Change these to whatever the team agreed on.
    draft = "draft"
    published = "published"
    archived = "archived"


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StoryStatus] = mapped_column(
        # values_callable stores "draft", not the member name "DRAFT"
        Enum(StoryStatus, name="story_status", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=StoryStatus.draft,
    )
    first_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    tags: Mapped[list["StoryTag"]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )
    articles: Mapped[list["StoryArticle"]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )
