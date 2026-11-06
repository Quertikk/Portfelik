from datetime import date

import pytest

from app import format_zl, parse_amount, parse_month, shift_month


@pytest.mark.parametrize("text, expected", [
    ("12,50", 1250), ("12.5", 1250), ("12", 1200), (" 1 234,56 ", 123456),
    ("0,01", 1), ("1000000", 100_000_000),
])
def test_parse_amount_valid(text, expected):
    assert parse_amount(text) == expected


@pytest.mark.parametrize("text", [
    "0", "0,00", "0,004",             # zero i kwota zaokrąglona do zera
    "-5", "-0,01",                    # liczba ujemna
    "1000000,01",                     # powyżej limitu 1 000 000 zł
    "inf", "-inf", "1e999",           # OverflowError
    "nan",                            # ValueError
    "abc", "", "12 zł", "1,2,3",      # tekst
    None,                             # brak pola w formularzu
])
def test_parse_amount_invalid(text):
    assert parse_amount(text) is None


def test_parse_month_valid():
    assert parse_month("2026-03") == date(2026, 3, 1)


@pytest.mark.parametrize("text", [None, "", "abc", "2026", "2026-13", "2026-00", "2026-1-1"])
def test_parse_month_invalid_falls_back_to_current(text):
    assert parse_month(text) == date.today().replace(day=1)


@pytest.mark.parametrize("start, delta, expected", [
    (date(2026, 11, 1), 1, date(2026, 12, 1)),
    (date(2026, 12, 1), 1, date(2027, 1, 1)),
    (date(2026, 1, 1), -1, date(2025, 12, 1)),
    (date(2026, 3, 1), -3, date(2025, 12, 1)),
    (date(2026, 5, 1), 0, date(2026, 5, 1)),
    (date(2026, 1, 1), 25, date(2028, 2, 1)),
])
def test_shift_month(start, delta, expected):
    assert shift_month(start, delta) == expected


@pytest.mark.parametrize("grosze, expected", [
    (0, "0,00 zł"), (5, "0,05 zł"), (1250, "12,50 zł"),
    (123456, "1 234,56 zł"), (100_000_000, "1 000 000,00 zł"),
])
def test_format_zl(grosze, expected):
    assert format_zl(grosze) == expected
