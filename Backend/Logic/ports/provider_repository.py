import uuid
from typing import Any, Protocol

from Backend.Logic.domain.provider import Provider


class ProviderRepository(Protocol):
    def get(self, provider_id: uuid.UUID) -> Provider | None:
        ...

    def get_by_domain(self, domain: str) -> Provider | None:
        ...

    def list_all(self) -> list[Provider]:
        ...

    def add(self, **fields: Any) -> Provider:
        ...