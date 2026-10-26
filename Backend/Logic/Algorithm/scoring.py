"""Scoring: turns one user's actions into a score per tag.

Two steps:
1. convert  every input into a Signal (tag_ids, weight, happened_at).
            This is the only place the weights live: the DAL delivers raw
            data, the Logic decides what it is worth.
2. add up   weight × decay for every tag a signal touches.

Who gets scored (consent, logged in) is decided before this runs.
Everything passed in here is assumed to be allowed to be used.
"""

import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from Backend.Logic.Algorithm.decay import decay
from Backend.Logic.Algorithm.shared_types import StoryTags, TagScores
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.onboarding_tag import OnboardingTag
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction

# ---- weights (design doc D1, D8) ---------------------------------------------

EVENT_WEIGHTS: dict[str, float] = {
    "share": 5,
    "read_complete": 1,
}

REACTION_WEIGHTS: dict[Reaction, float] = {
    Reaction.like: 2,
    Reaction.dislike: -5,
}

ONBOARDING_BONUS: float = 5


@dataclass(frozen=True)
class Signal:
    """One thing that tells us something about the user's interests."""

    tag_ids: tuple[uuid.UUID, ...]
    weight: float
    happened_at: datetime


# ---- step 1: convert -----------------------------------------------------------

def signals_from_events(events: list[EngagementEvent], story_tags: StoryTags) -> list[Signal]:
    signals = []

    for event in events:
        weight = EVENT_WEIGHTS.get(event.event_type)
        tag_ids = story_tags.get(event.story_id, [])

        # Unknown event types and stories without tags tell us nothing.
        if weight is None or not tag_ids:
            continue

        signals.append(Signal(tuple(tag_ids), weight, event.occurred_at))

    return signals


def signals_from_reactions(reactions: list[StoryReaction], story_tags: StoryTags) -> list[Signal]:
    signals = []

    for reaction in reactions:
        tag_ids = story_tags.get(reaction.story_id, [])

        if not tag_ids:
            continue

        signals.append(
            Signal(tuple(tag_ids), REACTION_WEIGHTS[reaction.reaction], reaction.updated_at)
        )

    return signals


def signals_from_onboarding(onboarding_tags: list[OnboardingTag]) -> list[Signal]:
    return [
        Signal((tag.tag_id,), ONBOARDING_BONUS, tag.picked_at)
        for tag in onboarding_tags
    ]


# ---- step 2: add up --------------------------------------------------------------

def tag_scores(signals: list[Signal], now: datetime) -> TagScores:
    """Every signal gives its full weight to every tag it touches (design doc D6)."""
    scores: dict[uuid.UUID, float] = defaultdict(float)

    for signal in signals:
        value = signal.weight * decay(signal.happened_at, now)

        for tag_id in signal.tag_ids:
            scores[tag_id] += value

    return dict(scores)


# ---- both steps for one user -------------------------------------------------------

def score_user(
    events: list[EngagementEvent],
    reactions: list[StoryReaction],
    onboarding_tags: list[OnboardingTag],
    story_tags: StoryTags,
    now: datetime,
) -> TagScores:
    signals = (
        signals_from_events(events, story_tags)
        + signals_from_reactions(reactions, story_tags)
        + signals_from_onboarding(onboarding_tags)
    )

    return tag_scores(signals, now)