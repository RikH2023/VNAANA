import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import EngagementEvent


class EngagementEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, **fields: Any) -> EngagementEvent:
        event = EngagementEvent(**fields)
        self.db.add(event)
        self.db.flush()
        return event

    def list_for_user(
        self, user_id: uuid.UUID, *, limit: int = 50, offset: int = 0
    ) -> list[EngagementEvent]:
        stmt = (
            select(EngagementEvent)
            .where(EngagementEvent.user_id == user_id)
            .order_by(EngagementEvent.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))
