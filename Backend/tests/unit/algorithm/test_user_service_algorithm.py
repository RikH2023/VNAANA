"""The parts of UserService that belong to the algorithm: reactions (D2)
and deleting algorithm data when consent is withdrawn (D3)."""

import pytest

from Backend.Logic.domain.story_reaction import Reaction
from Backend.Logic.exceptions import ConsentRequiredError, NotFoundError
from Backend.tests.unit.algorithm.builders import make_story, make_user, new_id


def add_user(repo, users, *, consent=True):
    user = users.add(make_user(consent=consent))
    repo.add_user(user)
    return user


# ---- reactions ----------------------------------------------------------------------

def test_latest_reaction_wins(repo, users, user_service):
    user = add_user(repo, users)
    story = repo.add_story(make_story(), [])

    user_service.set_reaction(user.id, story.id, Reaction.like)
    user_service.set_reaction(user.id, story.id, Reaction.dislike)

    assert len(repo.reactions) == 1
    assert repo.reactions[(user.id, story.id)].reaction == Reaction.dislike


def test_unlike_removes_the_reaction(repo, users, user_service):
    user = add_user(repo, users)
    story = repo.add_story(make_story(), [])
    user_service.set_reaction(user.id, story.id, Reaction.like)

    user_service.remove_reaction(user.id, story.id)

    assert repo.reactions == {}


def test_reacting_without_consent_is_refused(repo, users, user_service):
    user = add_user(repo, users, consent=False)
    story = repo.add_story(make_story(), [])

    with pytest.raises(ConsentRequiredError):
        user_service.set_reaction(user.id, story.id, Reaction.like)

    assert repo.reactions == {}


def test_removing_a_reaction_needs_no_consent(repo, users, user_service):
    user = add_user(repo, users, consent=False)
    user_service.remove_reaction(user.id, new_id())  # must not raise


def test_reacting_to_an_unknown_story_is_not_found(repo, users, user_service):
    user = add_user(repo, users)

    with pytest.raises(NotFoundError):
        user_service.set_reaction(user.id, new_id(), Reaction.like)


# ---- consent withdrawn -------------------------------------------------------------

def test_withdrawing_consent_deletes_algorithm_data(repo, users, user_service):
    user = add_user(repo, users)
    story = repo.add_story(make_story(), [])
    user_service.set_reaction(user.id, story.id, Reaction.like)
    repo.scores[user.id] = {new_id(): 3.0}

    user_service.set_consent(user.id, False)

    assert repo.data_deleted_for == [user.id]
    assert repo.reactions == {}
    assert user.id not in repo.scores


@pytest.mark.parametrize("start, new", [(False, False), (True, True), (False, True)])
def test_other_consent_changes_delete_nothing(repo, users, user_service, start, new):
    user = add_user(repo, users, consent=start)

    user_service.set_consent(user.id, new)

    assert repo.data_deleted_for == []
