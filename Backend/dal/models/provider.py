import uuid
from datetime import datetime

from sqlalchemy import CHAR, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from Backend.dal.models.base import Base, utcnow


class Provider(Base):
    """A news source (NOS, BBC, ...)."""

    __tablename__ = "providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    country_code: Mapped[str | None] = mapped_column(CHAR(2))
    reliability_status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
