import uuid
from typing import Any, Protocol

from Backend.Logic.domain.user import User


class UserRepository(Protocol):
    def get(self, user_id: uuid.UUID) -> User | None:
        ...

    def add(self, **fields: Any) -> User:
        ...

    def update(self, user: User, **fields: Any) -> User:
        ...

    def delete(self, user: User) -> None:
        ...

    def get_tag_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        ...

    def replace_tags(
        self,
        user: User,
        tag_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        ...