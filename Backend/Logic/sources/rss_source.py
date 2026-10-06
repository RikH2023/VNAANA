import feedparser
import asyncio

from Backend.Logic.domain.article import RawArticle
from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.sources.news_source import NewsSource


class RSSSource(NewsSource):

    async def fetch(
        self,
        source: ProviderSource,
    ) -> list[RawArticle]:

        feed = feedparser.parse(source.url)

        articles: list[RawArticle] = []

        for entry in feed.entries:
            articles.append(
                RawArticle(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    description=entry.get("summary"),
                    author=entry.get("author"),
                    language=entry.get("language"),
                    published_at=None,
                    provider_id=source.provider_id,
                )
            )

        return articles