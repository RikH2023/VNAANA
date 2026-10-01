import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, String, false
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Backend.dal.models.base import Base

if TYPE_CHECKING:
    from Backend.dal.models.user_tag import UserTag


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    age_band: Mapped[str | None] = mapped_column(String)
    language: Mapped[str | None] = mapped_column(String(5))
    region: Mapped[str | None] = mapped_column(String)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # Privacy by default: no consent until the user explicitly gives it.
    analytics_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    consent_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tags: Mapped[list["UserTag"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
