import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.Dal.models import Tag as TagModel
from Backend.Logic.domain.tag import Tag
from Backend.Logic.ports.tag_repository import (
    TagRepository as TagRepositoryPort,
)


class TagRepository(TagRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(tag: TagModel) -> Tag:
        return Tag(
            id=tag.id,
            name=tag.name,
        )

    def get(self, tag_id: uuid.UUID) -> Tag | None:
        tag = self.db.get(TagModel, tag_id)

        if tag is None:
            return None

        return self._to_domain(tag)

    def get_many(self, tag_ids: list[uuid.UUID]) -> list[Tag]:
        if not tag_ids:
            return []

        tags = self.db.scalars(
            select(TagModel).where(TagModel.id.in_(tag_ids))
        )

        return [self._to_domain(tag) for tag in tags]

    def get_by_name(self, name: str) -> Tag | None:
        tag = self.db.scalars(
            select(TagModel).where(TagModel.name == name)
        ).first()

        if tag is None:
            return None

        return self._to_domain(tag)

    def list_all(self) -> list[Tag]:
        tags = self.db.scalars(
            select(TagModel).order_by(TagModel.name)
        )

        return [self._to_domain(tag) for tag in tags]

    def add(self, name: str) -> Tag:
        tag_model = TagModel(name=name)

        self.db.add(tag_model)
        self.db.flush()

        return self._to_domain(tag_model)