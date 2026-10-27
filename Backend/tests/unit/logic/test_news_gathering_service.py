from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

import pytest

from Backend.Logic.domain.article import RawArticle
from Backend.Logic.domain.provider_source import ProviderSource
from Backend.Logic.news_gathering_service import NewsGatheringService


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


@pytest.fixture
def raw_article(source):
    return RawArticle(
        title="Example headline",
        url="https://example.com/story/1",
        description="A simulated story",
        author="Reporter",
        language="en",
        published_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
        provider_id=source.provider_id,
    )


@pytest.fixture
def service():
    provider_source_service = Mock()
    provider_source_service.get_active_sources = Mock()

    article_service = Mock()
    article_repository = Mock()
    provider_repository = Mock()
    normalization_service = Mock()

    service = NewsGatheringService(
        provider_source_service=provider_source_service,
        article_service=article_service,
        article_repository=article_repository,
        provider_repository=provider_repository,
        source_handlers={},
        article_normalization_service=normalization_service,
    )
    return service


@pytest.mark.asyncio
async def test_gather_fetches_and_ingests_articles(source, raw_article):
    source_service = Mock()
    source_service.get_active_sources = Mock(return_value=[source])
    # Replace with an AsyncMock because get_active_sources is async.
    from unittest.mock import AsyncMock
    source_service.get_active_sources = AsyncMock(return_value=[source])

    handler = Mock()
    handler.fetch = AsyncMock(return_value=[raw_article])

    normalized = {"title": "Example headline", "provider_id": source.provider_id}
    normalization = Mock()
    normalization.normalize.return_value = normalized

    article = Mock()
    article.title = "Example headline"
    article_service = Mock()
    article_service.ingest_article.return_value = (article, True)

    service = NewsGatheringService(
        provider_source_service=source_service,
        article_service=article_service,
        article_repository=Mock(),
        provider_repository=Mock(),
        source_handlers={"rss": handler},
        article_normalization_service=normalization,
    )

    await service.gather()

    source_service.get_active_sources.assert_awaited_once_with()
    handler.fetch.assert_awaited_once_with(source)
    normalization.normalize.assert_called_once_with(
        raw_article, provider_id=source.provider_id
    )
    article_service.ingest_article.assert_called_once_with(normalized)


@pytest.mark.asyncio
async def test_gather_continues_when_one_article_is_invalid(source, raw_article):
    from unittest.mock import AsyncMock

    source_service = Mock()
    source_service.get_active_sources = AsyncMock(return_value=[source])
    handler = Mock()
    handler.fetch = AsyncMock(return_value=[raw_article, raw_article])

    normalization = Mock()
    normalization.normalize.side_effect = [
        ValueError("missing title"),
        {"title": "Valid article", "provider_id": source.provider_id},
    ]

    article = Mock()
    article.title = "Valid article"
    article_service = Mock()
    article_service.ingest_article.return_value = (article, True)

    service = NewsGatheringService(
        provider_source_service=source_service,
        article_service=article_service,
        article_repository=Mock(),
        provider_repository=Mock(),
        source_handlers={"rss": handler},
        article_normalization_service=normalization,
    )

    await service.gather()

    assert normalization.normalize.call_count == 2
    article_service.ingest_article.assert_called_once()


@pytest.mark.asyncio
async def test_gather_raises_for_unsupported_source_type(source):
    from unittest.mock import AsyncMock
    from dataclasses import replace

    unsupported_source = replace(source, source_type="unknown")
    source_service = Mock()
    source_service.get_active_sources = AsyncMock(return_value=[unsupported_source])

    service = NewsGatheringService(
        provider_source_service=source_service,
        article_service=Mock(),
        article_repository=Mock(),
        provider_repository=Mock(),
        source_handlers={},
        article_normalization_service=Mock(),
    )

    with pytest.raises(ValueError, match="Unsupported source type: unknown"):
        await service.gather()


@pytest.mark.asyncio
async def test_gather_propagates_source_fetch_failure(source):
    from unittest.mock import AsyncMock

    source_service = Mock()
    source_service.get_active_sources = AsyncMock(return_value=[source])
    handler = Mock()
    handler.fetch = AsyncMock(side_effect=RuntimeError("feed unavailable"))

    service = NewsGatheringService(
        provider_source_service=source_service,
        article_service=Mock(),
        article_repository=Mock(),
        provider_repository=Mock(),
        source_handlers={"rss": handler},
        article_normalization_service=Mock(),
    )

    with pytest.raises(RuntimeError, match="feed unavailable"):
        await service.gather()
