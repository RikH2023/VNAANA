from Backend.database import SessionLocal
from Backend.Dal.repositories.article_repository import ArticleRepository
from Backend.Logic.article_scraping_service import ArticleScrapingService


BATCH_SIZE = 100


def main() -> None:
    db = SessionLocal()

    try:
        article_repository = ArticleRepository(db)

        scraping_service = ArticleScrapingService(
            article_repository=article_repository,
        )

        print("Starting article scraping...")
        print(f"Batch size: {BATCH_SIZE}\n")

        results = scraping_service.scrape_pending_articles(
            limit=BATCH_SIZE,
        )

        db.commit()

        print("\n" + "=" * 50)
        print("ARTICLE SCRAPING SUMMARY")
        print("=" * 50)
        print(f"Total:      {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed:     {results['failed']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()