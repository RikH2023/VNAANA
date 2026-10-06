import uuid
from abc import ABC, abstractmethod
from typing import Any

from Backend.Logic.domain.article import Article


class ArticleRepository(ABC):

    @abstractmethod
    def get(
        self,
        article_id: uuid.UUID,
    ) -> Article | None:
        ...

    @abstractmethod
    def get_by_canonical_url(
        self,
        canonical_url: str,
    ) -> Article | None:
        ...

    @abstractmethod
    def list(
        self,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        ...

    @abstractmethod
    def add(
        self,
        **fields: Any,
    ) -> Article:
        ...

    @abstractmethod
    def ingest(
        self,
        **fields: Any,
    ) -> tuple[Article, bool]:
        ...

    @abstractmethod
    def update(
        self,
        article: Article,
        **fields: Any,
    ) -> Article:
        ...