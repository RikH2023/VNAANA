import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class Reaction(str, enum.Enum):
    like = "like"
    dislike = "dislike"


@dataclass(frozen=True)
class StoryReaction:
    """A user's current reaction to a story (design doc D2).

    One per user and story; the latest tap wins. Unliking removes the row,
    so "no reaction" is simply the absence of a StoryReaction.
    """

    user_id: uuid.UUID
    story_id: uuid.UUID
    reaction: Reaction
    updated_at: datetime
