import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from Backend.Logic.domain.story import StoryStatus
from Backend.Presentation.schemas.articles import ArticleSummary
from Backend.Presentation.schemas.common import ORMModel, TagRead


class StoryCreate(BaseModel):
    title: str = Field(min_length=1)
    summary: str | None = None
    context: str | None = None
    status: StoryStatus = StoryStatus.draft


class StoryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    context: str | None = None
    status: StoryStatus | None = None


class StoryTagInput(BaseModel):
    tag_id: uuid.UUID
    relevance_score: float | None = Field(default=None, ge=0, le=1)


class StoryTagsUpdate(BaseModel):
    tags: list[StoryTagInput] = Field(default_factory=list)


class StoryArticleLink(BaseModel):
    article_id: uuid.UUID
    similarity_score: float | None = Field(default=None, ge=0, le=1)
    is_primary: bool = False


class StoryTagRead(ORMModel):
    tag: TagRead
    relevance_score: float | None


class StoryArticleRead(ORMModel):
    article: ArticleSummary
    similarity_score: float | None
    is_primary: bool
    added_at: datetime


class StoryListItem(ORMModel):
    id: uuid.UUID
    title: str
    summary: str | None
    status: StoryStatus
    first_published_at: datetime | None
    last_updated_at: datetime


class StoryRead(StoryListItem):
    context: str | None
    tags: list[StoryTagRead]
    articles: list[StoryArticleRead]
