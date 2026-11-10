"""Sprint 3: uzupełnienie testów uprawnień (usuwanie, dostęp cudzy, niepoprawne dane) i ścieżek bez pokrycia."""
import pytest

import db
from conftest import WALLET, login, query

SHARED = WALLET["shared"]


def add(client, wallet=SHARED, **extra):
    data = {"amount": "10", "category_id": 1, "description": "x", **extra}
    client.post(f"/portfel/{wallet}/dodaj", data=data)
    return query("SELECT * FROM expenses ORDER BY id DESC LIMIT 1")[0]


@pytest.fixture
def daria(app):
    return login(app.test_client(), "Daria")


def test_author_deletes_own_expense(client):
    e = add(client)
    client.post(f"/wydatek/{e['id']}/usun")
    assert not query("SELECT 1 FROM expenses WHERE id = ?", e["id"])


def test_cannot_delete_someone_elses_expense(client, daria):
    e = add(client)
    resp = daria.post(f"/wydatek/{e['id']}/usun", follow_redirects=True)
    assert "tylko własne" in resp.get_data(as_text=True)
    assert query("SELECT 1 FROM expenses WHERE id = ?", e["id"])


def test_delete_requires_login(client, anon):
    e = add(client)
    assert anon.post(f"/wydatek/{e['id']}/usun").status_code == 302
    assert query("SELECT 1 FROM expenses WHERE id = ?", e["id"])


def test_member_of_other_wallet_cannot_see_expense_edit_or_decide(app, client):
    e = add(client, wallet=WALLET["Filip"], amount="5")
    daria = login(app.test_client(), "Daria")
    assert daria.get(f"/wydatek/{e['id']}/edytuj").status_code == 404
    assert daria.post(f"/wydatek/{e['id']}/zatwierdz").status_code == 404
    assert daria.post(f"/wydatek/{e['id']}/odrzuc").status_code == 404


def test_non_member_cannot_add_export_or_invite(app):
    foreign = login(app.test_client(), "Daria")  # portfel osobisty Filipa nie należy do Darii
    assert foreign.post(f"/portfel/{WALLET['Filip']}/dodaj", data={"amount": "1", "category_id": 1}).status_code == 404
    assert foreign.post(f"/portfel/{WALLET['Filip']}/zaproszenie").status_code == 404
    assert foreign.post(f"/portfel/{WALLET['Filip']}/limity", data={}).status_code == 404


def test_non_owner_cannot_set_limits(app):
    resp = login(app.test_client(), "Daria").post(f"/portfel/{SHARED}/limity", data={"limit_1": "100"})
    assert resp.status_code == 403
    assert not query("SELECT 1 FROM category_limits")


def test_already_decided_expense_cannot_be_decided_again(client, daria):
    e = add(client, amount="500")
    daria.post(f"/wydatek/{e['id']}/zatwierdz")
    resp = daria.post(f"/wydatek/{e['id']}/odrzuc", follow_redirects=True)
    assert "nie czeka już" in resp.get_data(as_text=True)
    assert query("SELECT status FROM expenses WHERE id = ?", e["id"])[0][0] == "approved"


def test_invalid_date_is_not_saved(client):
    before = len(query("SELECT 1 FROM expenses"))
    resp = client.post(f"/portfel/{SHARED}/dodaj", data={"amount": "10", "category_id": 1, "spent_on": "2026-13-45"},
                       follow_redirects=True)
    assert "poprawną kwotę, kategorię i datę" in resp.get_data(as_text=True)
    assert len(query("SELECT 1 FROM expenses")) == before


def test_unknown_category_is_not_saved(client):
    before = len(query("SELECT 1 FROM expenses"))
    client.post(f"/portfel/{SHARED}/dodaj", data={"amount": "10", "category_id": 999})
    assert len(query("SELECT 1 FROM expenses")) == before


def test_register_form_is_shown(anon):
    assert anon.get("/rejestracja").status_code == 200


def test_user_without_wallet_gets_404_on_index(app):
    with db.connect() as conn:
        conn.execute("DELETE FROM wallet_members WHERE user_id = 3")
    client = app.test_client()
    with client.session_transaction() as s:
        s["user_id"] = 3
    assert client.get("/").status_code == 404
