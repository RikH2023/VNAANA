import logging
from typing import Any

import requests
import trafilatura

from Backend.Logic.ports.article_repository import ArticleRepository


logger = logging.getLogger(__name__)


class ArticleScrapingService:
    def __init__(
        self,
        article_repository: ArticleRepository,
        *,
        timeout: int = 20,
        user_agent: str = "VNAANA/1.0 (article research project)",
    ) -> None:
        self.article_repository = article_repository
        self.timeout = timeout
        self.user_agent = user_agent

    def scrape_pending_articles(self, *, limit: int = 100) -> dict[str, int]:
        """
        Scrape articles that have not yet been processed.

        Every attempted article is marked as scraped, even if fetching
        or extracting its content fails.

        Returns a summary of the scraping results.
        """
        articles = self.article_repository.list_unscraped(limit=limit)

        results = {
            "total": len(articles),
            "successful": 0,
            "failed": 0,
        }

        logger.info("Found %d articles waiting to be scraped.", len(articles))

        for article in articles:
            try:
                content = self._extract_content(article.canonical_url)

                if content:
                    self.article_repository.update(
                        article,
                        content=content,
                        is_scraped=True,
                    )
                    results["successful"] += 1

                    logger.info(
                        "Successfully scraped article %s.",
                        article.id,
                    )
                else:
                    self.article_repository.update(
                        article,
                        is_scraped=True,
                    )
                    results["failed"] += 1

                    logger.warning(
                        "No article content could be extracted for %s.",
                        article.id,
                    )

            except Exception:
                results["failed"] += 1

                logger.exception(
                    "Failed to scrape article %s.",
                    article.id,
                )

                try:
                    self.article_repository.update(
                        article,
                        is_scraped=True,
                    )
                except Exception:
                    logger.exception(
                        "Failed to mark article %s as scraped.",
                        article.id,
                    )

        logger.info(
            "Scraping finished. Total: %d, successful: %d, failed: %d.",
            results["total"],
            results["successful"],
            results["failed"],
        )

        return results

    def _extract_content(self, url: str) -> str | None:
        """
        Download a page and extract its main article text.

        Returns None if the page cannot be fetched or no meaningful
        article text can be extracted.
        """
        response = requests.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()

        content = trafilatura.extract(
            response.text,
            url=url,
            include_comments=False,
            include_tables=True,
        )

        if content:
            content = content.strip()

        return content or None