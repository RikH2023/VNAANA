import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from Backend.dal.models import (
    EngagementEvent as EngagementEventModel,
    User as UserModel,
    UserTag,
)
from Backend.Logic.domain.user import User
from Backend.Logic.ports.user_repository import (
    UserRepository as UserRepositoryPort,
)


class UserRepository(UserRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(user: UserModel) -> User:
        return User(
            id=user.id,
            age_band=user.age_band,
            language=user.language,
            region=user.region,
            preferences=user.preferences,
            analytics_consent=user.analytics_consent,
            consent_updated_at=user.consent_updated_at,
        )

    def get(self, user_id: uuid.UUID) -> User | None:
        user = self.db.get(UserModel, user_id)

        if user is None:
            return None

        return self._to_domain(user)

    def add(self, **fields: Any) -> User:
        user_model = UserModel(**fields)

        self.db.add(user_model)
        self.db.flush()

        return self._to_domain(user_model)

    def update(self, user: User, **fields: Any) -> User:
        user_model = self.db.get(UserModel, user.id)

        if user_model is None:
            raise ValueError(f"User {user.id} not found")

        for key, value in fields.items():
            setattr(user_model, key, value)

        self.db.flush()

        return self._to_domain(user_model)

    def delete(self, user: User) -> None:
        """Hard delete (right to erasure)."""

        self.db.execute(
            delete(EngagementEventModel).where(
                EngagementEventModel.user_id == user.id
            )
        )

        self.db.execute(
            delete(UserTag).where(
                UserTag.user_id == user.id
            )
        )

        user_model = self.db.get(UserModel, user.id)

        if user_model is None:
            return

        self.db.delete(user_model)
        self.db.flush()

    # ---- user_tags ----

    def get_tag_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        stmt = select(UserTag.tag_id).where(
            UserTag.user_id == user_id
        )

        return list(self.db.scalars(stmt))

    def replace_tags(
        self,
        user: User,
        tag_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        wanted = set(tag_ids)

        current = set(self.get_tag_ids(user.id))

        for tag_id in current - wanted:
            self.db.execute(
                delete(UserTag).where(
                    UserTag.user_id == user.id,
                    UserTag.tag_id == tag_id,
                )
            )

        for tag_id in wanted - current:
            self.db.add(
                UserTag(
                    user_id=user.id,
                    tag_id=tag_id,
                )
            )

        self.db.flush()

        return self.get_tag_ids(user.id)