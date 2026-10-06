from abc import ABC, abstractmethod

from Backend.Logic.domain.article import RawArticle
from Backend.Logic.domain.provider_source import ProviderSource


class NewsSource(ABC):

    @abstractmethod
    async def fetch(
        self,
        source: ProviderSource,
    ) -> list[RawArticle]:
        pass