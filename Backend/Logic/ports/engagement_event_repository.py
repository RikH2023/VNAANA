import uuid
from typing import Any, Protocol

from Backend.Logic.domain.engagement_event import EngagementEvent


class EngagementEventRepository(Protocol):
    def add(self, **fields: Any) -> EngagementEvent:
        ...

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EngagementEvent]:
        ...