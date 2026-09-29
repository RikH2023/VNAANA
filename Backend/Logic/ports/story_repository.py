import uuid
from decimal import Decimal
from typing import Any, Protocol

from Backend.Logic.domain.story import Story, StoryStatus
from Backend.Logic.domain.story_article_link import StoryArticleLink


class StoryRepository(Protocol):
    def get(self, story_id: uuid.UUID) -> Story | None:
        ...

    def list(
        self,
        *,
        status: StoryStatus | None = None,
        tag_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Story]:
        ...

    def add(self, **fields: Any) -> Story:
        ...

    def update(self, story: Story, **fields: Any) -> Story:
        ...

    def replace_tags(
        self,
        story: Story,
        tags: dict[uuid.UUID, Decimal | None],
    ) -> None:
        ...

    def get_article_link(
        self,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
    ) -> StoryArticleLink | None:
        ...

    def add_article_link(
        self,
        *,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
        similarity_score: Decimal | None = None,
        is_primary: bool = False,
    ) -> StoryArticleLink:
        ...

    def clear_primary(self, story_id: uuid.UUID) -> None:
        ...

    def remove_article_link(
        self,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
    ) -> None:
        ...