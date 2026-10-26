"""DAL implementation of the AlgorithmRepository port.

Storage layout (live Supabase schema, migration 83fdcb1cc3fc):
- tag scores live in user_tags.score / computed_at. A row is either a declared
  interest (is_declared = true) or a tag the algorithm scored (is_declared = false).
- users.affinity_updated_at records when the user was last scored.
- reactions live in story_reactions.

This class only stores and fetches. Weights, decay and ranking are decided in
Backend/Logic/Algorithm.
"""

import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from Backend.Dal.models import (
    EngagementEvent as EngagementEventModel,
    Story as StoryModel,
    StoryReaction as StoryReactionModel,
    StoryStatus,
    StoryTag as StoryTagModel,
    User as UserModel,
    UserTag as UserTagModel,
)
from Backend.Dal.repositories.engagement_event_repository import EngagementEventRepository
from Backend.Dal.repositories.story_repository import StoryRepository
from Backend.Logic.Algorithm.shared_types import StoryTags, TagScores
from Backend.Logic.domain.declared_tag import DeclaredTag
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.story import Story
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction
from Backend.Logic.ports.algorithm_repository import (
    AlgorithmRepository as AlgorithmRepositoryPort,
)


class AlgorithmRepository(AlgorithmRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _reaction_to_domain(row: StoryReactionModel) -> StoryReaction:
        return StoryReaction(
            user_id=row.user_id,
            story_id=row.story_id,
            reaction=Reaction(row.reaction),
            updated_at=row.updated_at,
        )

    # ---- hourly job: reading a user's signals --------------------------------

    def list_consented_user_ids(self) -> list[uuid.UUID]:
        stmt = select(UserModel.id).where(UserModel.analytics_consent.is_(True))

        return list(self.db.scalars(stmt))

    def list_events_since(self, user_id: uuid.UUID, since: datetime) -> list[EngagementEvent]:
        # Uses the (user_id, occurred_at) index from Hanh's migration.
        stmt = select(EngagementEventModel).where(
            EngagementEventModel.user_id == user_id,
            EngagementEventModel.occurred_at >= since,
        )

        # Same mapping as the events endpoint, so there is only one to maintain.
        return [EngagementEventRepository._to_domain(event) for event in self.db.scalars(stmt)]

    def list_reactions_since(self, user_id: uuid.UUID, since: datetime) -> list[StoryReaction]:
        stmt = select(StoryReactionModel).where(
            StoryReactionModel.user_id == user_id,
            StoryReactionModel.updated_at >= since,
        )

        return [self._reaction_to_domain(row) for row in self.db.scalars(stmt)]

    def list_declared_tags(self, user_id: uuid.UUID) -> list[DeclaredTag]:
        stmt = select(UserTagModel.tag_id, UserTagModel.updated_at).where(
            UserTagModel.user_id == user_id,
            UserTagModel.is_declared.is_(True),
        )

        return [
            DeclaredTag(tag_id=tag_id, declared_at=updated_at)
            for tag_id, updated_at in self.db.execute(stmt)
        ]

    # ---- hourly job: saving the result -----------------------------------------

    def replace_tag_scores(self, user_id: uuid.UUID, scores: TagScores, computed_at: datetime) -> None:
        rows = {
            row.tag_id: row
            for row in self.db.scalars(select(UserTagModel).where(UserTagModel.user_id == user_id))
        }

        for tag_id, row in rows.items():
            if tag_id in scores:
                row.score = scores[tag_id]
                row.computed_at = computed_at
            elif row.is_declared:
                # Declared interests stay, they just have no score this run.
                row.score = 0.0
                row.computed_at = computed_at
            else:
                # Only existed to hold a score that is gone now.
                self.db.delete(row)

        for tag_id, score in scores.items():
            if tag_id not in rows:
                self.db.add(
                    UserTagModel(
                        user_id=user_id,
                        tag_id=tag_id,
                        is_declared=False,
                        score=score,
                        computed_at=computed_at,
                    )
                )

        user = self.db.get(UserModel, user_id)

        if user is not None:
            user.affinity_updated_at = computed_at

        self.db.flush()

    def delete_tag_scores_without_consent(self) -> None:
        no_consent = select(UserModel.id).where(UserModel.analytics_consent.is_(False))

        self._clear_scores(UserTagModel.user_id.in_(no_consent))
        self.db.execute(
            update(UserModel)
            .where(UserModel.analytics_consent.is_(False), UserModel.affinity_updated_at.is_not(None))
            .values(affinity_updated_at=None)
        )
        self.db.flush()

    def _clear_scores(self, which_users) -> None:
        """Drop score-only rows; keep declared interests but wipe their score."""
        self.db.execute(
            delete(UserTagModel).where(which_users, UserTagModel.is_declared.is_(False)),
            execution_options={"synchronize_session": "fetch"},
        )
        self.db.execute(
            update(UserTagModel)
            .where(which_users, UserTagModel.is_declared.is_(True))
            .values(score=0.0, computed_at=None),
            execution_options={"synchronize_session": "fetch"},
        )

    # ---- reactions (design doc D2) -------------------------------------------------

    def set_reaction(
        self, user_id: uuid.UUID, story_id: uuid.UUID, reaction: Reaction, at: datetime
    ) -> StoryReaction:
        row = self.db.get(StoryReactionModel, (user_id, story_id))

        if row is None:
            row = StoryReactionModel(
                user_id=user_id,
                story_id=story_id,
                reaction=reaction.value,
                updated_at=at,
            )
            self.db.add(row)
        else:
            row.reaction = reaction.value
            row.updated_at = at

        self.db.flush()

        return self._reaction_to_domain(row)

    def delete_reaction(self, user_id: uuid.UUID, story_id: uuid.UUID) -> None:
        self.db.execute(
            delete(StoryReactionModel).where(
                StoryReactionModel.user_id == user_id,
                StoryReactionModel.story_id == story_id,
            )
        )
        self.db.flush()

    # ---- consent withdrawn (design doc D3) ---------------------------------------

    def delete_algorithm_data(self, user_id: uuid.UUID) -> None:
        self.db.execute(delete(StoryReactionModel).where(StoryReactionModel.user_id == user_id))
        self._clear_scores(UserTagModel.user_id == user_id)

        user = self.db.get(UserModel, user_id)

        if user is not None:
            user.affinity_updated_at = None

        self.db.flush()

    # ---- feed request ------------------------------------------------------------

    def get_tag_scores(self, user_id: uuid.UUID) -> TagScores:
        # computed_at IS NULL means "declared, never scored yet": not a real score.
        stmt = select(UserTagModel.tag_id, UserTagModel.score).where(
            UserTagModel.user_id == user_id,
            UserTagModel.computed_at.is_not(None),
        )

        return {tag_id: score for tag_id, score in self.db.execute(stmt)}

    def list_candidate_stories(self, since: datetime) -> list[Story]:
        stmt = select(StoryModel).where(
            StoryModel.status == StoryStatus.published,
            StoryModel.last_updated_at >= since,
        )

        return [StoryRepository._to_domain(story) for story in self.db.scalars(stmt)]

    # ---- both ----------------------------------------------------------------------

    def get_story_tags(self, story_ids: list[uuid.UUID]) -> StoryTags:
        if not story_ids:
            return {}

        stmt = select(StoryTagModel.story_id, StoryTagModel.tag_id).where(
            StoryTagModel.story_id.in_(story_ids)
        )

        result: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)

        for story_id, tag_id in self.db.execute(stmt):
            result[story_id].append(tag_id)

        return dict(result)
