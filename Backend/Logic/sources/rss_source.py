import feedparser

from domain.article import RawArticle
from domain.provider_source import ProviderSource
from sources.news_source import NewsSource


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
                    content=entry.get("summary"),
                    published_at=None,
                    provider_id=source.provider_id,
                )
            )

        return articles