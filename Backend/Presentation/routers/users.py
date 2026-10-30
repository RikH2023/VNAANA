""" /users endpoints.

All endpoints are plain `def` on purpose: the SQLAlchemy session is
synchronous, and FastAPI runs plain def endpoints in a threadpool so a DB call
doesn't block the event loop (see ADR: FastAPI as Web Framework).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from Backend.Presentation.dependencies import UserServiceDep
from Backend.Presentation.schemas.users import (
    ConsentUpdate,
    EngagementEventCreate,
    EngagementEventRead,
    ReactionUpdate,
    StoryReactionRead,
    UserRead,
    UserTagsUpdate,
    UserUpdate,
)
from Backend.Presentation.auth import AuthenticatedSubject

router = APIRouter(prefix="/users", tags=["users"])


def require_user_owner(
    user_id: uuid.UUID,
    subject: AuthenticatedSubject,
    service: UserServiceDep,
) -> None:
    """Allow access only when the profile belongs to the verified identity."""
    user = service.get_user(user_id)

    if (
        user.auth_provider != "supabase"
        or user.auth_subject != str(subject)
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot access another user's profile.",
        )


@router.post(
    "/me/bootstrap",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def bootstrap_user(
    subject: AuthenticatedSubject,
    service: UserServiceDep,
):
    return service.get_or_create_authenticated_user(subject)

@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_user_owner)],
)
def get_user(
    user_id: uuid.UUID,
    service: UserServiceDep,
):
    return service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_user_owner)])
def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    service: UserServiceDep,
):
    return service.update_user(
        user_id,
        body.model_dump(exclude_unset=True),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_user_owner)],
)
def delete_user(
    user_id: uuid.UUID,
    service: UserServiceDep,
):
    service.delete_user(user_id)


@router.put("/{user_id}/consent", response_model=UserRead, dependencies=[Depends(require_user_owner)])
def set_consent(
    user_id: uuid.UUID,
    body: ConsentUpdate,
    service: UserServiceDep,
):
    return service.set_consent(
        user_id,
        body.analytics_consent,
    )


@router.get(
    "/{user_id}/tags",
    response_model=list[uuid.UUID],
    dependencies=[Depends(require_user_owner)],
)
def get_user_tags(
    user_id: uuid.UUID,
    service: UserServiceDep,
):
    return service.get_tags(user_id)


@router.put(
    "/{user_id}/tags",
    response_model=list[uuid.UUID],
    dependencies=[Depends(require_user_owner)],
)
def set_user_tags(
    user_id: uuid.UUID,
    body: UserTagsUpdate,
    service: UserServiceDep,
):
    return service.set_tags(
        user_id,
        body.tag_ids,
    )


@router.post(
    "/{user_id}/events",
    response_model=EngagementEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_user_owner)],
)
def log_event(
    user_id: uuid.UUID,
    body: EngagementEventCreate,
    service: UserServiceDep,
):
    return service.log_event(
        user_id,
        body.model_dump(),
    )


@router.get(
    "/{user_id}/events",
    response_model=list[EngagementEventRead],
    dependencies=[Depends(require_user_owner)],
)
def list_events(
    user_id: uuid.UUID,
    service: UserServiceDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return service.list_events(
        user_id,
        limit,
        offset,
    )


@router.put(
    "/{user_id}/reactions/{story_id}",
    response_model=StoryReactionRead,
    dependencies=[Depends(require_user_owner)],
)
def set_reaction(
    user_id: uuid.UUID,
    story_id: uuid.UUID,
    body: ReactionUpdate,
    service: UserServiceDep,
):
    return service.set_reaction(
        user_id,
        story_id,
        body.reaction,
    )


@router.delete(
    "/{user_id}/reactions/{story_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_user_owner)],
)
def remove_reaction(
    user_id: uuid.UUID,
    story_id: uuid.UUID,
    service: UserServiceDep,
):
    service.remove_reaction(
        user_id,
        story_id,
    )
