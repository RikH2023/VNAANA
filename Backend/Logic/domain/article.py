import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    id: uuid.UUID
    provider_id: uuid.UUID
    canonical_url: str
    title: str
    description: str | None
    author: str | None
    language: str | None
    published_at: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime