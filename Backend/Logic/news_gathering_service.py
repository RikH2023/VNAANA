from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.article_service import ArticleService
from Backend.Logic.provider_source_service import ProviderSourceService
from Backend.Logic.sources.news_source import NewsSource
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.provider_repository import ProviderRepository
from datetime import datetime, timezone


class NewsGatheringService:

    def __init__(
        self,
        provider_source_service: ProviderSourceService,
        article_service: ArticleService,
        article_repository: ArticleRepository,
        provider_repository: ProviderRepository,
        source_handlers: dict[str, NewsSource],
    ):
        self.provider_source_service = provider_source_service
        self.article_service = article_service
        self.article_repository = article_repository
        self.provider_repository = provider_repository
        self.source_handlers = source_handlers

    async def gather(self) -> None:
        sources = (
            await self.provider_source_service.get_active_sources()
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
            self.article_service.ingest_article(
                self.article_repository,
                self.provider_repository,
                {
                    "provider_id": raw_article.provider_id,
                    "canonical_url": raw_article.url,
                    "title": raw_article.title,
                    "description": raw_article.content,
                    "author": None,
                    "language": None,
                    "published_at": raw_article.published_at,
                    "first_seen_at": datetime.now(timezone.utc),
                    "last_seen_at": datetime.now(timezone.utc),
                },
            )