"""Wires Logic services to their dependencies per request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.Logic.article_service import ArticleService
from Backend.Logic.story_service import StoryService
from Backend.Logic.user_service import UserService
from Backend.Logic.ports.article_repository import ArticleRepository
from Backend.Logic.ports.engagement_event_repository import (
    EngagementEventRepository,
)
from Backend.Logic.ports.provider_repository import ProviderRepository
from Backend.Logic.ports.story_repository import StoryRepository
from Backend.Logic.ports.tag_repository import TagRepository
from Backend.Logic.ports.user_repository import UserRepository


DbSession = Annotated[Session, Depends(get_db)]


def get_article_repository(db: DbSession) -> ArticleRepository:
    raise RuntimeError(
        "ArticleRepository dependency has not been configured"
    )


def get_story_repository(db: DbSession) -> StoryRepository:
    raise RuntimeError(
        "StoryRepository dependency has not been configured"
    )


def get_tag_repository(db: DbSession) -> TagRepository:
    raise RuntimeError(
        "TagRepository dependency has not been configured"
    )


def get_user_repository(db: DbSession) -> UserRepository:
    raise RuntimeError(
        "UserRepository dependency has not been configured"
    )


def get_engagement_event_repository(
    db: DbSession,
) -> EngagementEventRepository:
    raise RuntimeError(
        "EngagementEventRepository dependency has not been configured"
    )


def get_provider_repository(db: DbSession) -> ProviderRepository:
    raise RuntimeError(
        "ProviderRepository dependency has not been configured"
    )


ArticleRepositoryDep = Annotated[
    ArticleRepository,
    Depends(get_article_repository),
]

StoryRepositoryDep = Annotated[
    StoryRepository,
    Depends(get_story_repository),
]

TagRepositoryDep = Annotated[
    TagRepository,
    Depends(get_tag_repository),
]

UserRepositoryDep = Annotated[
    UserRepository,
    Depends(get_user_repository),
]

EngagementEventRepositoryDep = Annotated[
    EngagementEventRepository,
    Depends(get_engagement_event_repository),
]

ProviderRepositoryDep = Annotated[
    ProviderRepository,
    Depends(get_provider_repository),
]


def get_article_service() -> ArticleService:
    return ArticleService()


def get_story_service() -> StoryService:
    return StoryService()


def get_user_service() -> UserService:
    return UserService()


ArticleServiceDep = Annotated[
    ArticleService,
    Depends(get_article_service),
]

StoryServiceDep = Annotated[
    StoryService,
    Depends(get_story_service),
]

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]