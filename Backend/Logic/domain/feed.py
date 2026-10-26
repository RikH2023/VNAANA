import enum
from dataclasses import dataclass, field

from Backend.Logic.domain.story import Story


class FeedStatus(str, enum.Enum):
    available = "available"          # personalised stories below
    not_logged_in = "not_logged_in"  # anonymous: no user record, no algorithm
    no_consent = "no_consent"        # logged in, analytics consent is off (D3)
    locked = "locked"                # consent on, not enough signal yet (D10)


@dataclass(frozen=True)
class RankedStory:
    story: Story
    score: float  # kept so we can later explain to a user why they see a story


@dataclass(frozen=True)
class Feed:
    """The "For you" answer. Stories are only filled when status is available;
    otherwise the frontend shows the general feed and can explain why."""

    status: FeedStatus
    stories: list[RankedStory] = field(default_factory=list)
