"""Ranking and the unlock rule (design doc D7, D9, D10)."""

import pytest

from Backend.Logic.Algorithm.ranking import (
    final_score,
    is_unlocked,
    rank_stories,
    story_score,
)
from Backend.tests.algorithm.builders import NOW, days_ago, make_story, new_id

HIKING, SPORT, POLITICS = new_id(), new_id(), new_id()


# ---- D7: story score is the average of its tags -----------------------------

def test_story_score_is_the_average_of_its_tags():
    assert story_score([HIKING, SPORT], {HIKING: 10, SPORT: -2}) == 4


def test_tag_without_a_score_counts_as_zero():
    assert story_score([HIKING, POLITICS], {HIKING: 10}) == 5


def test_story_without_tags_scores_zero():
    assert story_score([], {HIKING: 10}) == 0


# ---- D9: freshness only lowers positive scores --------------------------------

def test_freshness_lowers_a_positive_score():
    assert final_score(4.0, days_ago(15), NOW) == pytest.approx(2.0)


def test_freshness_leaves_a_negative_score_alone():
    """Otherwise disliked stories would drift up towards neutral as they age."""
    assert final_score(-5.0, days_ago(25), NOW) == -5.0


def test_equal_scores_go_to_the_newest_story():
    older, newer = make_story("older", updated_days_ago=5), make_story("newer", updated_days_ago=1)
    ranked = rank_stories([older, newer], {}, {}, NOW)
    assert [r.story.title for r in ranked] == ["newer", "older"]


def test_strong_older_interest_beats_weak_fresh_interest():
    old = make_story("old", updated_days_ago=20)
    fresh = make_story("fresh")
    ranked = rank_stories([fresh, old], {old.id: [HIKING], fresh.id: [SPORT]}, {HIKING: 4, SPORT: 0.5}, NOW)
    assert [r.story.title for r in ranked] == ["old", "fresh"]


# ---- D10: when "For you" unlocks ----------------------------------------------

@pytest.mark.parametrize(
    "scores, unlocked",
    [
        ([], False),                 # brand-new user
        ([15], True),                # one tag at 15
        ([14.9, 10], False),         # two at 10, none at 15
        ([14.9, 10, 9.99], False),   # third just below 10
        ([10, 10, 10], True),        # exactly three at 10
        ([5, 5, 5], False),          # three fresh declared tags alone
    ],
)
def test_unlock_rule(scores, unlocked):
    assert is_unlocked({new_id(): s for s in scores}) is unlocked
