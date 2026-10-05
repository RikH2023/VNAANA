from domain.provider_source import ProviderSource
from article_service import ArticleService
from provider_source_service import ProviderSourceService
from sources.news_source import NewsSource


class NewsGatheringService:

    def __init__(
        self,
        provider_source_service: ProviderSourceService,
        article_service: ArticleService,
        source_handlers: dict[str, NewsSource],
    ):
        self.provider_source_service = provider_source_service
        self.article_service = article_service
        self.source_handlers = source_handlers

    async def gather(self) -> None:
        sources = (
            await self.provider_source_service
            .get_active_sources()
        )

        for source in sources:
            await self._gather_source(source)

    async def _gather_source(
        self,
        source: ProviderSource,
    ) -> None:

        handler = self.source_handlers.get(source.source_type)

        if handler is None:
            raise ValueError(
                f"Unsupported source type: {source.source_type}"
            )

        raw_articles = await handler.fetch(source)

        for raw_article in raw_articles:
            article = await self.article_service.process(
                raw_article
            )

            await self.article_service.save(article)