"""Wires a database session into each service, per request."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from Backend.dal.database import get_db
from Backend.logic.article_service import ArticleService
from Backend.logic.story_service import StoryService
from Backend.logic.user_service import UserService

DbSession = Annotated[Session, Depends(get_db)]


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


def get_story_service(db: DbSession) -> StoryService:
    return StoryService(db)


def get_article_service(db: DbSession) -> ArticleService:
    return ArticleService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
StoryServiceDep = Annotated[StoryService, Depends(get_story_service)]
ArticleServiceDep = Annotated[ArticleService, Depends(get_article_service)]
