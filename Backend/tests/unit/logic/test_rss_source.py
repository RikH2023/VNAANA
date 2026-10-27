import calendar
from datetime import datetime, timezone
from time import struct_time
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.sources import rss_source as rss_module
from Backend.Logic.sources.rss_source import RSSSource


@pytest.fixture
def source():
    return ProviderSource(
        id=uuid4(),
        provider_id=uuid4(),
        provider_name="Example News",
        provider_domain="example.com",
        name="Example RSS",
        source_type="rss",
        url="https://example.com/feed.xml",
        poll_interval_minutes=30,
        is_active=True,
        configuration={},
    )


@pytest.mark.asyncio
async def test_fetch_maps_feed_entry_to_raw_article(monkeypatch, source):
    published = struct_time((2025, 2, 3, 4, 5, 6, 0, 34, 0))
    feed = SimpleNamespace(
        bozo=0,
        entries=[
            {
                "title": "Headline",
                "link": "https://example.com/story",
                "summary": "Summary",
                "author": "Author",
                "language": "en",
                "published_parsed": published,
            }
        ],
        feed={"language": "nl"},
    )
    parse = Mock(return_value=feed)
    monkeypatch.setattr(rss_module.feedparser, "parse", parse)

    articles = await RSSSource().fetch(source)

    parse.assert_called_once_with(source.url)
    assert len(articles) == 1
    article = articles[0]
    assert article.title == "Headline"
    assert article.url == "https://example.com/story"
    assert article.description == "Summary"
    assert article.author == "Author"
    assert article.language == "en"
    assert article.provider_id == source.provider_id
    assert article.published_at == datetime(
        2025, 2, 3, 4, 5, 6, tzinfo=timezone.utc
    )


@pytest.mark.asyncio
async def test_fetch_uses_feed_language_and_updated_date(monkeypatch, source):
    updated = struct_time((2024, 8, 9, 10, 11, 12, 4, 222, 0))
    feed = SimpleNamespace(
        bozo=0,
        entries=[{"title": "Headline", "link": "https://example.com/a",
                  "updated_parsed": updated}],
        feed={"language": "fr"},
    )
    monkeypatch.setattr(rss_module.feedparser, "parse", Mock(return_value=feed))

    articles = await RSSSource().fetch(source)

    assert articles[0].language == "fr"
    assert articles[0].published_at == datetime.fromtimestamp(
        calendar.timegm(updated), tz=timezone.utc
    )
    assert articles[0].description is None
    assert articles[0].author is None


@pytest.mark.asyncio
async def test_fetch_returns_empty_list_for_empty_feed(monkeypatch, source):
    feed = SimpleNamespace(bozo=0, entries=[], feed={})
    monkeypatch.setattr(rss_module.feedparser, "parse", Mock(return_value=feed))

    assert await RSSSource().fetch(source) == []


@pytest.mark.asyncio
async def test_fetch_handles_missing_optional_fields(monkeypatch, source):
    feed = SimpleNamespace(bozo=0, entries=[{}], feed={})
    monkeypatch.setattr(rss_module.feedparser, "parse", Mock(return_value=feed))

    articles = await RSSSource().fetch(source)

    assert len(articles) == 1
    assert articles[0].title == ""
    assert articles[0].url == ""
    assert articles[0].description is None
    assert articles[0].published_at is None
