import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from Backend.dal.models import Story, StoryArticle, StoryStatus
from Backend.dal.models.base import utcnow
from Backend.dal.repositories import ArticleRepository, StoryRepository, TagRepository
from Backend.logic.exceptions import ConflictError, NotFoundError


class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self.stories = StoryRepository(db)
        self.tags = TagRepository(db)
        self.articles = ArticleRepository(db)

    def list_stories(
        self,
        status: StoryStatus | None,
        tag_id: uuid.UUID | None,
        limit: int,
        offset: int,
    ) -> list[Story]:
        return self.stories.list(status=status, tag_id=tag_id, limit=limit, offset=offset)

    def get_story(self, story_id: uuid.UUID) -> Story:
        story = self.stories.get(story_id, with_relations=True)
        if story is None:
            raise NotFoundError("Story", story_id)
        return story

    def create_story(self, data: dict[str, Any]) -> Story:
        if data.get("status") == StoryStatus.published:
            data["first_published_at"] = utcnow()
        story = self.stories.add(**data)
        self.db.commit()
        return self.get_story(story.id)

    def update_story(self, story_id: uuid.UUID, changes: dict[str, Any]) -> Story:
        story = self.get_story(story_id)

        # first_published_at is set once, the first time a story goes live.
        if changes.get("status") == StoryStatus.published and story.first_published_at is None:
            changes["first_published_at"] = utcnow()

        self.stories.update(story, **changes, last_updated_at=utcnow())
        self.db.commit()
        return self.get_story(story_id)

    def set_tags(self, story_id: uuid.UUID, tags: dict[uuid.UUID, float | None]) -> Story:
        story = self.get_story(story_id)
        found = {tag.id for tag in self.tags.get_many(list(tags))}
        missing = [tid for tid in tags if tid not in found]
        if missing:
            raise NotFoundError("Tag", ", ".join(map(str, missing)))

        scores = {tid: (Decimal(str(s)) if s is not None else None) for tid, s in tags.items()}
        self.stories.replace_tags(story, scores)
        self.db.commit()
        return self.get_story(story_id)

    def link_article(
        self,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
        similarity_score: float | None,
        is_primary: bool,
    ) -> StoryArticle:
        story = self.get_story(story_id)
        if self.articles.get(article_id) is None:
            raise NotFoundError("Article", article_id)
        if self.stories.get_article_link(story_id, article_id) is not None:
            raise ConflictError("Article is already linked to this story")

        # A story has at most one primary article.
        if is_primary:
            self.stories.clear_primary(story_id)

        link = self.stories.add_article_link(
            story_id=story_id,
            article_id=article_id,
            similarity_score=Decimal(str(similarity_score)) if similarity_score is not None else None,
            is_primary=is_primary,
        )
        # New coverage means the story changed.
        self.stories.update(story, last_updated_at=utcnow())
        self.db.commit()
        return link

    def unlink_article(self, story_id: uuid.UUID, article_id: uuid.UUID) -> None:
        link = self.stories.get_article_link(story_id, article_id)
        if link is None:
            raise NotFoundError("Story article link", f"{story_id}/{article_id}")
        self.stories.remove_article_link(link)
        self.db.commit()
