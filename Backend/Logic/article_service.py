import uuid
from typing import Any

from sqlalchemy.orm import Session

from Backend.dal.models import Article
from Backend.dal.models.base import utcnow
from Backend.dal.repositories import ArticleRepository, ProviderRepository
from Backend.logic.exceptions import NotFoundError


class ArticleService:
    def __init__(self, db: Session):
        self.db = db
        self.articles = ArticleRepository(db)
        self.providers = ProviderRepository(db)

    def list_articles(
        self,
        provider_id: uuid.UUID | None,
        language: str | None,
        limit: int,
        offset: int,
    ) -> list[Article]:
        return self.articles.list(
            provider_id=provider_id, language=language, limit=limit, offset=offset
        )

    def get_article(self, article_id: uuid.UUID) -> Article:
        article = self.articles.get(article_id)
        if article is None:
            raise NotFoundError("Article", article_id)
        return article

    def ingest_article(self, data: dict[str, Any]) -> tuple[Article, bool]:
        """Insert an article, or refresh it if the canonical_url is already known.

        The scraper will see the same article on every run, so a repeat is not
        an error: we bump last_seen_at and update the content fields instead.
        Returns (article, created).
        """
        if self.providers.get(data["provider_id"]) is None:
            raise NotFoundError("Provider", data["provider_id"])

        data["canonical_url"] = data["canonical_url"].strip()
        existing = self.articles.get_by_canonical_url(data["canonical_url"])

        if existing is None:
            article = self.articles.add(**data)
            created = True
        else:
            # Never overwrite a known value with an empty one.
            changes = {k: v for k, v in data.items() if v is not None and k != "canonical_url"}
            article = self.articles.update(existing, **changes, last_seen_at=utcnow())
            created = False

        self.db.commit()
        return article, created
