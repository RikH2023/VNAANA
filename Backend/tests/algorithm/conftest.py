"""Shared fixtures: a fresh fake database and services for every test."""

import pytest

from Backend.Logic.algorithm_service import AlgorithmService
from Backend.Logic.user_service import UserService
from Backend.tests.algorithm.fakes import (
    FakeAlgorithmRepository,
    FakeStoryRepository,
    FakeUserRepository,
)


@pytest.fixture
def repo() -> FakeAlgorithmRepository:
    return FakeAlgorithmRepository()


@pytest.fixture
def users() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def algorithm_service(repo, users) -> AlgorithmService:
    return AlgorithmService(algorithm=repo, users=users)


@pytest.fixture
def user_service(repo, users) -> UserService:
    # tags, events and articles aren't touched by the code under test here.
    return UserService(
        users=users,
        tags=None,
        events=None,
        stories=FakeStoryRepository(repo.stories),
        articles=None,
        algorithm=repo,
    )
