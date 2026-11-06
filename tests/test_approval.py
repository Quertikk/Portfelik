"""F8: zatwierdzanie wspólnych wydatków powyżej progu."""
from datetime import date

import pytest

import db
from app import format_zl
from conftest import WALLET, login, query

SHARED = WALLET["shared"]
THIS_MONTH = date.today().strftime("%Y-%m")


def add(client, amount, wallet=SHARED, description="test"):
    client.post(f"/portfel/{wallet}/dodaj", data={"amount": amount, "category_id": 1, "description": description})
    return query("SELECT * FROM expenses ORDER BY id DESC LIMIT 1")[0]


@pytest.fixture
def daria(app):
    return login(app.test_client(), "Daria")


def test_tc_f8_01_above_threshold_is_pending(client):
    assert add(client, "200,01")["status"] == "pending"


@pytest.mark.parametrize("amount", ["200", "50"])
def test_at_or_below_threshold_is_approved(client, amount):
    assert add(client, amount)["status"] == "approved"


def test_personal_wallet_never_needs_approval(client):
    assert add(client, "5000", wallet=WALLET["Filip"])["status"] == "approved"


def test_tc_f8_02_author_cannot_approve(client):
    e = add(client, "500")
    resp = client.post(f"/wydatek/{e['id']}/zatwierdz", follow_redirects=True)
    assert "inny członek" in resp.get_data(as_text=True)
    assert query("SELECT status FROM expenses WHERE id = ?", e["id"])[0]["status"] == "pending"


def test_other_member_approves(client, daria):
    e = add(client, "500")
    daria.post(f"/wydatek/{e['id']}/zatwierdz")
    row = query("SELECT status, decided_by, decided_at FROM expenses WHERE id = ?", e["id"])[0]
    assert row["status"] == "approved" and row["decided_at"]
    assert row["decided_by"] == query("SELECT id FROM users WHERE name = 'Daria'")[0]["id"]


def test_rejected_expense_stays_in_history_without_counting(client, daria):
    e = add(client, "500", description="Telewizor")
    daria.post(f"/wydatek/{e['id']}/odrzuc")
    assert query("SELECT status FROM expenses WHERE id = ?", e["id"])[0]["status"] == "rejected"
    html = client.get(f"/portfel/{SHARED}").get_data(as_text=True)
    assert "Telewizor" in html and "odrzucony" in html
    daria.post(f"/wydatek/{e['id']}/zatwierdz")  # decyzja jest ostateczna
    assert query("SELECT status FROM expenses WHERE id = ?", e["id"])[0]["status"] == "rejected"


def test_non_member_cannot_decide(app, client):
    e = add(client, "500")
    outsider = login(app.test_client(), "Daria")
    with db.connect() as conn:
        conn.execute("DELETE FROM wallet_members WHERE wallet_id = ? AND user_id ="
                     " (SELECT id FROM users WHERE name = 'Daria')", (SHARED,))
    assert outsider.post(f"/wydatek/{e['id']}/zatwierdz").status_code == 404


def sums(client):
    """Suma miesiąca, kategorie i osoby z widoku portfela (kwoty jako tekst)."""
    return client.get(f"/portfel/{SHARED}?m={THIS_MONTH}").get_data(as_text=True)


def test_pending_not_in_sums(client, daria):
    before = query(
        "SELECT SUM(amount) FROM expenses WHERE wallet_id = ? AND status = 'approved'"
        " AND substr(spent_on, 1, 7) = ?", SHARED, THIS_MONTH)[0][0]
    add(client, "777,77")
    html = sums(client)
    assert "777,77" in html  # widoczny na liście i w karcie zatwierdzania
    assert format_zl(before) in html
    assert format_zl(before + 77777) not in html
    e = query("SELECT id FROM expenses WHERE amount = 77777")[0]
    daria.post(f"/wydatek/{e['id']}/zatwierdz")
    assert format_zl(before + 77777) in sums(client)


def test_owner_changes_threshold(app):
    owner = login(app.test_client(), "Valentyn")
    owner.post(f"/portfel/{SHARED}/prog", data={"threshold": "1000"})
    assert query("SELECT approval_threshold FROM wallets WHERE id = ?", SHARED)[0][0] == 100000
    assert add(owner, "500")["status"] == "approved"


def test_non_owner_cannot_change_threshold(client):
    assert client.post(f"/portfel/{SHARED}/prog", data={"threshold": "1"}).status_code == 403
    assert query("SELECT approval_threshold FROM wallets WHERE id = ?", SHARED)[0][0] == 20000


def test_invalid_threshold_is_rejected(app):
    owner = login(app.test_client(), "Valentyn")
    owner.post(f"/portfel/{SHARED}/prog", data={"threshold": "abc"})
    assert query("SELECT approval_threshold FROM wallets WHERE id = ?", SHARED)[0][0] == 20000
