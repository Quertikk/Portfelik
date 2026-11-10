from datetime import date

import pytest

from budget import average, due_soon, limit_state, saver_mode, settle


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


# F13: dzień płatności 31 w krótszym miesiącu, przełom miesiąca i roku
def due(day, today):
    return [d for _, d in due_soon([{"day_of_month": day}], today)]


def test_due_soon_window():
    assert due(10, date(2026, 11, 8)) == [date(2026, 11, 10)]  # za 2 dni
    assert due(10, date(2026, 11, 10)) == [date(2026, 11, 10)]  # dziś
    assert due(10, date(2026, 11, 7)) == []  # za 3 dni
    assert due(10, date(2026, 11, 11)) == []  # już po terminie, następny za miesiąc


def test_due_soon_31st_in_short_month():
    assert due(31, date(2027, 2, 27)) == [date(2027, 2, 28)]
    assert due(31, date(2028, 2, 27)) == [date(2028, 2, 29)]  # rok przestępny: luty ma 29 dni
    assert due(31, date(2028, 2, 26)) == []
    assert due(30, date(2026, 11, 28)) == [date(2026, 11, 30)]


def test_due_soon_across_year_end():
    assert due(1, date(2026, 12, 30)) == [date(2027, 1, 1)]
    assert due(1, date(2026, 12, 29)) == []
    assert due(31, date(2026, 12, 31)) == [date(2026, 12, 31)]


def test_due_soon_sorted_by_date():
    subs = [{"day_of_month": 12, "n": "b"}, {"day_of_month": 11, "n": "a"}]
    assert [s["n"] for s, _ in due_soon(subs, date(2026, 11, 10))] == ["a", "b"]


# F12
def test_average():
    assert average(90000, 3) == 30000
    assert average(100, 3) == 33
    assert average(500, 0) is None  # portfel bez historii


# F17: salda sumują się do zera, a przelewy je wyrównują
def apply(balance, transfers):
    balance = dict(balance)
    for src, dst, amount in transfers:
        balance[src] += amount
        balance[dst] -= amount
    return balance


def test_settle_two_people():
    balance, transfers = settle({"Ala": 3000, "Bob": 1000})
    assert balance == {"Ala": 1000, "Bob": -1000}
    assert transfers == [("Bob", "Ala", 1000)]


def test_settle_three_people_one_paid_all():
    balance, transfers = settle({"Ala": 9000, "Bob": 0, "Cel": 0})
    assert balance == {"Ala": 6000, "Bob": -3000, "Cel": -3000}
    assert transfers == [("Bob", "Ala", 3000), ("Cel", "Ala", 3000)]


def test_settle_everyone_paid_equally():
    assert settle({"Ala": 500, "Bob": 500, "Cel": 500}) == ({"Ala": 0, "Bob": 0, "Cel": 0}, [])


def test_settle_nobody_paid_and_empty():
    assert settle({"Ala": 0, "Bob": 0}) == ({"Ala": 0, "Bob": 0}, [])
    assert settle({}) == ({}, [])


@pytest.mark.parametrize("paid", [
    {"Ala": 100, "Bob": 0, "Cel": 0},  # reszta 1 grosz
    {"Ala": 1001, "Bob": 502, "Cel": 7, "Dan": 0},
    {"Ala": 5, "Bob": 5, "Cel": 6},
])
def test_settle_balances_sum_to_zero_and_transfers_clear_them(paid):
    balance, transfers = settle(paid)
    assert sum(balance.values()) == 0
    assert set(apply(balance, transfers).values()) == {0}
    assert all(amount > 0 for _, _, amount in transfers)
