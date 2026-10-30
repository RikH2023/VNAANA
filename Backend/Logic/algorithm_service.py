"""Runs the algorithm: the hourly scoring job and the "For you" feed.

This service decides WHO and WHEN; the Algorithm package decides HOW MUCH.
It only talks to storage through the AlgorithmRepository port, so it works
the same against Supabase, SQLite or an in-memory fake.
The caller owns the transaction (commit/rollback), like the other services.
"""

import uuid
from datetime import datetime, timedelta, timezone

from Backend.Logic.Algorithm.decay import LIFETIME_DAYS
from Backend.Logic.Algorithm.ranking import is_unlocked, rank_stories
from Backend.Logic.Algorithm.scoring import score_user
from Backend.Logic.domain.feed import Feed, FeedStatus
from Backend.Logic.exceptions import NotFoundError
from Backend.Logic.ports.algorithm_repository import AlgorithmRepository
from Backend.Logic.ports.user_repository import UserRepository


class AlgorithmService:
    def __init__(
        self,
        algorithm: AlgorithmRepository,
        users: UserRepository,
    ):
        self.algorithm = algorithm
        self.users = users

    # ------------------------------------------------------------------
    # Hourly job (design doc D11)
    # ------------------------------------------------------------------

    def run_scoring(self, now: datetime | None = None) -> int:
        """Recompute and store the tag scores of every consented user.

        Returns how many users were scored. `now` is a parameter so a test
        can pin the clock; the job itself leaves it empty.
        """
        now = now or datetime.now(timezone.utc)
        since = now - timedelta(days=LIFETIME_DAYS)

        # Consent can be withdrawn between runs: clean those scores up first.
        self.algorithm.delete_tag_scores_without_consent()

        user_ids = self.algorithm.list_consented_user_ids()

        for user_id in user_ids:
            events = self.algorithm.list_events_since(user_id, since)
            reactions = self.algorithm.list_reactions_since(user_id, since)
            declared_tags = self.algorithm.list_declared_tags(user_id)

            story_ids = {event.story_id for event in events if event.story_id is not None}
            story_ids |= {reaction.story_id for reaction in reactions}
            story_tags = self.algorithm.get_story_tags(list(story_ids))

            scores = score_user(events, reactions, declared_tags, story_tags, now)
            self.algorithm.replace_tag_scores(user_id, scores, now)

        return len(user_ids)

    # ------------------------------------------------------------------
    # "For you" feed (design doc D3, D10, D12)
    # ------------------------------------------------------------------

    def get_feed(
        self,
        user_id: uuid.UUID | None,
        *,
        limit: int = 20,
        offset: int = 0,
        now: datetime | None = None,
    ) -> Feed:
        """Personalised stories, or the reason there aren't any."""
        if user_id is None:
            return Feed(FeedStatus.not_logged_in)

        user = self.users.get(user_id)

        if user is None:
            raise NotFoundError("User", user_id)

        if not user.analytics_consent:
            return Feed(FeedStatus.no_consent)

        tag_scores = self.algorithm.get_tag_scores(user_id)

        if not is_unlocked(tag_scores):
            return Feed(FeedStatus.locked)

        now = now or datetime.now(timezone.utc)
        stories = self.algorithm.list_candidate_stories(now - timedelta(days=LIFETIME_DAYS))
        story_tags = self.algorithm.get_story_tags([story.id for story in stories])

        ranked = rank_stories(stories, story_tags, tag_scores, now)

        return Feed(FeedStatus.available, ranked[offset:offset + limit])
