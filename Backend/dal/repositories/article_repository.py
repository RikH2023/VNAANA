import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import Article as ArticleModel
from Backend.Logic.domain.article import Article
from Backend.Logic.ports.article_repository import ArticleRepository as ArticleRepositoryPort


class ArticleRepository(ArticleRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(article: ArticleModel) -> Article:
        return Article(
            id=article.id,
            provider_id=article.provider_id,
            canonical_url=article.canonical_url,
            title=article.title,
            description=article.description,
            author=article.author,
            language=article.language,
            published_at=article.published_at,
            first_seen_at=article.first_seen_at,
            last_seen_at=article.last_seen_at,
        )

    def get(self, article_id: uuid.UUID) -> Article | None:
        article = self.db.get(ArticleModel, article_id)

        if article is None:
            return None

        return self._to_domain(article)

    def get_by_canonical_url(self, canonical_url: str) -> Article | None:
        stmt = select(ArticleModel).where(
            ArticleModel.canonical_url == canonical_url
        )

        article = self.db.scalars(stmt).first()

        if article is None:
            return None

        return self._to_domain(article)

    def list(
        self,
        *,
        provider_id: uuid.UUID | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        stmt = select(ArticleModel)

        if provider_id is not None:
            stmt = stmt.where(ArticleModel.provider_id == provider_id)

        if language is not None:
            stmt = stmt.where(ArticleModel.language == language)

        stmt = (
            stmt
            .order_by(
                ArticleModel.published_at.desc().nulls_last(),
                ArticleModel.first_seen_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        articles = self.db.scalars(stmt)

        return [self._to_domain(article) for article in articles]

    def add(self, **fields: Any) -> Article:
        article_model = ArticleModel(**fields)

        self.db.add(article_model)
        self.db.flush()

        return self._to_domain(article_model)

    def update(self, article: Article, **fields: Any) -> Article:
        article_model = self.db.get(ArticleModel, article.id)

        if article_model is None:
            raise ValueError(f"Article {article.id} not found")

        for key, value in fields.items():
            setattr(article_model, key, value)

        self.db.flush()

        return self._to_domain(article_model)