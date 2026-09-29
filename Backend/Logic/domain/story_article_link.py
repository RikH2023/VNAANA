import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class StoryArticleLink:
    story_id: uuid.UUID
    article_id: uuid.UUID
    similarity_score: Decimal | None
    is_primary: bool
    added_at: datetime