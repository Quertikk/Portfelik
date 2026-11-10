"""F12 średnia z 3 miesięcy, F13 subskrypcje, F17 rozliczenie, F18 eksport CSV."""
import csv
import io
from datetime import date, timedelta

import pytest

import db
from app import shift_month
from conftest import WALLET, login, query

MINE = WALLET["Filip"]
SHARED = WALLET["shared"]
THIS = date.today().replace(day=1)


def add_expense(wallet, user, month_offset, zl, category=1, description="", status="approved"):
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, spent_on, status)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (wallet, user, category, round(zl * 100), description,
             shift_month(THIS, month_offset).isoformat(), status))


# --- F12 ---------------------------------------------------------------------------------------------

def test_average_of_three_previous_months(client):
    add_expense(MINE, 3, -1, 300)
    add_expense(MINE, 3, -3, 900)  # miesiąc -2 bez wydatków liczy się jako 0
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "średnia z 3 miesięcy: 400,00 zł" in html and 'class="avg"' in html


def test_average_with_shorter_history_uses_only_months_since_first_expense(client):
    add_expense(MINE, 3, -1, 300)  # portfel ma 1 miesiąc historii, nie 3
    assert "średnia z 3 miesięcy: 300,00 zł" in client.get(f"/portfel/{MINE}").get_data(as_text=True)


def test_no_average_without_history(client):
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)  # dane demo tylko z bieżącego miesiąca
    assert "średnia z 3 miesięcy" not in html and 'class="avg"' not in html


def test_average_ignores_pending_older_than_three_months_and_current_month(client):
    add_expense(MINE, 3, -1, 300)
    add_expense(MINE, 3, -4, 9000)  # za stary
    add_expense(MINE, 3, 0, 9000)  # bieżący miesiąc nie jest „poprzedni”
    add_expense(MINE, 3, -2, 5000, status="pending")  # niezatwierdzony
    assert "średnia z 3 miesięcy: 400,00 zł" not in client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "średnia z 3 miesięcy: 100,00 zł" in client.get(f"/portfel/{MINE}").get_data(as_text=True)  # 300 / 3


def test_marker_position_is_within_bar(client):
    add_expense(MINE, 3, -1, 99999)  # średnia wyższa niż wydatki z bieżącego miesiąca
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    left = float(html.split('class="avg" style="left: ', 1)[1].split("%", 1)[0])
    assert 0 <= left <= 100


# --- F13 ---------------------------------------------------------------------------------------------

