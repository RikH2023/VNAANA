"""FastAPI dependency wiring.

Presentation owns the request-scoped database session and constructs the
application services with their repository dependencies.

Routers only depend on services.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from Backend.database import get_db

from Backend.Dal.repositories.article_repository import (
    ArticleRepository as DalArticleRepository,
)
from Backend.Dal.repositories.engagement_event_repository import (
    EngagementEventRepository as DalEngagementEventRepository,
)
from Backend.Dal.repositories.provider_repository import (
    ProviderRepository as DalProviderRepository,
)
from Backend.Dal.repositories.story_repository import (
    StoryRepository as DalStoryRepository,
)
from Backend.Dal.repositories.tag_repository import (
    TagRepository as DalTagRepository,
)
from Backend.Dal.repositories.user_repository import (
    UserRepository as DalUserRepository,
)

from Backend.Logic.article_service import ArticleService
from Backend.Logic.story_service import StoryService
from Backend.Logic.user_service import UserService


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DbSession = Annotated[
    Session,
    Depends(get_db),
]


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------

def get_article_service(
    db: DbSession,
) -> ArticleService:
    return ArticleService(
        articles=DalArticleRepository(db),
        providers=DalProviderRepository(db),
    )


ArticleServiceDep = Annotated[
    ArticleService,
    Depends(get_article_service),
]


# ---------------------------------------------------------------------------
# Story
# ---------------------------------------------------------------------------

def get_story_service(
    db: DbSession,
) -> StoryService:
    return StoryService(
        stories=DalStoryRepository(db),
        articles=DalArticleRepository(db),
        tags=DalTagRepository(db),
    )


StoryServiceDep = Annotated[
    StoryService,
    Depends(get_story_service),
]


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_user_service(
    db: DbSession,
) -> UserService:
    return UserService(
        users=DalUserRepository(db),
        tags=DalTagRepository(db),
        events=DalEngagementEventRepository(db),
        stories=DalStoryRepository(db),
        articles=DalArticleRepository(db),
    )


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]