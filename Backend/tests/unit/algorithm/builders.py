"""Mock data for the algorithm tests.

Small helpers that build domain objects with sensible defaults, so a test
only has to spell out what it is actually about. Every date is relative to
one fixed NOW, so results never depend on when the tests run.
"""

import uuid
from datetime import datetime, timedelta, timezone

from Backend.Logic.domain.declared_tag import DeclaredTag
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.story import Story, StoryStatus
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction
from Backend.Logic.domain.user import User

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def days_ago(days: float) -> datetime:
    return NOW - timedelta(days=days)


def new_id() -> uuid.UUID:
    return uuid.uuid4()


def make_user(*, consent: bool = True) -> User:
    return User(
        id=new_id(),
        age_band=None,
        language=None,
        region=None,
        preferences=None,
        analytics_consent=consent,
        consent_updated_at=None,
        auth_provider="google",
        auth_subject=str(new_id()),
        affinity_updated_at=None,
    )


def make_story(
    title: str = "story",
    *,
    updated_days_ago: float = 0,
    status: StoryStatus = StoryStatus.published,
) -> Story:
    return Story(
        id=new_id(),
        title=title,
        summary=None,
        context=None,
        status=status,
        first_published_at=days_ago(updated_days_ago),
        last_updated_at=days_ago(updated_days_ago),
    )


def make_event(
    user_id: uuid.UUID,
    story_id: uuid.UUID | None,
    event_type: str,
    *,
    happened_days_ago: float = 0,
) -> EngagementEvent:
    return EngagementEvent(
        id=new_id(),
        user_id=user_id,
        session_id=new_id(),
        story_id=story_id,
        article_id=None,
        event_type=event_type,
        occurred_at=days_ago(happened_days_ago),
        ingested_at=NOW,
        active_duration_ms=None,
        event_metadata=None,
    )


def make_reaction(
    user_id: uuid.UUID,
    story_id: uuid.UUID,
    reaction: Reaction,
    *,
    happened_days_ago: float = 0,
) -> StoryReaction:
    return StoryReaction(
        user_id=user_id,
        story_id=story_id,
        reaction=reaction,
        updated_at=days_ago(happened_days_ago),
    )


def declared(tag_id: uuid.UUID, *, declared_days_ago: float = 0) -> DeclaredTag:
    return DeclaredTag(tag_id=tag_id, declared_at=days_ago(declared_days_ago))
