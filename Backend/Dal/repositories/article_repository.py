import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from Backend.Dal.models import Article as ArticleModel
from Backend.Logic.domain.article import Article
from Backend.Logic.ports.article_repository import (
    ArticleRepository as ArticleRepositoryPort,
)


class ArticleRepository(ArticleRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(article_model: ArticleModel) -> Article:
        """Convert a DAL/SQLAlchemy model into a Logic domain object."""
        return Article(
            id=article_model.id,
            provider_id=article_model.provider_id,
            canonical_url=article_model.canonical_url,
            title=article_model.title,
            description=article_model.description,
            author=article_model.author,
            language=article_model.language,
            published_at=article_model.published_at,
            first_seen_at=article_model.first_seen_at,
            last_seen_at=article_model.last_seen_at,
        )

    def get(self, article_id: uuid.UUID) -> Article | None:
        article_model = self.db.get(ArticleModel, article_id)

        if article_model is None:
            return None

        return self._to_domain(article_model)

    def get_by_canonical_url(
        self,
        canonical_url: str,
    ) -> Article | None:
        stmt = select(ArticleModel).where(
            ArticleModel.canonical_url == canonical_url
        )

        article_model = self.db.scalars(stmt).first()

        if article_model is None:
            return None

        return self._to_domain(article_model)

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
            stmt = stmt.where(
                ArticleModel.provider_id == provider_id
            )

        if language is not None:
            stmt = stmt.where(
                ArticleModel.language == language
            )

        stmt = (
            stmt
            .order_by(
                ArticleModel.published_at.desc().nulls_last(),
                ArticleModel.first_seen_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        article_models = self.db.scalars(stmt)

        return [
            self._to_domain(article_model)
            for article_model in article_models
        ]

    def add(self, **fields: Any) -> Article:
        article_model = ArticleModel(**fields)

        self.db.add(article_model)
        self.db.flush()

        return self._to_domain(article_model)

    def ingest(self, **fields: Any) -> tuple[Article, bool]:
        """Atomically insert or refresh an article by canonical URL.

        A conflicting insert keeps the existing id and first_seen_at.
        The caller owns the transaction and commit.

        Returns:
            tuple[Article, bool]:
                The domain article and whether it was newly created.
        """
        candidate_id = uuid.uuid4()

        # IMPORTANT:
        # SQLAlchemy operations use the DAL model, not the domain model.
        stmt = insert(ArticleModel).values(
            **{**fields, "id": candidate_id}
        )

        refresh_fields = (
            "provider_id",
            "title",
            "description",
            "author",
            "language",
            "published_at",
        )

        changes = {
            key: stmt.excluded[key]
            for key in refresh_fields
            if fields.get(key) is not None
        }

        changes["last_seen_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            index_elements=[ArticleModel.canonical_url],
            set_=changes,
        ).returning(ArticleModel)

        article_model = self.db.scalars(
            stmt,
            execution_options={"populate_existing": True},
        ).one()

        article = self._to_domain(article_model)

        return article, article_model.id == candidate_id

    def update(
        self,
        article: Article,
        **fields: Any,
    ) -> Article:
        # Input/output at the repository boundary is the domain model.
        # Database lookup uses the DAL model.
        article_model = self.db.get(ArticleModel, article.id)

        if article_model is None:
            raise ValueError(
                f"Article {article.id} not found"
            )

        for key, value in fields.items():
            setattr(article_model, key, value)

        self.db.flush()

        return self._to_domain(article_model)