from uuid import UUID
from typing import List
from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.ports.provider_source_repository import (
    ProviderSourceRepository,
)

from Backend.Dal.mock_data.provider_sources import MOCK_PROVIDER_SOURCES


class MockProviderSourceRepository(ProviderSourceRepository):
    """Temporary in-memory repository used until the database DAL exists."""

    def __init__(
        self,
        sources: list[ProviderSource] | None = None,
    ) -> None:
        self._sources = list(sources or MOCK_PROVIDER_SOURCES)

    async def get_active_sources(self) -> list[ProviderSource]:
        return [
            source
            for source in self._sources
            if source.is_active
        ]

    def get(self, source_id: UUID) -> ProviderSource | None:
        return next(
            (
                source
                for source in self._sources
                if source.id == source_id
            ),
            None,
        )

    def list(
        self,
        *,
        provider_id: UUID | None = None,
        active_only: bool = False,
    ) -> List[ProviderSource]:

        sources = self._sources

        if provider_id is not None:
            sources = [
                source
                for source in sources
                if source.provider_id == provider_id
            ]

        if active_only:
            sources = [
                source
                for source in sources
                if source.is_active
            ]

        return list(sources)

    def list_active(self) -> List[ProviderSource]:
        return self.list(active_only=True)