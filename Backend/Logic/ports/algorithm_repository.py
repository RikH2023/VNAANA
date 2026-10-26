"""Everything the algorithm needs from storage, in one port.

The Logic layer decides what it needs; the DAL decides how to fetch it.
Business rules stay out of this interface on purpose:
- no weights: events and reactions come back raw, scoring decides their worth
- no "30 days": the caller passes `since`, the DAL just filters on it
"""

import uuid
from datetime import datetime
from typing import Protocol

from Backend.Logic.Algorithm.shared_types import StoryTags, TagScores
from Backend.Logic.domain.declared_tag import DeclaredTag
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.story import Story
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction


class AlgorithmRepository(Protocol):

    # ---- hourly job: reading a user's signals --------------------------------

    def list_consented_user_ids(self) -> list[uuid.UUID]:
        """Every user with analytics_consent = true."""
        ...

    def list_events_since(self, user_id: uuid.UUID, since: datetime) -> list[EngagementEvent]:
        """The user's engagement events with occurred_at >= since, any event type."""
        ...

    def list_reactions_since(self, user_id: uuid.UUID, since: datetime) -> list[StoryReaction]:
        """The user's current likes/dislikes with updated_at >= since."""
        ...

    def list_declared_tags(self, user_id: uuid.UUID) -> list[DeclaredTag]:
        """The user's declared tags (user_tags.is_declared), with when they were declared."""
        ...

    # ---- hourly job: saving the result -----------------------------------------

    def replace_tag_scores(self, user_id: uuid.UUID, scores: TagScores, computed_at: datetime) -> None:
        """Swap all of this user's stored tag scores for the new ones."""
        ...

    def delete_tag_scores_without_consent(self) -> None:
        """Remove stored scores of every user who no longer has consent."""
        ...

    # ---- reactions (design doc D2) -------------------------------------------------

    def set_reaction(
        self, user_id: uuid.UUID, story_id: uuid.UUID, reaction: Reaction, at: datetime
    ) -> StoryReaction:
        """Store the user's like/dislike on a story, replacing any earlier one."""
        ...

    def delete_reaction(self, user_id: uuid.UUID, story_id: uuid.UUID) -> None:
        """Unlike/undislike. Doing nothing when there is no reaction is fine."""
        ...

    # ---- consent withdrawn (design doc D3) ---------------------------------------

    def delete_algorithm_data(self, user_id: uuid.UUID) -> None:
        """Remove the user's reactions and tag scores straight away."""
        ...

    # ---- feed request ------------------------------------------------------------

    def get_tag_scores(self, user_id: uuid.UUID) -> TagScores:
        """The scores the last hourly run stored for this user (empty if none)."""
        ...

    def list_candidate_stories(self, since: datetime) -> list[Story]:
        """Published stories with last_updated_at >= since."""
        ...

    # ---- both ----------------------------------------------------------------------

    def get_story_tags(self, story_ids: list[uuid.UUID]) -> StoryTags:
        """Tag ids per story. Stories without tags may be missing from the result."""
        ...
