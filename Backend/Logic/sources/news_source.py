from abc import ABC, abstractmethod

from domain.article import RawArticle
from domain.provider_source import ProviderSource


class NewsSource(ABC):

    @abstractmethod
    async def fetch(self, source: ProviderSource) -> list[RawArticle]:
        pass