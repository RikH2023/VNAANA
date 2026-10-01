import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import User, UserTag


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def add(self, **fields: Any) -> User:
        user = User(**fields)
        self.db.add(user)
        self.db.flush()
        return user

    def update(self, user: User, **fields: Any) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        self.db.flush()
        return user

    def delete(self, user: User) -> None:
        """Delete the user and tags; the database nulls retained events' user_id."""
        self.db.delete(user)
        self.db.flush()

    # ---- user_tags ----

    def get_tags(self, user_id: uuid.UUID) -> list[UserTag]:
        stmt = select(UserTag).where(UserTag.user_id == user_id)
        return list(self.db.scalars(stmt))

    def replace_tags(self, user: User, tag_ids: list[uuid.UUID]) -> list[UserTag]:
        """Replace the user's interests with exactly these tags.

        Tags the user already had keep their row (and updated_at), new ones are
        added, and missing ones are removed.
        """
        wanted = set(tag_ids)
        current = {ut.tag_id: ut for ut in self.get_tags(user.id)}

        for tag_id, user_tag in current.items():
            if tag_id not in wanted:
                self.db.delete(user_tag)
        for tag_id in wanted - current.keys():
            self.db.add(UserTag(user_id=user.id, tag_id=tag_id))

        self.db.flush()
        self.db.expire(user, ["tags"])
        return self.get_tags(user.id)
