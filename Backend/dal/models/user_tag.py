import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.dal.models.base import Base, utcnow

if TYPE_CHECKING:
    from Backend.dal.models.tag import Tag
    from Backend.dal.models.user import User


class UserTag(Base):
    """A user's interest in a tag (picked at onboarding, adjusted later)."""

    __tablename__ = "user_tags"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(lazy="joined")
