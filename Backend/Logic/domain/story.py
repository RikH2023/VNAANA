import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class StoryStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


@dataclass
class Story:
    id: uuid.UUID
    title: str
    summary: str | None
    context: str | None
    status: StoryStatus
    first_published_at: datetime | None
    last_updated_at: datetime