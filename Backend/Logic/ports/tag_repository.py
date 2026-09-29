import uuid
from typing import Protocol

from Backend.Logic.domain.tag import Tag


class TagRepository(Protocol):
    def get(self, tag_id: uuid.UUID) -> Tag | None:
        ...

    def get_many(self, tag_ids: list[uuid.UUID]) -> list[Tag]:
        ...

    def get_by_name(self, name: str) -> Tag | None:
        ...

    def list_all(self) -> list[Tag]:
        ...

    def add(self, name: str) -> Tag:
        ...