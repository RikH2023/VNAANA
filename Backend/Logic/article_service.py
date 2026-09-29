import uuid
from datetime import datetime, timezone
from typing import Any

from Backend.Logic.domain.article import Article
from Backend.Logic.exceptions import NotFoundError
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.provider_repository import ProviderRepository


class ArticleService:
    def list_articles(
        self,
        articles: ArticleRepository,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        return articles.list(
            provider_id=provider_id,
            language=language,
            limit=limit,
            offset=offset,
        )

    def get_article(
        self,
        articles: ArticleRepository,
        article_id: uuid.UUID,
    ) -> Article:
        article = articles.get(article_id)

        if article is None:
            raise NotFoundError("Article", article_id)

        return article

    def ingest_article(
        self,
        articles: ArticleRepository,
        providers: ProviderRepository,
        data: dict[str, Any],
    ) -> tuple[Article, bool]:
        """Insert an article or refresh an existing article.

        The scraper may encounter the same article on multiple runs.
        If the canonical URL already exists, the existing article is
        refreshed instead of creating a duplicate.

        Returns:
            tuple[Article, bool]:
                The article and whether it was newly created.
        """
        provider_id = data["provider_id"]

        if providers.get(provider_id) is None:
            raise NotFoundError("Provider", provider_id)

        data["canonical_url"] = data["canonical_url"].strip()

        existing = articles.get_by_canonical_url(data["canonical_url"])

        if existing is None:
            article = articles.add(**data)
            created = True
        else:
            changes = {
                key: value
                for key, value in data.items()
                if value is not None and key != "canonical_url"
            }

            article = articles.update(
                existing,
                **changes,
                last_seen_at=datetime.now(timezone.utc),
            )
            created = False

        return article, created