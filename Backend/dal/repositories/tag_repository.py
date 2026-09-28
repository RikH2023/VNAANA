import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import Tag


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, tag_id: uuid.UUID) -> Tag | None:
        return self.db.get(Tag, tag_id)

    def get_many(self, tag_ids: list[uuid.UUID]) -> list[Tag]:
        if not tag_ids:
            return []
        return list(self.db.scalars(select(Tag).where(Tag.id.in_(tag_ids))))

    def get_by_name(self, name: str) -> Tag | None:
        return self.db.scalars(select(Tag).where(Tag.name == name)).first()

    def list_all(self) -> list[Tag]:
        return list(self.db.scalars(select(Tag).order_by(Tag.name)))

    def add(self, name: str) -> Tag:
        tag = Tag(name=name)
        self.db.add(tag)
        self.db.flush()
        return tag
