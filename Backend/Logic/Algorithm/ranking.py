"""Ranking: turns a user's tag scores into an ordered feed.

Also decides whether "For you" is unlocked at all.

Which stories are candidates (published, not deleted) and whether the user
may be personalised (logged in, consent) is decided before this runs.
"""

import uuid
from datetime import datetime

from Backend.Logic.Algorithm.decay import as_utc, decay
from Backend.Logic.Algorithm.shared_types import StoryTags, TagScores
from Backend.Logic.domain.feed import RankedStory
from Backend.Logic.domain.story import Story

# ---- unlock rule (design doc D10) ---------------------------------------------

BROAD_TAG_COUNT = 3     # three tags ...
BROAD_MIN_SCORE = 10    # ... at 10 or more
FOCUSED_MIN_SCORE = 15  # or one tag at 15 or more


def is_unlocked(tag_scores: TagScores) -> bool:
    broad = sum(1 for score in tag_scores.values() if score >= BROAD_MIN_SCORE)
    focused = any(score >= FOCUSED_MIN_SCORE for score in tag_scores.values())

    return broad >= BROAD_TAG_COUNT or focused


# ---- scoring a single story (design doc D7, D9) --------------------------------

def story_score(tag_ids: list[uuid.UUID], tag_scores: TagScores) -> float:
    """Average of the user's scores for the story's tags.

    A tag the user has no score for counts as 0. A story without tags is 0.
    """
    if not tag_ids:
        return 0.0

    return sum(tag_scores.get(tag_id, 0.0) for tag_id in tag_ids) / len(tag_ids)


def final_score(score: float, last_updated_at: datetime, now: datetime) -> float:
    """Freshness only lowers positive scores; a negative score stays as it is."""
    if score > 0:
        return score * decay(last_updated_at, now)

    return score


# ---- the feed ----------------------------------------------------------------------

def rank_stories(
    stories: list[Story],
    story_tags: StoryTags,
    tag_scores: TagScores,
    now: datetime,
) -> list[RankedStory]:
    """Highest final score first; equal scores go to the newest story."""
    ranked = [
        RankedStory(
            story=story,
            score=final_score(
                story_score(story_tags.get(story.id, []), tag_scores),
                story.last_updated_at,
                now,
            ),
        )
        for story in stories
    ]

    return sorted(
        ranked,
        key=lambda item: (item.score, as_utc(item.story.last_updated_at)),
        reverse=True,
    )