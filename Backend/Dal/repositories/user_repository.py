import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.Dal.models import (
    User as UserModel,
    UserTag,
)
from Backend.Dal.models.base import utcnow
from Backend.Logic.domain.user import User
from Backend.Logic.ports.user_repository import (
    UserRepository as UserRepositoryPort,
)
from sqlalchemy.dialects.postgresql import insert

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
            auth_provider=user.auth_provider,
            auth_subject=user.auth_subject,
            affinity_updated_at=user.affinity_updated_at,
        )

    def get(self, user_id: uuid.UUID) -> User | None:
        user = self.db.get(UserModel, user_id)

        if user is None:
            return None

        return self._to_domain(user)

    def get_by_identity(self, auth_provider: str, auth_subject: str) -> User | None:
        user = self.db.scalar(select(UserModel).where(
            UserModel.auth_provider == auth_provider,
            UserModel.auth_subject == auth_subject,
        ))
        return self._to_domain(user) if user is not None else None

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
        user_model = self.db.get(UserModel, user.id)

        if user_model is None:
            return

        self.db.delete(user_model)
        self.db.flush()

    def get_tag_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        stmt = select(UserTag.tag_id).where(
            UserTag.user_id == user_id,
            UserTag.is_declared.is_(True),
        )

        return list(self.db.scalars(stmt))

    def replace_tags(
        self,
        user: User,
        tag_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        wanted = set(tag_ids)

        # Edit declared interests while preserving stored affinity data.
        current = {
            row.tag_id: row
            for row in self.db.scalars(select(UserTag).where(UserTag.user_id == user.id))
        }
        for tag_id, row in current.items():
            declared = tag_id in wanted
            if row.is_declared != declared:
                row.is_declared = declared
                row.updated_at = utcnow()

        for tag_id in wanted - current.keys():
            self.db.add(
                UserTag(
                    user_id=user.id,
                    tag_id=tag_id,
                    is_declared=True,
                    score=0.0,  # Neutral initial value; no affinity calculation here.
                )
            )

        self.db.flush()

        return self.get_tag_ids(user.id)

    def get_or_create_by_identity(
        self,
        auth_provider: str,
        auth_subject: str,
    ) -> User:
        stmt = insert(UserModel).values(
            auth_provider=auth_provider,
            auth_subject=auth_subject,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[
                UserModel.auth_provider,
                UserModel.auth_subject,
            ],
            set_={
                "auth_subject": stmt.excluded.auth_subject,
            },
        ).returning(UserModel)

        user_model = self.db.scalars(
            stmt,
            execution_options={"populate_existing": True},
        ).one()

        return self._to_domain(user_model)
