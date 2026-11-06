from datetime import date

import pytest

from budget import limit_state, saver_mode


@pytest.mark.parametrize("spent, limit, expected", [
    (0, 10000, "ok"),
    (7999, 10000, "ok"),
    (8000, 10000, "warn"),   # granica 80%
    (10000, 10000, "warn"),  # limit osiągnięty, nie przekroczony
    (10001, 10000, "over"),
    (1, 1, "warn"),
])
def test_limit_state(spent, limit, expected):
    assert limit_state(spent, limit) == expected


@pytest.mark.parametrize("spent, limits, today, expected", [
    (8001, 10000, date(2026, 11, 15), True),
    (8000, 10000, date(2026, 11, 15), False),   # dokładnie 80% to jeszcze nie „ponad”
    (5000, 0, date(2026, 11, 15), False),       # brak limitów
    (0, 0, date(2026, 11, 1), False),
    (9000, 10000, date(2026, 11, 29), True),
    (9000, 10000, date(2026, 11, 30), False),   # ostatni dzień miesiąca
    (9000, 10000, date(2027, 2, 27), True),
    (9000, 10000, date(2027, 2, 28), False),    # luty w roku nieprzestępnym
    (9000, 10000, date(2028, 2, 28), True),     # luty w roku przestępnym
])
def test_saver_mode(spent, limits, today, expected):
    assert saver_mode(spent, limits, today) is expected
