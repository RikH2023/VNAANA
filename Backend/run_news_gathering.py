import asyncio

from Backend.database import SessionLocal
from Backend.Dal.mock_data.provider_sources import MOCK_PROVIDER_SOURCES
from Backend.Dal.repositories.article_repository import ArticleRepository
from Backend.Dal.repositories.provider_repository import ProviderRepository
from Backend.Dal.repositories.mock_provider_source_repository import (
    MockProviderSourceRepository,
)
from Backend.Logic.article_service import ArticleService
from Backend.Logic.news_gathering_service import NewsGatheringService
from Backend.Logic.provider_source_service import ProviderSourceService
from Backend.Logic.sources.rss_source import RSSSource


async def main() -> None:
    nos_source = next(
        source
        for source in MOCK_PROVIDER_SOURCES
        if source.provider_name == "NOS"
    )

    print(f"Selected source: {nos_source.name}")
    print(f"URL: {nos_source.url}")
    print(f"Provider ID: {nos_source.provider_id}")

    source_repository = MockProviderSourceRepository(
        sources=[nos_source]
    )

    db = SessionLocal()

    try:
        provider_repository = ProviderRepository(db)
        article_repository = ArticleRepository(db)

        provider = provider_repository.get(nos_source.provider_id)

        if provider is None:
            raise RuntimeError(
                "The NOS provider does not exist in the database. "
                f"Expected provider_id: {nos_source.provider_id}"
            )

        print(
            f"Found provider in database: "
            f"{provider.name} ({provider.domain})"
        )

        provider_source_service = ProviderSourceService(
            source_repository
        )

        article_service = ArticleService()

        news_gathering_service = NewsGatheringService(
            provider_source_service=provider_source_service,
            article_service=article_service,
            article_repository=article_repository,
            provider_repository=provider_repository,
            source_handlers={
                "rss": RSSSource(),
            },
        )

        await news_gathering_service.gather()

        db.commit()

        print("Database transaction committed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())