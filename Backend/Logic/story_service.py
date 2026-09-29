import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from Backend.Logic.domain.story import Story, StoryStatus
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.story_repository import StoryRepository
from Backend.Logic.ports.tag_repository import TagRepository
from Backend.Logic.exceptions import ConflictError, NotFoundError


class StoryService:
    def list_stories(
        self,
        stories: StoryRepository,
        *,
        status: StoryStatus | None = None,
        tag_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Story]:
        return stories.list(
            status=status,
            tag_id=tag_id,
            limit=limit,
            offset=offset,
        )

    def get_story(
        self,
        stories: StoryRepository,
        story_id: uuid.UUID,
    ) -> Story:
        story = stories.get(story_id)

        if story is None:
            raise NotFoundError("Story", story_id)

        return story

    def create_story(
        self,
        stories: StoryRepository,
        data: dict[str, Any],
    ) -> Story:
        if data.get("status") == StoryStatus.published:
            data["first_published_at"] = datetime.now(timezone.utc)

        story = stories.add(**data)

        return self.get_story(stories, story.id)

    def update_story(
        self,
        stories: StoryRepository,
        story_id: uuid.UUID,
        changes: dict[str, Any],
    ) -> Story:
        story = self.get_story(stories, story_id)

        # first_published_at is set once, the first time a story goes live.
        if (
            changes.get("status") == StoryStatus.published
            and story.first_published_at is None
        ):
            changes["first_published_at"] = datetime.now(timezone.utc)

        stories.update(
            story,
            **changes,
            last_updated_at=datetime.now(timezone.utc),
        )

        return self.get_story(stories, story_id)

    def set_tags(
        self,
        stories: StoryRepository,
        tags_repository: TagRepository,
        story_id: uuid.UUID,
        tags: dict[uuid.UUID, float | None],
    ) -> Story:
        story = self.get_story(stories, story_id)

        found = {
            tag.id
            for tag in tags_repository.get_many(list(tags))
        }

        missing = [
            tag_id
            for tag_id in tags
            if tag_id not in found
        ]

        if missing:
            raise NotFoundError(
                "Tag",
                ", ".join(map(str, missing)),
            )

        scores = {
            tag_id: Decimal(str(score)) if score is not None else None
            for tag_id, score in tags.items()
        }

        stories.replace_tags(story, scores)

        return self.get_story(stories, story_id)

    def link_article(
        self,
        stories: StoryRepository,
        articles: ArticleRepository,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
        similarity_score: float | None,
        is_primary: bool,
    ):
        story = self.get_story(stories, story_id)

        if articles.get(article_id) is None:
            raise NotFoundError("Article", article_id)

        if stories.get_article_link(story_id, article_id) is not None:
            raise ConflictError(
                "Article is already linked to this story"
            )

        # A story has at most one primary article.
        if is_primary:
            stories.clear_primary(story_id)

        link = stories.add_article_link(
            story_id=story_id,
            article_id=article_id,
            similarity_score=(
                Decimal(str(similarity_score))
                if similarity_score is not None
                else None
            ),
            is_primary=is_primary,
        )

        # New coverage means the story changed.
        stories.update(
            story,
            last_updated_at=datetime.now(timezone.utc),
        )

        return link

    def unlink_article(
        self,
        stories: StoryRepository,
        story_id: uuid.UUID,
        article_id: uuid.UUID,
    ) -> None:
        link = stories.get_article_link(
            story_id,
            article_id,
        )

        if link is None:
            raise NotFoundError(
                "Story article link",
                f"{story_id}/{article_id}",
            )

        stories.remove_article_link(
            story_id,
            article_id,
        )