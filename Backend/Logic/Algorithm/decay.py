"""Linear decay: how much a signal still counts, based on its age.

Used three times in the algorithm (design doc D4, D8, D9):
- an action (like, share, ...) fades from the moment it happened
- the onboarding bonus fades from the moment of onboarding
- a story's freshness fades from its last_updated_at
"""

from datetime import datetime, timezone

LIFETIME_DAYS = 30
SECONDS_PER_DAY = 86_400


def as_utc(moment: datetime) -> datetime:
    """Treat a datetime without a timezone as UTC.

    Postgres (timestamptz) returns timezone-aware datetimes, SQLite (used in
    tests) returns naive ones, and Python refuses to subtract one from the other.
    """
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment


def decay(happened_at: datetime, now: datetime, lifetime_days: float = LIFETIME_DAYS) -> float:
    """1.0 right now, 0.0 once lifetime_days have passed, a straight line in between."""
    age_days = (as_utc(now) - as_utc(happened_at)).total_seconds() / SECONDS_PER_DAY

    # occurred_at can be sent by the client, so a wrong phone clock can put an
    # event in the future. Treat that as "just now" instead of counting extra.
    age_days = max(age_days, 0)

    return max(0.0, 1 - age_days / lifetime_days)
