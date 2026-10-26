"""decay(): linear from 1.0 to 0.0 over 30 days (design doc D4)."""

import pytest

from Backend.Logic.Algorithm.decay import decay
from Backend.tests.algorithm.builders import NOW, days_ago


@pytest.mark.parametrize(
    "age_days, expected",
    [
        (0, 1.0),
        (3, 0.9),
        (6, 0.8),
        (15, 0.5),
        (30, 0.0),
        (45, 0.0),
    ],
)
def test_loses_weight_linearly_until_30_days(age_days, expected):
    assert decay(days_ago(age_days), NOW) == pytest.approx(expected)


def test_future_timestamp_counts_as_now():
    """A wrong phone clock must not make an event count extra."""
    assert decay(days_ago(-2), NOW) == 1.0


def test_naive_datetime_is_treated_as_utc():
    """SQLite returns datetimes without a timezone; that must not crash."""
    assert decay(days_ago(15).replace(tzinfo=None), NOW) == pytest.approx(0.5)
