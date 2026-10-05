from Dal.repositories.provider_source_repository import ProviderSourceRepository
from domain.provider_source import ProviderSource


class ProviderSourceService:

    def __init__(
        self,
        repository: ProviderSourceRepository,
    ):
        self.repository = repository

    async def get_active_sources(self) -> list[ProviderSource]:
        return await self.repository.get_active_sources()