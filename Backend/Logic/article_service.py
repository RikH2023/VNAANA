import uuid
from datetime import datetime, timezone
from typing import Any

from Backend.Logic.domain.article import Article
from Backend.Logic.exceptions import NotFoundError
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.provider_repository import ProviderRepository


class ArticleService:
    def __init__(
        self,
        articles: ArticleRepository,
        providers: ProviderRepository,
    ):
        self.articles = articles
        self.providers = providers

    def list_articles(
        self,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        return self.articles.list(
            provider_id=provider_id,
            language=language,
            limit=limit,
            offset=offset,
        )

    def get_article(
        self,
        article_id: uuid.UUID,
    ) -> Article:
        article = self.articles.get(article_id)

        if article is None:
            raise NotFoundError("Article", article_id)

        return article

    def ingest_article(
        self,
        data: dict[str, Any],
    ) -> tuple[Article, bool]:
        provider_id = data["provider_id"]

        if self.providers.get(provider_id) is None:
            raise NotFoundError("Provider", provider_id)

        data = {
            **data,
            "canonical_url": data["canonical_url"].strip(),
            "last_seen_at": datetime.now(timezone.utc),
        }

        return self.articles.ingest(**data)