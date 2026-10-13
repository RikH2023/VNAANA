from datetime import datetime, timezone

from Backend.Logic.article_normalization_service import ArticleNormalizationService
from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.article_service import ArticleService
from Backend.Logic.provider_source_service import ProviderSourceService
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.provider_repository import ProviderRepository
from Backend.Logic.sources.news_source import NewsSource


class NewsGatheringService:

    def __init__(
        self,
        provider_source_service: ProviderSourceService,
        article_service: ArticleService,
        article_repository: ArticleRepository,
        provider_repository: ProviderRepository,
        source_handlers: dict[str, NewsSource],
        article_normalization_service: ArticleNormalizationService,
    ):
        self.article_normalization_service = article_normalization_service
        self.provider_source_service = provider_source_service
        self.article_service = article_service
        self.article_repository = article_repository
        self.provider_repository = provider_repository
        self.source_handlers = source_handlers

    async def gather(self) -> None:
        sources = await self.provider_source_service.get_active_sources()

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

        print(f"Fetching source: {source.name}")
        print(f"URL: {source.url}")

        raw_articles = await handler.fetch(source)

        print(f"Fetched {len(raw_articles)} articles")

        for raw_article in raw_articles:
            try:
                article_data = self.article_normalization_service.normalize(
                    raw_article,
                    provider_id=source.provider_id,
                )

                article, created = self.article_service.ingest_article(
                    article_data
                )

                action = "created" if created else "updated"
                print(f"{action}: {article.title}")

            except (ValueError, TypeError) as exc:
                print(
                    f"Skipping invalid article from {source.name}: {exc}"
                )