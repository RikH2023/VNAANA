from Backend.database import SessionLocal
from Backend.Dal.mock_data.provider_sources import MOCK_PROVIDER_SOURCES
from Backend.Dal.repositories.provider_repository import ProviderRepository
from Backend.Logic.article_normalization_service import (
    ArticleNormalizationService,
)

def main() -> None:
    print("1. Starting provider seed script")

    # One provider may have multiple RSS category feeds.
    providers = {
        source.provider_id: source
        for source in MOCK_PROVIDER_SOURCES
    }

    print(f"2. Found {len(providers)} unique providers")

    db = SessionLocal()

    created = 0
    skipped = 0

    try:
        repository = ProviderRepository(db)

        for provider_id, source in providers.items():
            print(
                f"\nChecking: {source.provider_name} "
                f"({source.provider_domain})"
            )

            existing = repository.get(provider_id)

            if existing is not None:
                print(
                    f"  SKIPPED: Already exists "
                    f"({existing.name})"
                )
                skipped += 1
                continue

            provider = repository.add(
                id=source.provider_id,
                name=source.provider_name,
                domain=source.provider_domain,
                country_code="NL",
                reliability_status="unknown",
            )

            print(f"  CREATED: {provider.name}")
            created += 1

        db.commit()

        print("\n" + "=" * 50)
        print("PROVIDER SEED SUMMARY")
        print("=" * 50)
        print(f"Total unique providers: {len(providers)}")
        print(f"Created:               {created}")
        print(f"Already existed:       {skipped}")
        print("Database transaction committed successfully.")

    except Exception:
        print("ERROR — rolling back transaction")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()