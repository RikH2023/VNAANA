from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Models map onto existing tables (created by the DB owner, not by this API)."""


def utcnow() -> datetime:
    """Timezone-aware 'now', matches timestamptz columns."""
    return datetime.now(timezone.utc)