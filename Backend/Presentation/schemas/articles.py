import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from Backend.Presentation.schemas.common import ORMModel


class ProviderRead(ORMModel):
    id: uuid.UUID
    name: str
    domain: str
    country_code: str | None
    reliability_status: str


class ArticleCreate(BaseModel):
    provider_id: uuid.UUID
    canonical_url: str = Field(min_length=1, examples=["https://nos.nl/artikel/123456"])
    title: str = Field(min_length=1)
    description: str | None = None
    author: str | None = None
    language: str | None = Field(default=None, max_length=5)
    published_at: datetime | None = None


class ArticleSummary(ORMModel):
    """Short version, used when an article is nested inside a story."""

    id: uuid.UUID
    title: str
    canonical_url: str
    published_at: datetime | None
    provider: ProviderRead


class ArticleRead(ORMModel):
    id: uuid.UUID
    provider: ProviderRead
    canonical_url: str
    title: str
    description: str | None
    author: str | None
    language: str | None
    published_at: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime
