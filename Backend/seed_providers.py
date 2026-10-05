from Backend.database import SessionLocal
from Backend.Dal.mock_data.provider_sources import MOCK_PROVIDER_SOURCES
from Backend.Dal.repositories.provider_repository import ProviderRepository


def main() -> None:
    print("1. Starting seed script")

    print("2. Creating database session")
    db = SessionLocal()

    try:
        print("3. Creating repository")
        repository = ProviderRepository(db)

        print("4. Loading mock sources")
        nos_source = next(
            source
            for source in MOCK_PROVIDER_SOURCES
            if source.provider_name == "NOS"
        )

        print(f"5. Found source: {nos_source.name}")
        print(f"   Provider ID: {nos_source.provider_id}")

        print("6. Checking provider in database")
        existing = repository.get(nos_source.provider_id)

        print("7. Provider lookup finished")

        if existing is not None:
            print(
                f"Provider already exists: "
                f"{existing.name} ({existing.domain})"
            )
            return

        print("8. Creating provider")

        provider = repository.add(
            id=nos_source.provider_id,
            name=nos_source.provider_name,
            domain=nos_source.provider_domain,
            country_code="NL",
            reliability_status="unknown",
        )

        print("9. Committing transaction")
        db.commit()

        print(
            f"Created provider: "
            f"{provider.name} ({provider.domain})"
        )
        print(f"Provider ID: {provider.id}")

    except Exception:
        print("ERROR — rolling back")
        db.rollback()
        raise

    finally:
        print("10. Closing database")
        db.close()


if __name__ == "__main__":
    main()