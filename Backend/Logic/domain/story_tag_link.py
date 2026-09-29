import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class StoryTagLink:
    story_id: uuid.UUID
    tag_id: uuid.UUID
    relevance_score: Decimal | None