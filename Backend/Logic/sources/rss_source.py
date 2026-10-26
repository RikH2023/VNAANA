
import calendar
import feedparser

from datetime import datetime, timezone

from Backend.Logic.domain.article import RawArticle
from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.sources.news_source import NewsSource


class RSSSource(NewsSource):

    async def fetch(
        self,
        source: ProviderSource,
    ) -> list[RawArticle]:

        feed = feedparser.parse(source.url)

        if getattr(feed, "bozo", False):
            print(
                f"Warning: feed parsing issue for {source.name}: "
                f"{getattr(feed, 'bozo_exception', 'unknown error')}"
            )

        articles: list[RawArticle] = []

        for entry in feed.entries:
            parsed_date = (
                entry.get("published_parsed")
                or entry.get("updated_parsed")
            )

            published_at = None
            if parsed_date:
                published_at = datetime.fromtimestamp(
                    calendar.timegm(parsed_date),
                    tz=timezone.utc,
                )

            articles.append(
                RawArticle(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    description=(
                        entry.get("summary")
                        or entry.get("description")
                    ),
                    author=(
                        entry.get("author")
                        or entry.get("dc_creator")
                    ),
                    language=(
                        entry.get("language")
                        or feed.feed.get("language")
                    ),
                    published_at=published_at,
                    provider_id=source.provider_id,
                )
            )

        return articles
