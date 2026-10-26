
import re
import uuid
from datetime import datetime, timezone
from html import unescape

from Backend.Logic.domain.article import RawArticle


class ArticleNormalizationService:
    """Normalize parsed feed entries into the application's article schema."""

    def normalize(
        self,
        raw_article: RawArticle,
        *,
        provider_id: uuid.UUID,
        fallback_language: str = "nl",
    ) -> dict:
        now = datetime.now(timezone.utc)

        title = self._clean_text(raw_article.title)
        url = self._clean_text(raw_article.url)

        if not title:
            raise ValueError("RSS item has no title")

        if not url:
            raise ValueError("RSS item has no URL")

        return {
            "provider_id": provider_id,
            "canonical_url": url,
            "title": title,
            "description": self._clean_text(
                raw_article.description
            ) or None,
            "author": self._clean_text(
                raw_article.author
            ) or None,
            "language": (
                self._clean_text(raw_article.language)
                or fallback_language
            ),
            "published_at": self._normalize_date(
                getattr(raw_article, "published_at", None)
            ),
            "first_seen_at": now,
            "last_seen_at": now,
        }

    @staticmethod
    def _clean_text(value: str | None) -> str:
        if not value:
            return ""

        value = unescape(value)
        value = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _normalize_date(value) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                return None
        else:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)
