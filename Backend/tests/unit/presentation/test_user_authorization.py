"""Authorization regression tests. No database or live Supabase calls."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from Backend.main import app
from Backend.Logic.exceptions import NotFoundError
from Backend.Logic.user_service import UserService
from Backend.Presentation.auth import get_authenticated_subject
from Backend.Presentation.dependencies import get_user_service, get_algorithm_service


@pytest.fixture
def context():
    subject, user_id, story_id = uuid4(), uuid4(), uuid4()
    profile = SimpleNamespace(
        id=user_id, auth_provider="supabase", auth_subject=str(subject),
        age_band=None, language=None, region=None, preferences=None,
        analytics_consent=False, consent_updated_at=None, affinity_updated_at=None,
    )
    service = Mock()
    service.get_user.return_value = profile
    service.get_authenticated_user.return_value = profile
    service.get_or_create_authenticated_user.return_value = profile
    service.update_user.return_value = profile
    service.set_consent.return_value = profile
    service.get_tags.return_value = []
    service.set_tags.return_value = []
    service.list_events.return_value = []
    now = datetime.now(timezone.utc)
    service.set_reaction.return_value = dict(story_id=story_id, reaction="like", updated_at=now)
    session_id = uuid4()
    service.log_event.return_value = dict(
        id=uuid4(), user_id=user_id, session_id=session_id, story_id=None,
        article_id=None, event_type="view", occurred_at=now, ingested_at=now,
        active_duration_ms=None, metadata=None,
    )
    algorithm = Mock()
    algorithm.get_feed.return_value = dict(status="available", stories=[])
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_user_service] = lambda: service
    app.dependency_overrides[get_algorithm_service] = lambda: algorithm
    cases = [
        ("GET", f"/users/{user_id}", None, 200),
        ("PATCH", f"/users/{user_id}", {"language": "en"}, 200),
        ("DELETE", f"/users/{user_id}", None, 204),
        ("PUT", f"/users/{user_id}/consent", {"analytics_consent": True}, 200),
        ("GET", f"/users/{user_id}/tags", None, 200),
        ("PUT", f"/users/{user_id}/tags", {"tag_ids": []}, 200),
        ("POST", f"/users/{user_id}/events", {"session_id": str(session_id), "event_type": "view"}, 201),
        ("GET", f"/users/{user_id}/events", None, 200),
        ("PUT", f"/users/{user_id}/reactions/{story_id}", {"reaction": "like"}, 200),
        ("DELETE", f"/users/{user_id}/reactions/{story_id}", None, 204),
    ]
    try:
        with TestClient(app) as client:
            yield SimpleNamespace(client=client, service=service, algorithm=algorithm,
                                  profile=profile, subject=subject, cases=cases)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.parametrize("case_index", range(10))
@pytest.mark.parametrize("identity", ["missing", "owner", "other", "wrong_provider"])
def test_all_user_routes_enforce_ownership(context, case_index, identity):
    c = context
    if identity != "missing":
        subject = uuid4() if identity == "other" else c.subject
        app.dependency_overrides[get_authenticated_subject] = lambda: subject
    if identity == "wrong_provider":
        c.profile.auth_provider = "google"
    method, path, body, success = c.cases[case_index]
    response = c.client.request(method, path, json=body)
    expected = success if identity == "owner" else (401 if identity == "missing" else 403)
    assert response.status_code == expected, response.text
    if identity == "missing":
        assert not c.service.mock_calls
    elif identity != "owner":
        # Only the ownership lookup ran; no read/mutation endpoint executed.
        assert len(c.service.mock_calls) == 1
        c.service.get_user.assert_called_once_with(c.profile.id)


def test_bootstrap_requires_auth_and_uses_verified_subject(context):
    c = context
    assert c.client.post("/users/me/bootstrap").status_code == 401
    assert not c.service.mock_calls
    app.dependency_overrides[get_authenticated_subject] = lambda: c.subject
    for _ in range(2):
        response = c.client.post("/users/me/bootstrap", json={"auth_subject": str(uuid4())})
        assert response.status_code == 200
        assert response.json()["id"] == str(c.profile.id)
    assert c.service.get_or_create_authenticated_user.call_count == 2
    c.service.get_or_create_authenticated_user.assert_called_with(c.subject)


def test_personal_feed_ignores_supplied_user_id(context):
    c = context
    assert c.client.get("/stories/for-you").status_code == 401
    c.algorithm.get_feed.assert_not_called()
    app.dependency_overrides[get_authenticated_subject] = lambda: c.subject
    response = c.client.get(f"/stories/for-you?user_id={uuid4()}")
    assert response.status_code == 200
    c.service.get_authenticated_user.assert_called_once_with(c.subject)
    c.algorithm.get_feed.assert_called_once_with(c.profile.id, limit=20, offset=0)


def test_missing_profile_returns_404(context):
    app.dependency_overrides[get_authenticated_subject] = lambda: context.subject
    context.service.get_user.side_effect = NotFoundError("User", context.profile.id)
    assert context.client.get(f"/users/{context.profile.id}").status_code == 404


@pytest.mark.parametrize("upstream, expected", [(401, 401), (403, 401), (500, 503), (429, 503), (200, 200)])
def test_real_auth_helper_with_mocked_supabase(context, upstream, expected):
    c = context
    response = httpx.Response(upstream, json={"id": str(c.subject)})
    with patch("Backend.Presentation.auth.httpx.AsyncClient") as factory:
        client = factory.return_value.__aenter__.return_value
        client.get = AsyncMock(return_value=response)
        result = c.client.get(f"/users/{c.profile.id}", headers={"Authorization": "Bearer test-token"})
    assert result.status_code == expected
    assert client.get.call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
    if expected != 200:
        assert not c.service.mock_calls


def test_auth_network_failure_and_bad_response(context):
    with patch("Backend.Presentation.auth.httpx.AsyncClient") as factory:
        client = factory.return_value.__aenter__.return_value
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        headers = {"Authorization": "Bearer test-token"}
        assert context.client.get("/auth/me", headers=headers).status_code == 503
        client.get = AsyncMock(return_value=httpx.Response(200, json={"id": "invalid"}))
        assert context.client.get("/auth/me", headers=headers).status_code == 502


@pytest.mark.parametrize("method", ["POST", "PATCH", "PUT", "DELETE"])
def test_cors_allows_protected_browser_operations(context, method):
    response = context.client.options("/users/me/bootstrap", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_public_user_creation_remains_removed(context):
    assert context.client.post("/users", json={}).status_code in (404, 405)
    assert not context.service.mock_calls


def test_identity_lookup_is_read_only(context):
    repository = Mock()
    service = UserService(users=repository, tags=None, events=None,
                          stories=None, articles=None, algorithm=None)
    repository.get_by_identity.return_value = context.profile
    assert service.get_authenticated_user(context.subject) is context.profile
    repository.get_by_identity.assert_called_once_with("supabase", str(context.subject))
    assert len(repository.mock_calls) == 1
    repository.get_by_identity.return_value = None
    with pytest.raises(NotFoundError):
        service.get_authenticated_user(context.subject)
    repository.get_or_create_by_identity.assert_not_called()


def test_cors_rejects_other_origin(context):
    response = context.client.options("/users/me/bootstrap", headers={
        "Origin": "https://untrusted.example",
        "Access-Control-Request-Method": "POST",
    })
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
