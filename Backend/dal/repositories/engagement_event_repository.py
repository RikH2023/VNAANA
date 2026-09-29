import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import EngagementEvent as EngagementEventModel
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.ports.engagement_event_repository import (
    EngagementEventRepository as EngagementEventRepositoryPort,
)


class EngagementEventRepository(EngagementEventRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(event: EngagementEventModel) -> EngagementEvent:
        return EngagementEvent(
            id=event.id,
            user_id=event.user_id,
            session_id=event.session_id,
            story_id=event.story_id,
            article_id=event.article_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            active_duration_ms=event.active_duration_ms,
            event_metadata=event.event_metadata,
        )

    def add(self, **fields: Any) -> EngagementEvent:
        event_model = EngagementEventModel(**fields)

        self.db.add(event_model)
        self.db.flush()

        return self._to_domain(event_model)

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EngagementEvent]:
        stmt = (
            select(EngagementEventModel)
            .where(EngagementEventModel.user_id == user_id)
            .order_by(EngagementEventModel.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )

        events = self.db.scalars(stmt)

        return [self._to_domain(event) for event in events]