import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DeclaredTag:
    """A tag the user currently says they are interested in (user_tags.is_declared).

    Each one gets the starting bonus, fading from declared_at (design doc D8,
    revised: any declared tag counts, not only onboarding picks).
    """

    tag_id: uuid.UUID
    declared_at: datetime
