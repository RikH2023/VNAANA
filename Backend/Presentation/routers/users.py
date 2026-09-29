""" /users endpoints.

All endpoints are plain `def` on purpose: the SQLAlchemy session is
synchronous, and FastAPI runs plain def endpoints in a threadpool so a DB call
doesn't block the event loop (see ADR: FastAPI as Web Framework).
"""

import uuid

from fastapi import APIRouter, Query, status

from Backend.Presentation.dependencies import (
    ArticleRepositoryDep,
    EngagementEventRepositoryDep,
    StoryRepositoryDep,
    TagRepositoryDep,
    UserRepositoryDep,
    UserServiceDep,
)
from Backend.Presentation.schemas.users import (
    ConsentUpdate,
    EngagementEventCreate,
    EngagementEventRead,
    UserCreate,
    UserRead,
    UserTagRead,
    UserTagsUpdate,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    body: UserCreate,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    return service.create_user(
        users,
        body.model_dump(),
    )


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    return service.get_user(
        users,
        user_id,
    )


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    # exclude_unset: only change the fields that were actually sent
    return service.update_user(
        users,
        user_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: uuid.UUID,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    service.delete_user(
        users,
        user_id,
    )


@router.put("/{user_id}/consent", response_model=UserRead)
def set_consent(
    user_id: uuid.UUID,
    body: ConsentUpdate,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    return service.set_consent(
        users,
        user_id,
        body.analytics_consent,
    )


@router.get(
    "/{user_id}/tags",
    response_model=list[UserTagRead],
)
def get_user_tags(
    user_id: uuid.UUID,
    service: UserServiceDep,
    users: UserRepositoryDep,
):
    return service.get_tags(
        users,
        user_id,
    )


@router.put(
    "/{user_id}/tags",
    response_model=list[UserTagRead],
)
def set_user_tags(
    user_id: uuid.UUID,
    body: UserTagsUpdate,
    service: UserServiceDep,
    users: UserRepositoryDep,
    tags: TagRepositoryDep,
):
    return service.set_tags(
        users,
        tags,
        user_id,
        body.tag_ids,
    )


@router.post(
    "/{user_id}/events",
    response_model=EngagementEventRead,
    status_code=status.HTTP_201_CREATED,
)
def log_event(
    user_id: uuid.UUID,
    body: EngagementEventCreate,
    service: UserServiceDep,
    users: UserRepositoryDep,
    events: EngagementEventRepositoryDep,
    stories: StoryRepositoryDep,
    articles: ArticleRepositoryDep,
):
    return service.log_event(
        users,
        events,
        stories,
        articles,
        user_id,
        body.model_dump(),
    )


@router.get(
    "/{user_id}/events",
    response_model=list[EngagementEventRead],
)
def list_events(
    user_id: uuid.UUID,
    service: UserServiceDep,
    users: UserRepositoryDep,
    events: EngagementEventRepositoryDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_events(
        users,
        events,
        user_id,
        limit,
        offset,
    )