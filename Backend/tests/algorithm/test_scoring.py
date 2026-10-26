"""score_user(): actions → a score per tag (design doc D1, D2, D6, D8)."""

import pytest

from Backend.Logic.Algorithm.scoring import score_user
from Backend.Logic.domain.story_reaction import Reaction
from Backend.tests.algorithm.builders import (
    NOW,
    declared,
    make_event,
    make_reaction,
    new_id,
)

USER = new_id()
HIKING, SPORT, EDUCATION, FOOTBALL = new_id(), new_id(), new_id(), new_id()


def score(events=(), reactions=(), declared_tags=(), story_tags=None):
    return score_user(list(events), list(reactions), list(declared_tags), story_tags or {}, NOW)


@pytest.mark.parametrize("event_type, weight", [("share", 5), ("read_complete", 1)])
def test_event_weights(event_type, weight):
    story = new_id()
    result = score(events=[make_event(USER, story, event_type)], story_tags={story: [HIKING]})
    assert result == {HIKING: weight}


@pytest.mark.parametrize("reaction, weight", [(Reaction.like, 2), (Reaction.dislike, -5)])
def test_reaction_weights(reaction, weight):
    story = new_id()
    result = score(reactions=[make_reaction(USER, story, reaction)], story_tags={story: [HIKING]})
    assert result == {HIKING: weight}


def test_declared_tag_starts_at_5_and_fades():
    result = score(declared_tags=[declared(HIKING, declared_days_ago=15)])
    assert result == {HIKING: pytest.approx(2.5)}


def test_unknown_event_type_counts_for_nothing():
    story = new_id()
    result = score(events=[make_event(USER, story, "story_open")], story_tags={story: [HIKING]})
    assert result == {}


def test_story_without_tags_counts_for_nothing():
    result = score(events=[make_event(USER, new_id(), "share")])
    assert result == {}


def test_every_tag_on_a_story_gets_the_full_weight():
    """D6: a like on a hiking + sport story gives +2 to both, not +1 each."""
    story = new_id()
    result = score(
        reactions=[make_reaction(USER, story, Reaction.like)],
        story_tags={story: [HIKING, SPORT]},
    )
    assert result == {HIKING: 2, SPORT: 2}


def test_one_dislike_cancels_a_declared_tag_of_the_same_age():
    """D8: +5 was chosen so a dislike exactly cancels a fresh pick."""
    story = new_id()
    result = score(
        reactions=[make_reaction(USER, story, Reaction.dislike)],
        declared_tags=[declared(SPORT)],
        story_tags={story: [SPORT]},
    )
    assert result == {SPORT: 0}


def test_worked_example_from_the_design_doc():
    a, b, c, d, e, f, g = (new_id() for _ in range(7))
    story_tags = {
        a: [HIKING], b: [HIKING, EDUCATION], c: [HIKING, SPORT], d: [HIKING],
        e: [HIKING], f: [EDUCATION], g: [SPORT, FOOTBALL],
    }

    result = score(
        events=[
            make_event(USER, a, "share", happened_days_ago=3),
            make_event(USER, b, "share", happened_days_ago=6),
            make_event(USER, e, "read_complete"),
            make_event(USER, f, "read_complete", happened_days_ago=6),
        ],
        reactions=[
            make_reaction(USER, c, Reaction.like, happened_days_ago=3),
            make_reaction(USER, d, Reaction.like),
            make_reaction(USER, g, Reaction.dislike),
        ],
        declared_tags=[declared(t, declared_days_ago=15) for t in (HIKING, SPORT, EDUCATION)],
        story_tags=story_tags,
    )

    assert result == {
        HIKING: pytest.approx(15.8),
        EDUCATION: pytest.approx(7.3),
        SPORT: pytest.approx(-0.7),
        FOOTBALL: pytest.approx(-5.0),
    }
