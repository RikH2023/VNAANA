import uuid
from datetime import datetime, timezone
from typing import Any

from Backend.Logic.domain.engagement_event import EngagementEvent
from Backend.Logic.domain.story_reaction import Reaction, StoryReaction
from Backend.Logic.domain.user import User
from Backend.Logic.exceptions import ConsentRequiredError, NotFoundError
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.engagement_event_repository import (
    EngagementEventRepository,
)
from Backend.Logic.ports.story_repository import StoryRepository
from Backend.Logic.ports.tag_repository import TagRepository
from Backend.Logic.ports.user_repository import UserRepository
from Backend.Logic.ports.algorithm_repository import AlgorithmRepository



class UserService:
    def __init__(
        self,
        users: UserRepository,
        tags: TagRepository,
        events: EngagementEventRepository,
        stories: StoryRepository,
        articles: ArticleRepository,
        algorithm: AlgorithmRepository,
    ):
        self.users = users
        self.tags = tags
        self.events = events
        self.stories = stories
        self.articles = articles
        self.algorithm = algorithm

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def get_user(
        self,
        user_id: uuid.UUID,
    ) -> User:
        user = self.users.get(user_id)

        if user is None:
            raise NotFoundError("User", user_id)

        return user

    def create_user(
        self,
        data: dict[str, Any],
    ) -> User:
        if data.get("analytics_consent"):
            data["consent_updated_at"] = datetime.now(timezone.utc)

        return self.users.add(**data)

    def get_authenticated_user(self, subject: uuid.UUID) -> User:
        """Resolve an existing application profile without creating one on reads."""
        user = self.users.get_by_identity("supabase", str(subject))
        if user is None:
            raise NotFoundError("User", subject)
        return user

    def get_or_create_authenticated_user(
        self,
        subject: uuid.UUID,
    ) -> User:
        return self.users.get_or_create_by_identity(
            auth_provider="supabase",
            auth_subject=str(subject),
        )

    def update_user(
        self,
        user_id: uuid.UUID,
        changes: dict[str, Any],
    ) -> User:
        user = self.get_user(user_id)

        return self.users.update(
            user,
            **changes,
        )

    def set_consent(
            self,
            user_id: uuid.UUID,
            consent: bool,
    ) -> User:
        user = self.get_user(user_id)

        if user.analytics_consent != consent:
            user = self.users.update(
                user,
                analytics_consent=consent,
                consent_updated_at=datetime.now(timezone.utc),
            )

            if not consent:
                # Consent went from on to off. Reactions and tag scores only
                # exist while consent is on, so this is exactly when there is
                # data to remove (design doc D3).
                self.algorithm.delete_algorithm_data(user_id)

        return user

    def delete_user(
        self,
        user_id: uuid.UUID,
    ) -> None:
        user = self.get_user(user_id)

        self.users.delete(user)

    # ------------------------------------------------------------------
    # Interests / user_tags
    # ------------------------------------------------------------------

    def get_tags(
        self,
        user_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        self.get_user(user_id)

        return self.users.get_tag_ids(user_id)

    def set_tags(
        self,
        user_id: uuid.UUID,
        tag_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        user = self.get_user(user_id)

        found = {
            tag.id
            for tag in self.tags.get_many(tag_ids)
        }

        missing = [
            tag_id
            for tag_id in tag_ids
            if tag_id not in found
        ]

        if missing:
            raise NotFoundError(
                "Tag",
                ", ".join(map(str, missing)),
            )

        return self.users.replace_tags(
            user,
            tag_ids,
        )

    # ------------------------------------------------------------------
    # Engagement events
    # ------------------------------------------------------------------

    def log_event(
        self,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> EngagementEvent:
        user = self.get_user(user_id)

        if not user.analytics_consent:
            raise ConsentRequiredError(
                "User has not given analytics consent"
            )

        story_id = data.get("story_id")

        if story_id and self.stories.get(story_id) is None:
            raise NotFoundError(
                "Story",
                story_id,
            )

        article_id = data.get("article_id")

        if article_id and self.articles.get(article_id) is None:
            raise NotFoundError(
                "Article",
                article_id,
            )

        if data.get("occurred_at") is None:
            data.pop("occurred_at", None)

        if "metadata" in data:
            data["event_metadata"] = data.pop("metadata")

        return self.events.add(
            user_id=user_id,
            **data,
        )

    def list_events(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> list[EngagementEvent]:
        self.get_user(user_id)

        return self.events.list_for_user(
            user_id,
            limit=limit,
            offset=offset,
        )

    # ------------------------------------------------------------------
    # Reactions (design doc D2)
    # ------------------------------------------------------------------

    def set_reaction(
        self,
        user_id: uuid.UUID,
        story_id: uuid.UUID,
        reaction: Reaction,
    ) -> StoryReaction:
        user = self.get_user(user_id)

        # Same rule as events: no consent, nothing is stored (design doc D3).
        if not user.analytics_consent:
            raise ConsentRequiredError(
                "User has not given analytics consent"
            )

        if self.stories.get(story_id) is None:
            raise NotFoundError(
                "Story",
                story_id,
            )

        return self.algorithm.set_reaction(
            user_id,
            story_id,
            reaction,
            datetime.now(timezone.utc),
        )

    def remove_reaction(
        self,
        user_id: uuid.UUID,
        story_id: uuid.UUID,
    ) -> None:
        # No consent check: removing data is always allowed.
        self.get_user(user_id)

        self.algorithm.delete_reaction(
            user_id,
            story_id,
        )
