"""F10: limity kategorii w widoku portfela."""
from datetime import date

from conftest import WALLET, login, query

MINE = WALLET["Filip"]
FOOD = 1  # Jedzenie, pierwsza kategoria w db.CATEGORIES


def set_limits(client, wallet=MINE, **limits):
    return client.post(f"/portfel/{wallet}/limity", data={f"limit_{k[1:]}": v for k, v in limits.items()})


def test_owner_sets_and_clears_limit(client):
    set_limits(client, c1="300", c2="50,50")
    assert {r["category_id"]: r["amount"] for r in query(
        "SELECT * FROM category_limits WHERE wallet_id = ?", MINE)} == {1: 30000, 2: 5050}
    set_limits(client, c1="300")  # puste pole kategorii 2 usuwa jej limit
    assert [r["category_id"] for r in query("SELECT * FROM category_limits WHERE wallet_id = ?", MINE)] == [1]


def test_invalid_limit_keeps_previous_value(client):
    set_limits(client, c1="300")
    resp = set_limits(client, c1="abc")
    assert query("SELECT amount FROM category_limits WHERE wallet_id = ?", MINE)[0][0] == 30000
    assert resp.status_code == 302


def test_non_owner_cannot_set_limits(client):
    assert set_limits(client, wallet=WALLET["shared"], c1="100").status_code == 403


def test_warning_at_80_percent(client):
    set_limits(client, c1="100")
    client.post(f"/portfel/{MINE}/dodaj", data={"amount": "85", "category_id": FOOD})
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "85% limitu" in html and 'class="bar warn"' in html


def test_over_limit_message(client):
    set_limits(client, c1="10")
    client.post(f"/portfel/{MINE}/dodaj", data={"amount": "12,50", "category_id": FOOD})
    assert "Limit przekroczony o 2,50 zł" in client.get(f"/portfel/{MINE}").get_data(as_text=True)


def test_limit_without_spending_is_listed(client):
    set_limits(client, c5="40")  # Rozrywka: Filip nie ma tu wydatków
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "Rozrywka" in html and "/ 40,00 zł" in html


def test_saver_banner(client, monkeypatch):
    monkeypatch.setattr("app.saver_mode", lambda *a: True)
    assert "Tryb Oszczędny" in client.get(f"/portfel/{MINE}").get_data(as_text=True)


def test_no_saver_banner_without_limits(client):
    assert "Tryb Oszczędny" not in client.get(f"/portfel/{MINE}").get_data(as_text=True)


def test_saver_banner_only_for_current_month(client, monkeypatch):
    monkeypatch.setattr("app.saver_mode", lambda *a: True)
    past = date(2020, 1, 1).strftime("%Y-%m")
    assert "Tryb Oszczędny" not in client.get(f"/portfel/{MINE}?m={past}").get_data(as_text=True)


def test_pending_expense_does_not_count_toward_limit(app):
    owner = login(app.test_client(), "Valentyn")
    set_limits(owner, wallet=WALLET["shared"], c6="400")  # Zakupy; pralka 349 zł czeka na decyzję (87%, gdyby się liczyła)
    html = owner.get(f"/portfel/{WALLET['shared']}").get_data(as_text=True)
    assert "/ 400,00 zł" in html and 'class="bar warn"' not in html
