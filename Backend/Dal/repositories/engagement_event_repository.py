import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.Dal.models import EngagementEvent as EngagementEventModel, EventWeight
from Backend.Dal.models.base import utcnow
from Backend.Logic.exceptions import NotFoundError
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
            ingested_at=event.ingested_at,
            active_duration_ms=event.active_duration_ms,
            event_metadata=event.event_metadata,
        )

    def add(self, **fields: Any) -> EngagementEvent:
        if self.db.get(EventWeight, fields["event_type"]) is None:
            raise NotFoundError("Event type", fields["event_type"])
        # Receipt time comes from the application, not the client or a DB default.
        fields["ingested_at"] = utcnow()
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
