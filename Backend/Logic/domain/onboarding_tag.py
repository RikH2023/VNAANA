import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OnboardingTag:
    """A tag the user picked during onboarding (design doc D8).

    Only these get the starting bonus. Tags added later are regular
    user_tags without the onboarding flag and never become an OnboardingTag.
    """

    tag_id: uuid.UUID
    picked_at: datetime
