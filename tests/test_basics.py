"""F1-F4: dodawanie wydatku, lista portfeli, podsumowanie miesiąca i „kto ile zapłacił”."""
from datetime import date

from app import shift_month
from conftest import WALLET, login, query

PERSONAL = WALLET["Filip"]
SHARED = WALLET["shared"]
THIS_MONTH = date.today().replace(day=1)


def page(client, wallet, month=None):
    return client.get(f"/portfel/{wallet}", query_string={"m": month} if month else None).get_data(as_text=True)


def test_add_expense_saves_all_fields(client):
    client.post(f"/portfel/{PERSONAL}/dodaj", data={
        "amount": "12,50", "category_id": 3, "spent_on": "2026-01-15", "description": "bilet"})
    e = query("SELECT * FROM expenses ORDER BY id DESC LIMIT 1")[0]
    assert (e["amount"], e["category_id"], e["spent_on"], e["description"], e["user_id"], e["wallet_id"]) == (
        1250, 3, "2026-01-15", "bilet", 3, PERSONAL)


def test_add_expense_defaults_date_to_today_and_description_to_empty(client):
    client.post(f"/portfel/{PERSONAL}/dodaj", data={"amount": "5", "category_id": 1})
    e = query("SELECT * FROM expenses ORDER BY id DESC LIMIT 1")[0]
    assert e["spent_on"] == date.today().isoformat() and e["description"] == ""


def test_wallet_list_has_personal_first_then_shared(client):
    html = page(client, PERSONAL)
    assert 0 < html.index("Portfel: Filip") < html.index("Wspólne mieszkanie")


def test_month_summary_and_comparison_with_previous_month(client):
    # demo: wspólny portfel, bieżący miesiąc 186,40 + 60,00 + 240,00 zatwierdzone; poprzedni 74,15 + 129,99 + 300,00
    html = page(client, SHARED)
    assert "486,40 zł" in html and "504,14 zł" in html and "-4%" in html


def test_pending_does_not_inflate_month_total(client):
    assert "835,40" not in page(client, SHARED)  # 486,40 + oczekująca pralka 349,00


def test_other_month_is_selectable(client):
    prev = shift_month(THIS_MONTH, -1).strftime("%Y-%m")
    assert "504,14 zł" in page(client, SHARED, prev)


def test_who_paid_lists_every_member_with_their_total(client):
    html = page(client, SHARED)
    for name in ("Valentyn", "Daria", "Filip"):
        assert name in html.split("Kto ile zapłacił")[1].split("Rozliczenie")[0]
    assert "240,00 zł" in html  # Daria
