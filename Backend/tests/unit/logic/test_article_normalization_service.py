from datetime import datetime, timezone
from uuid import uuid4

import pytest

from Backend.Logic.article_normalization_service import ArticleNormalizationService
from Backend.Logic.domain.article import RawArticle


@pytest.fixture
def provider_id():
    return uuid4()


def make_raw_article(**overrides):
    values = {
        "title": "  Example &amp; headline <b>today</b> ",
        "url": " https://example.com/story/1 ",
        "description": "  A <p>short</p> description ",
        "author": "  Jane&nbsp;Doe ",
        "language": "en",
        "published_at": datetime(2025, 1, 2, 12, tzinfo=timezone.utc),
        "provider_id": uuid4(),
    }
    values.update(overrides)
    return RawArticle(**values)


def test_normalize_cleans_text_and_preserves_article_fields(provider_id):
    raw = make_raw_article(provider_id=provider_id)

    result = ArticleNormalizationService().normalize(
        raw, provider_id=provider_id
    )

    assert result["provider_id"] == provider_id
    assert result["title"] == "Example & headline today"
    assert result["canonical_url"] == "https://example.com/story/1"
    assert result["description"] == "A short description"
    assert result["author"] == "Jane Doe"
    assert result["language"] == "en"
    assert result["published_at"] == datetime(
        2025, 1, 2, 12, tzinfo=timezone.utc
    )
    assert result["first_seen_at"].tzinfo is not None
    assert result["last_seen_at"].tzinfo is not None


@pytest.mark.parametrize("title", ["", "   ", None])
def test_normalize_rejects_missing_title(provider_id, title):
    with pytest.raises(ValueError, match="RSS item has no title"):
        ArticleNormalizationService().normalize(
            make_raw_article(title=title), provider_id=provider_id
        )


@pytest.mark.parametrize("url", ["", "   ", None])
def test_normalize_rejects_missing_url(provider_id, url):
    with pytest.raises(ValueError, match="RSS item has no URL"):
        ArticleNormalizationService().normalize(
            make_raw_article(url=url), provider_id=provider_id
        )


def test_normalize_uses_fallback_language(provider_id):
    result = ArticleNormalizationService().normalize(
        make_raw_article(language=" "), provider_id=provider_id
    )
    assert result["language"] == "nl"


def test_normalize_uses_custom_fallback_language(provider_id):
    result = ArticleNormalizationService().normalize(
        make_raw_article(language=None),
        provider_id=provider_id,
        fallback_language="de",
    )
    assert result["language"] == "de"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2025-01-02T12:30:00Z", datetime(2025, 1, 2, 12, 30, tzinfo=timezone.utc)),
        ("not-a-date", None),
        (None, None),
        (123, None),
    ],
)
def test_normalize_published_date(provider_id, value, expected):
    result = ArticleNormalizationService().normalize(
        make_raw_article(published_at=value), provider_id=provider_id
    )
    assert result["published_at"] == expected


def test_normalize_converts_naive_datetime_to_utc(provider_id):
    result = ArticleNormalizationService().normalize(
        make_raw_article(published_at=datetime(2025, 1, 2, 12)),
        provider_id=provider_id,
    )
    assert result["published_at"] == datetime(
        2025, 1, 2, 12, tzinfo=timezone.utc
    )
