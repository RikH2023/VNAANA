import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class EngagementEvent:
    id: uuid.UUID
    user_id: uuid.UUID | None
    session_id: uuid.UUID
    story_id: uuid.UUID | None
    article_id: uuid.UUID | None
    event_type: str
    occurred_at: datetime
    active_duration_ms: int | None
    event_metadata: dict[str, Any] | None