""" /stories endpoints. Plain `def` on purpose, see routers/users.py. """

import uuid

from fastapi import APIRouter, Query, status

from Backend.Logic.domain.story import StoryStatus
from Backend.Presentation.dependencies import StoryServiceDep
from Backend.Presentation.schemas.stories import (
    StoryArticleLink,
    StoryArticleRead,
    StoryCreate,
    StoryListItem,
    StoryRead,
    StoryTagsUpdate,
    StoryUpdate,
)

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=list[StoryListItem])
def list_stories(
    service: StoryServiceDep,
    status_filter: StoryStatus | None = Query(
        StoryStatus.published,
        alias="status",
    ),
    tag_id: uuid.UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return service.list_stories(
        status=status_filter,
        tag_id=tag_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=StoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_story(
    body: StoryCreate,
    service: StoryServiceDep,
):
    return service.create_story(
        body.model_dump(),
    )


@router.get("/{story_id}", response_model=StoryRead)
def get_story(
    story_id: uuid.UUID,
    service: StoryServiceDep,
):
    return service.get_story(story_id)


@router.patch("/{story_id}", response_model=StoryRead)
def update_story(
    story_id: uuid.UUID,
    body: StoryUpdate,
    service: StoryServiceDep,
):
    return service.update_story(
        story_id,
        body.model_dump(exclude_unset=True),
    )


@router.put("/{story_id}/tags", response_model=StoryRead)
def set_story_tags(
    story_id: uuid.UUID,
    body: StoryTagsUpdate,
    service: StoryServiceDep,
):
    tag_data = {
        tag.tag_id: tag.relevance_score
        for tag in body.tags
    }

    return service.set_tags(
        story_id,
        tag_data,
    )


@router.post(
    "/{story_id}/articles",
    response_model=StoryArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def link_article(
    story_id: uuid.UUID,
    body: StoryArticleLink,
    service: StoryServiceDep,
):
    return service.link_article(
        story_id,
        body.article_id,
        body.similarity_score,
        body.is_primary,
    )


@router.delete(
    "/{story_id}/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unlink_article(
    story_id: uuid.UUID,
    article_id: uuid.UUID,
    service: StoryServiceDep,
):
    service.unlink_article(
        story_id,
        article_id,
    )