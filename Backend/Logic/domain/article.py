import uuid

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RawArticle:
    title: str
    url: str
    description: str | None
    author: str | None
    language: str | None
    published_at: datetime | None
    provider_id: uuid.UUID

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