import uuid
from typing import Any, Protocol

from Backend.Logic.domain.article import Article


class ArticleRepository(Protocol):
    def get(self, article_id: uuid.UUID) -> Article | None:
        ...

    def get_by_canonical_url(self, canonical_url: str) -> Article | None:
        ...

    def list(
        self,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        ...

    def add(self, **fields: Any) -> Article:
        ...

    def update(self, article: Article, **fields: Any) -> Article:
        ...