"""AlgorithmService: the hourly job and the "For you" feed (D3, D10, D11, D12).

Runs against the in-memory fakes, so this is the whole Logic side of the
algorithm without a database.
"""

import pytest

from Backend.Logic.domain.feed import FeedStatus
from Backend.Logic.domain.story import StoryStatus
from Backend.Logic.domain.story_reaction import Reaction
from Backend.Logic.exceptions import NotFoundError
from Backend.tests.algorithm.builders import (
    NOW,
    declared,
    make_event,
    make_reaction,
    make_story,
    make_user,
    new_id,
)

HIKING, SPORT, EDUCATION, FOOTBALL, POLITICS, ECONOMY = (new_id() for _ in range(6))


def add_user(repo, users, *, consent=True):
    user = users.add(make_user(consent=consent))
    repo.add_user(user)
    return user


def worked_example_user(repo, users):
    """The user from the design doc's worked example, as stored data."""
    user = add_user(repo, users)
    past = {
        name: repo.add_story(make_story(name, updated_days_ago=40), tags)
        for name, tags in [
            ("A", [HIKING]), ("B", [HIKING, EDUCATION]), ("C", [HIKING, SPORT]), ("D", [HIKING]),
            ("E", [HIKING]), ("F", [EDUCATION]), ("G", [SPORT, FOOTBALL]),
        ]
    }
    repo.events += [
        make_event(user.id, past["A"].id, "share", happened_days_ago=3),
        make_event(user.id, past["B"].id, "share", happened_days_ago=6),
        make_event(user.id, past["E"].id, "read_complete"),
        make_event(user.id, past["F"].id, "read_complete", happened_days_ago=6),
    ]
    for story, reaction, days in [("C", Reaction.like, 3), ("D", Reaction.like, 0), ("G", Reaction.dislike, 0)]:
        repo.reactions[(user.id, past[story].id)] = make_reaction(
            user.id, past[story].id, reaction, happened_days_ago=days
        )
    repo.declared_tags[user.id] = [declared(t, declared_days_ago=15) for t in (HIKING, SPORT, EDUCATION)]
    return user


def todays_stories(repo):
    for name, tags, days in [
        ("S1", [HIKING], 0), ("S2", [HIKING, SPORT], 15), ("S3", [EDUCATION, POLITICS], 3),
        ("S4", [SPORT, FOOTBALL], 0), ("S5", [ECONOMY], 0),
    ]:
        repo.add_story(make_story(name, updated_days_ago=days), tags)


# ---- hourly job ------------------------------------------------------------------

def test_job_stores_the_worked_example_scores(repo, users, algorithm_service):
    user = worked_example_user(repo, users)

    scored = algorithm_service.run_scoring(now=NOW)

    assert scored == 1
    assert repo.scores[user.id] == {
        HIKING: pytest.approx(15.8),
        EDUCATION: pytest.approx(7.3),
        SPORT: pytest.approx(-0.7),
        FOOTBALL: pytest.approx(-5.0),
    }


def test_job_ignores_actions_older_than_30_days(repo, users, algorithm_service):
    user = add_user(repo, users)
    story = repo.add_story(make_story(updated_days_ago=40), [HIKING])
    repo.events.append(make_event(user.id, story.id, "share", happened_days_ago=31))

    algorithm_service.run_scoring(now=NOW)

    assert repo.scores[user.id] == {}


def test_job_skips_and_cleans_up_users_without_consent(repo, users, algorithm_service):
    user = add_user(repo, users, consent=False)
    repo.scores[user.id] = {HIKING: 99.0}  # left over from when consent was on

    scored = algorithm_service.run_scoring(now=NOW)

    assert scored == 0
    assert user.id not in repo.scores


# ---- feed: the four statuses ------------------------------------------------------

def test_feed_without_user_is_not_logged_in(algorithm_service):
    assert algorithm_service.get_feed(None).status == FeedStatus.not_logged_in


def test_feed_for_unknown_user_raises_not_found(algorithm_service):
    with pytest.raises(NotFoundError):
        algorithm_service.get_feed(new_id())


def test_feed_without_consent(repo, users, algorithm_service):
    user = add_user(repo, users, consent=False)
    assert algorithm_service.get_feed(user.id).status == FeedStatus.no_consent


def test_feed_is_locked_with_only_declared_tags(repo, users, algorithm_service):
    """Three fresh declared tags are worth 5 each: not enough to unlock."""
    user = add_user(repo, users)
    repo.declared_tags[user.id] = [declared(t) for t in (HIKING, SPORT, EDUCATION)]
    algorithm_service.run_scoring(now=NOW)

    feed = algorithm_service.get_feed(user.id, now=NOW)

    assert feed.status == FeedStatus.locked
    assert feed.stories == []


# ---- feed: the ranking ------------------------------------------------------------

def test_feed_matches_the_worked_example(repo, users, algorithm_service):
    user = worked_example_user(repo, users)
    todays_stories(repo)
    algorithm_service.run_scoring(now=NOW)

    feed = algorithm_service.get_feed(user.id, now=NOW)

    assert feed.status == FeedStatus.available
    assert [(r.story.title, round(r.score, 3)) for r in feed.stories] == [
        ("S1", 15.8), ("S2", 3.775), ("S3", 3.285), ("S5", 0.0), ("S4", -2.85),
    ]


def test_feed_paging(repo, users, algorithm_service):
    user = worked_example_user(repo, users)
    todays_stories(repo)
    algorithm_service.run_scoring(now=NOW)

    page = algorithm_service.get_feed(user.id, limit=2, offset=1, now=NOW)

    assert [r.story.title for r in page.stories] == ["S2", "S3"]


def test_feed_only_contains_published_stories_from_the_last_30_days(repo, users, algorithm_service):
    user = worked_example_user(repo, users)
    repo.add_story(make_story("fresh"), [HIKING])
    repo.add_story(make_story("draft", status=StoryStatus.draft), [HIKING])
    repo.add_story(make_story("too old", updated_days_ago=31), [HIKING])
    algorithm_service.run_scoring(now=NOW)

    feed = algorithm_service.get_feed(user.id, now=NOW)

    assert [r.story.title for r in feed.stories] == ["fresh"]
