from abc import ABC, abstractmethod

from Logic.domain.provider_source import ProviderSource


class ProviderSourceRepository(ABC):

    @abstractmethod
    async def get_active_sources(self) -> list[ProviderSource]:
        pass