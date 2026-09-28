import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from Backend.dal.models import Story, StoryArticle, StoryStatus, StoryTag


class StoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, story_id: uuid.UUID, *, with_relations: bool = False) -> Story | None:
        if not with_relations:
            return self.db.get(Story, story_id)
        stmt = (
            select(Story)
            .where(Story.id == story_id)
            .options(selectinload(Story.tags), selectinload(Story.articles))
            .execution_options(populate_existing=True)
        )
        return self.db.scalars(stmt).first()

    def list(
        self,
        *,
        status: StoryStatus | None = None,
        tag_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Story]:
        stmt = select(Story)
        if status is not None:
            stmt = stmt.where(Story.status == status)
        if tag_id is not None:
            stmt = stmt.join(StoryTag).where(StoryTag.tag_id == tag_id)
        stmt = stmt.order_by(Story.last_updated_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def add(self, **fields: Any) -> Story:
        story = Story(**fields)
        self.db.add(story)
        self.db.flush()
        return story

    def update(self, story: Story, **fields: Any) -> Story:
        for key, value in fields.items():
            setattr(story, key, value)
        self.db.flush()
        return story

    # ---- story_tags ----

    def replace_tags(self, story: Story, tags: dict[uuid.UUID, Decimal | None]) -> None:
        """Replace the story's tags. `tags` maps tag_id -> relevance_score."""
        current = {st.tag_id: st for st in story.tags}

        for tag_id, story_tag in current.items():
            if tag_id not in tags:
                story.tags.remove(story_tag)  # delete-orphan removes the row
        for tag_id, score in tags.items():
            if tag_id in current:
                current[tag_id].relevance_score = score
            else:
                story.tags.append(StoryTag(tag_id=tag_id, relevance_score=score))
        self.db.flush()

    # ---- story_articles ----

    def get_article_link(self, story_id: uuid.UUID, article_id: uuid.UUID) -> StoryArticle | None:
        return self.db.get(StoryArticle, (story_id, article_id))

    def add_article_link(self, **fields: Any) -> StoryArticle:
        link = StoryArticle(**fields)
        self.db.add(link)
        self.db.flush()
        return link

    def clear_primary(self, story_id: uuid.UUID) -> None:
        """Unset is_primary on every article of this story."""
        self.db.execute(
            update(StoryArticle)
            .where(StoryArticle.story_id == story_id, StoryArticle.is_primary.is_(True))
            .values(is_primary=False)
        )

    def remove_article_link(self, link: StoryArticle) -> None:
        self.db.delete(link)
        self.db.flush()
