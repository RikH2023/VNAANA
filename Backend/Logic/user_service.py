import uuid
from typing import Any

from sqlalchemy.orm import Session

from Backend.dal.models import EngagementEvent, User, UserTag
from Backend.dal.models.base import utcnow
from Backend.dal.repositories import (
    ArticleRepository,
    EngagementEventRepository,
    StoryRepository,
    TagRepository,
    UserRepository,
)
from Backend.logic.exceptions import ConsentRequiredError, NotFoundError


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tags = TagRepository(db)
        self.events = EngagementEventRepository(db)
        self.stories = StoryRepository(db)
        self.articles = ArticleRepository(db)

    # ---- users ----

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("User", user_id)
        return user

    def create_user(self, data: dict[str, Any]) -> User:
        # Record when consent was given, so we can show when it was agreed to.
        if data.get("analytics_consent"):
            data["consent_updated_at"] = utcnow()
        user = self.users.add(**data)
        self.db.commit()
        return user

    def update_user(self, user_id: uuid.UUID, changes: dict[str, Any]) -> User:
        user = self.get_user(user_id)
        self.users.update(user, **changes)
        self.db.commit()
        return user

    def set_consent(self, user_id: uuid.UUID, consent: bool) -> User:
        user = self.get_user(user_id)
        if user.analytics_consent != consent:
            self.users.update(user, analytics_consent=consent, consent_updated_at=utcnow())
            self.db.commit()
        return user

    def delete_user(self, user_id: uuid.UUID) -> None:
        user = self.get_user(user_id)
        self.users.delete(user)
        self.db.commit()

    # ---- interests (user_tags) ----

    def get_tags(self, user_id: uuid.UUID) -> list[UserTag]:
        self.get_user(user_id)
        return self.users.get_tags(user_id)

    def set_tags(self, user_id: uuid.UUID, tag_ids: list[uuid.UUID]) -> list[UserTag]:
        user = self.get_user(user_id)
        found = {tag.id for tag in self.tags.get_many(tag_ids)}
        missing = [tid for tid in tag_ids if tid not in found]
        if missing:
            raise NotFoundError("Tag", ", ".join(map(str, missing)))
        user_tags = self.users.replace_tags(user, tag_ids)
        self.db.commit()
        return user_tags

    # ---- engagement events ----

    def log_event(self, user_id: uuid.UUID, data: dict[str, Any]) -> EngagementEvent:
        user = self.get_user(user_id)
        # Behaviour tracking needs explicit consent (GDPR). Without it we don't
        # store anything tied to this user.
        if not user.analytics_consent:
            raise ConsentRequiredError("User has not given analytics consent")

        if data.get("story_id") and self.stories.get(data["story_id"]) is None:
            raise NotFoundError("Story", data["story_id"])
        if data.get("article_id") and self.articles.get(data["article_id"]) is None:
            raise NotFoundError("Article", data["article_id"])

        if data.get("occurred_at") is None:
            data.pop("occurred_at", None)  # let the model default fill in "now"
        if "metadata" in data:
            data["event_metadata"] = data.pop("metadata")

        event = self.events.add(user_id=user_id, **data)
        self.db.commit()
        return event

    def list_events(self, user_id: uuid.UUID, limit: int, offset: int) -> list[EngagementEvent]:
        self.get_user(user_id)
        return self.events.list_for_user(user_id, limit=limit, offset=offset)
