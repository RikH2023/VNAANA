"""In-memory stand-ins for the ports, used instead of the database.

They offer the same methods as the real DAL classes, so the services can't
tell the difference. That is the dependency inversion paying off: the Logic
layer can be tested without Supabase, SQLite or any setup.
"""

import dataclasses
import uuid
from datetime import datetime

from Backend.Logic.Algorithm.shared_types import StoryTags, TagScores
from Backend.Logic.domain.declared_tag import DeclaredTag
from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.story import Story, StoryStatus
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction
from Backend.Logic.domain.user import User


class FakeAlgorithmRepository:
    """Implements Backend.Logic.ports.algorithm_repository.AlgorithmRepository."""

    def __init__(self) -> None:
        self.consent: dict[uuid.UUID, bool] = {}
        self.events: list[EngagementEvent] = []
        self.reactions: dict[tuple[uuid.UUID, uuid.UUID], StoryReaction] = {}
        self.declared_tags: dict[uuid.UUID, list[DeclaredTag]] = {}
        self.story_tags: StoryTags = {}
        self.stories: list[Story] = []
        self.scores: dict[uuid.UUID, TagScores] = {}
        self.data_deleted_for: list[uuid.UUID] = []

    # ---- helpers for tests ---------------------------------------------------

    def add_user(self, user: User) -> None:
        self.consent[user.id] = user.analytics_consent

    def add_story(self, story: Story, tag_ids: list[uuid.UUID]) -> Story:
        self.stories.append(story)
        self.story_tags[story.id] = list(tag_ids)
        return story

    # ---- the port ------------------------------------------------------------

    def list_consented_user_ids(self) -> list[uuid.UUID]:
        return [user_id for user_id, consent in self.consent.items() if consent]

    def list_events_since(self, user_id: uuid.UUID, since: datetime) -> list[EngagementEvent]:
        return [e for e in self.events if e.user_id == user_id and e.occurred_at >= since]

    def list_reactions_since(self, user_id: uuid.UUID, since: datetime) -> list[StoryReaction]:
        return [r for r in self.reactions.values() if r.user_id == user_id and r.updated_at >= since]

    def list_declared_tags(self, user_id: uuid.UUID) -> list[DeclaredTag]:
        return list(self.declared_tags.get(user_id, []))

    def replace_tag_scores(self, user_id: uuid.UUID, scores: TagScores, computed_at: datetime) -> None:
        self.scores[user_id] = dict(scores)

    def delete_tag_scores_without_consent(self) -> None:
        for user_id in [u for u in self.scores if not self.consent.get(u, False)]:
            del self.scores[user_id]

    def set_reaction(
        self, user_id: uuid.UUID, story_id: uuid.UUID, reaction: Reaction, at: datetime
    ) -> StoryReaction:
        stored = StoryReaction(user_id=user_id, story_id=story_id, reaction=reaction, updated_at=at)
        self.reactions[(user_id, story_id)] = stored
        return stored

    def delete_reaction(self, user_id: uuid.UUID, story_id: uuid.UUID) -> None:
        self.reactions.pop((user_id, story_id), None)

    def delete_algorithm_data(self, user_id: uuid.UUID) -> None:
        self.data_deleted_for.append(user_id)
        self.scores.pop(user_id, None)
        for key in [k for k in self.reactions if k[0] == user_id]:
            del self.reactions[key]

    def get_tag_scores(self, user_id: uuid.UUID) -> TagScores:
        return dict(self.scores.get(user_id, {}))

    def list_candidate_stories(self, since: datetime) -> list[Story]:
        return [
            s for s in self.stories
            if s.status == StoryStatus.published and s.last_updated_at >= since
        ]

    def get_story_tags(self, story_ids: list[uuid.UUID]) -> StoryTags:
        return {sid: self.story_tags[sid] for sid in story_ids if sid in self.story_tags}


class FakeUserRepository:
    """The two methods of the UserRepository port that the services use."""

    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    def add(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    def update(self, user: User, **fields) -> User:
        updated = dataclasses.replace(user, **fields)
        self.users[user.id] = updated
        return updated


class FakeStoryRepository:
    """Only get(): UserService uses it to check a story exists before a reaction."""

    def __init__(self, stories: list[Story]) -> None:
        self.stories = stories

    def get(self, story_id: uuid.UUID) -> Story | None:
        return next((s for s in self.stories if s.id == story_id), None)
