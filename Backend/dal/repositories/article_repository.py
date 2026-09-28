import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import Article


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, article_id: uuid.UUID) -> Article | None:
        return self.db.get(Article, article_id)

    def get_by_canonical_url(self, canonical_url: str) -> Article | None:
        stmt = select(Article).where(Article.canonical_url == canonical_url)
        return self.db.scalars(stmt).first()

    def list(
        self,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        stmt = select(Article)
        if provider_id is not None:
            stmt = stmt.where(Article.provider_id == provider_id)
        if language is not None:
            stmt = stmt.where(Article.language == language)
        stmt = (
            stmt.order_by(Article.published_at.desc().nulls_last(), Article.first_seen_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))

    def add(self, **fields: Any) -> Article:
        article = Article(**fields)
        self.db.add(article)
        self.db.flush()
        return article

    def update(self, article: Article, **fields: Any) -> Article:
        for key, value in fields.items():
            setattr(article, key, value)
        self.db.flush()
        return article
