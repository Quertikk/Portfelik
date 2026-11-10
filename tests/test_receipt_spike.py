import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from receipt_spike import CATEGORIES, SCHEMA, check  # noqa: E402
from receipts import receipt_amount as grosze  # noqa: E402


def test_grosze_formats():
    assert grosze("12,50") == 1250
    assert grosze("12.5 zł") == 1250
    assert grosze("1 234,00 PLN") == 123400
    assert grosze("") is None and grosze("brak") is None


def test_check_compares_amount_date_shop():
    truth = {"kwota": "12,50", "data": "2026-11-06", "sklep": "Biedronka"}
    good = {"amount": "12.50", "date": "2026-11-06", "shop": "BIEDRONKA sp. z o.o."}
    assert all(check(good, truth).values())
    bad = {"amount": "12,05", "date": "2026-11-07", "shop": "Lidl"}
    assert not any(check(bad, truth).values())


def test_schema_categories_match_db():
    assert SCHEMA["properties"]["category"]["enum"] == CATEGORIES