def test_add_and_list_subscription(client):
    resp = client.post("/subskrypcje", data={"name": "Spotify", "amount": "23,99", "day": "15"}, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "Spotify" in html and "23,99 zł" in html and "15." in html
    assert tuple(query("SELECT name, amount, day_of_month, user_id FROM subscriptions")[0]) == ("Spotify", 2399, 15, 3)


@pytest.mark.parametrize("data", [
    {"name": "", "amount": "10", "day": "5"},
    {"name": "X", "amount": "abc", "day": "5"},
    {"name": "X", "amount": "0", "day": "5"},
    {"name": "X", "amount": "10", "day": "0"},
    {"name": "X", "amount": "10", "day": "32"},
    {"name": "X", "amount": "10", "day": "dziesiąty"},
    {"name": "X", "amount": "10"},
])
def test_invalid_subscription_is_not_saved(client, data):
    client.post("/subskrypcje", data=data)
    assert query("SELECT * FROM subscriptions") == []


def test_delete_only_own_subscription(client, app):
    client.post("/subskrypcje", data={"name": "Netflix", "amount": "50", "day": "1"})
    daria = login(app.test_client(), "Daria")
    sub_id = query("SELECT id FROM subscriptions")[0][0]
    daria.post(f"/subskrypcje/{sub_id}/usun")
    assert len(query("SELECT * FROM subscriptions")) == 1
    client.post(f"/subskrypcje/{sub_id}/usun")
    assert query("SELECT * FROM subscriptions") == []


def test_subscriptions_are_private(client, app):
    client.post("/subskrypcje", data={"name": "Netflix", "amount": "50", "day": "1"})
    daria = login(app.test_client(), "Daria")
    assert "Netflix" not in daria.get("/subskrypcje").get_data(as_text=True)


def test_banner_two_days_before_payment(client):
    day = (date.today() + timedelta(days=2)).day
    client.post("/subskrypcje", data={"name": "Spotify", "amount": "23,99", "day": str(day)})
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "Spotify" in html and "płatność pojutrze" in html


def test_banner_today_and_not_for_later_payments(client):
    client.post("/subskrypcje", data={"name": "Dziś", "amount": "10", "day": str(date.today().day)})
    day_later = (date.today() + timedelta(days=5)).day
    client.post("/subskrypcje", data={"name": "Później", "amount": "10", "day": str(day_later)})
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "płatność dziś" in html and "Później" not in html.split("<main>", 1)[1].split("Moje portfele")[0]


def test_subscriptions_require_login(anon):
    assert anon.get("/subskrypcje").status_code == 302


# --- F17 ---------------------------------------------------------------------------------------------

def test_settlement_card_on_shared_wallet(client):
    html = client.get(f"/portfel/{SHARED}").get_data(as_text=True)
    assert "Rozliczenie" in html and "→" in html
    # dane demo: Daria 240, Valentyn 186,40, Filip 60 -> średnio 162,13; Filip i Valentyn nie są rozliczeni
    assert "<strong>Filip</strong> → <strong>Daria</strong>" in html


def test_settlement_ignores_pending(client):
    before = client.get(f"/portfel/{SHARED}").get_data(as_text=True)
    add_expense(SHARED, 1, 0, 5000, status="pending")
    assert client.get(f"/portfel/{SHARED}").get_data(as_text=True).count("→") == before.count("→")


def test_no_settlement_on_personal_wallet(client):
    assert "Rozliczenie" not in client.get(f"/portfel/{MINE}").get_data(as_text=True)


def test_settlement_all_even(client):
    with db.connect() as conn:
        conn.execute("DELETE FROM expenses WHERE wallet_id = ?", (SHARED,))
    for uid in (1, 2, 3):
        add_expense(SHARED, uid, 0, 10)
    html = client.get(f"/portfel/{SHARED}").get_data(as_text=True)
    assert "Wszyscy są rozliczeni" in html and "→" not in html


# --- F18 ---------------------------------------------------------------------------------------------

def export(client, wallet=MINE, month=None):
    resp = client.get(f"/portfel/{wallet}/eksport.csv" + (f"?m={month}" if month else ""))
    return resp, list(csv.reader(io.StringIO(resp.data.decode("utf-8-sig")), delimiter=";"))


def test_export_has_bom_header_and_polish_characters(client):
    add_expense(MINE, 3, 0, 12.5, category=2, description="Żółć gęślą")
    resp, rows = export(client)
    assert resp.data.startswith(b"\xef\xbb\xbf") and resp.mimetype == "text/csv"
    assert "attachment" in resp.headers["Content-Disposition"] and ".csv" in resp.headers["Content-Disposition"]
    assert rows[0] == ["data", "kategoria", "kwota", "opis", "osoba", "status"]
    assert ["Restauracje i kawiarnie", "12,50", "Żółć gęślą", "Filip", "zatwierdzony"] in [r[1:] for r in rows]


@pytest.mark.parametrize("payload", ["=HYPERLINK(\"http://zle.pl\")", "+1+1", "-2", "@SUM(A1)", "\t=1"])
def test_formula_in_description_gets_apostrophe(client, payload):
    add_expense(MINE, 3, 0, 1, description=payload)
    _, rows = export(client)
    assert any(r[3] == "'" + payload for r in rows)
    assert not any(c.startswith(("=", "+", "-", "@")) for r in rows for c in r)


def test_empty_month_gives_header_only(client):
    _, rows = export(client, month="2000-01")
    assert len(rows) == 1


def test_export_only_chosen_month(client):
    add_expense(MINE, 3, -1, 7, description="stary")
    _, rows = export(client)
    assert not any(r[3] == "stary" for r in rows)
    _, rows = export(client, month=shift_month(THIS, -1).strftime("%Y-%m"))
    assert [r[3] for r in rows[1:]] == ["stary"]


def test_export_includes_pending_with_status(client):
    add_expense(SHARED, 3, 0, 500, description="pralka", status="pending")
    _, rows = export(client, wallet=SHARED)
    assert next(r for r in rows if r[3] == "pralka")[5] == "oczekuje"


def test_export_of_foreign_wallet_is_404(client):
    assert client.get(f"/portfel/{WALLET['Daria']}/eksport.csv").status_code == 404


def test_export_requires_login(anon):
    assert anon.get(f"/portfel/{MINE}/eksport.csv").status_code == 302
