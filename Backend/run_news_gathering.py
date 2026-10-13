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
    sources = [
        source
        for source in MOCK_PROVIDER_SOURCES
        if source.is_active
        and source.url
        and source.source_type == "rss"
    ]

    print(f"Found {len(sources)} active RSS sources to test.\n")

    if not sources:
        print("No active RSS sources found.")
        return

    successful = []
    failed = []
    skipped = []

    db = SessionLocal()

    try:
        provider_repository = ProviderRepository(db)
        article_repository = ArticleRepository(db)

        for source in sources:
            print("=" * 80)
            print(f"Source: {source.name}")
            print(f"Provider: {source.provider_name}")
            print(f"URL: {source.url}")
            print(f"Provider ID: {source.provider_id}")

            try:
                provider = provider_repository.get(source.provider_id)

                if provider is None:
                    message = (
                        "Provider does not exist in the database: "
                        f"{source.provider_id}"
                    )
                    print(f"SKIPPED: {message}")
                    skipped.append((source.name, message))
                    continue

                print(
                    f"Found provider: {provider.name} "
                    f"({provider.domain})"
                )

                # Isolate this source's database operations.
                source_repository = MockProviderSourceRepository(
                    sources=[source]
                )

                provider_source_service = ProviderSourceService(
                    source_repository
                )

                news_gathering_service = NewsGatheringService(
                    provider_source_service=provider_source_service,
                    article_service=ArticleService(),
                    article_repository=article_repository,
                    provider_repository=provider_repository,
                    source_handlers={
                        "rss": RSSSource(),
                    },
                )

                await news_gathering_service.gather()

                db.commit()

                print("SUCCESS: Gathering completed and committed.")
                successful.append(source.name)

            except Exception as exc:
                db.rollback()

                message = f"{type(exc).__name__}: {exc}"
                print(f"FAILED: {message}")
                failed.append((source.name, message))

    finally:
        db.close()

    print("\n" + "=" * 80)
    print("RSS SOURCE TEST SUMMARY")
    print("=" * 80)
    print(f"Total selected: {len(sources)}")
    print(f"Successful:     {len(successful)}")
    print(f"Failed:         {len(failed)}")
    print(f"Skipped:        {len(skipped)}")

    if successful:
        print("\nSuccessful sources:")
        for name in successful:
            print(f"  [OK] {name}")

    if failed:
        print("\nFailed sources:")
        for name, error in failed:
            print(f"  [FAIL] {name}: {error}")

    if skipped:
        print("\nSkipped sources:")
        for name, reason in skipped:
            print(f"  [SKIP] {name}: {reason}")


if __name__ == "__main__":
    asyncio.run(main())