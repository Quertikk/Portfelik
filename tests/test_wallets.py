"""F7 wspólny portfel i zaproszenia, NF4 izolacja danych."""
import re

import pytest

import db
from conftest import WALLET, login, query


def invite_code(client, wallet_id):
    assert client.post(f"/portfel/{wallet_id}/zaproszenie").status_code == 302
    return re.search(r"/dolacz/([\w-]+)", client.get(f"/portfel/{wallet_id}").get_data(as_text=True)).group(1)


def new_wallet(client, name="Wyjazd w góry"):
    resp = client.post("/portfele/nowy", data={"name": name})
    return int(resp.location.rsplit("/", 1)[1])


def test_index_redirects_to_personal_wallet(client):
    assert client.get("/").location.endswith(f"/portfel/{WALLET['Filip']}")


def test_create_shared_wallet_sets_owner_and_member(client):
    wid = new_wallet(client)
    row = query("SELECT w.kind, u.name FROM wallets w JOIN users u ON u.id = w.owner_id WHERE w.id = ?", wid)[0]
    assert (row["kind"], row["name"]) == ("shared", "Filip")
    assert query("SELECT COUNT(*) FROM wallet_members WHERE wallet_id = ?", wid)[0][0] == 1
    assert "Wyjazd w góry" in client.get(f"/portfel/{wid}").get_data(as_text=True)


def test_empty_wallet_name_is_rejected(client):
    before = query("SELECT COUNT(*) FROM wallets")[0][0]
    client.post("/portfele/nowy", data={"name": "  "})
    assert query("SELECT COUNT(*) FROM wallets")[0][0] == before


def test_invitation_lets_other_user_join(app, client):
    wid = new_wallet(client)
    code = invite_code(client, wid)
    other = login(app.test_client(), "Daria")
    assert other.get(f"/portfel/{wid}").status_code == 404  # przed dołączeniem
    assert other.get(f"/dolacz/{code}").location.endswith(f"/portfel/{wid}")
    assert other.get(f"/portfel/{wid}").status_code == 200
    other.get(f"/dolacz/{code}")  # ponowne wejście w link nie dubluje członkostwa
    assert query("SELECT COUNT(*) FROM wallet_members WHERE wallet_id = ?", wid)[0][0] == 2


def test_invitation_link_survives_login(app, client):
    wid = new_wallet(client)
    code = invite_code(client, wid)
    anon = app.test_client()
    resp = anon.get(f"/dolacz/{code}")
    assert "/logowanie" in resp.location and code in resp.location
    resp = anon.post("/logowanie", data={"email": "daria@demo.pl", "password": "demo1234", "next": f"/dolacz/{code}"})
    assert resp.location.endswith(f"/dolacz/{code}")


def test_expired_invitation_gives_message(app, client):
    wid = new_wallet(client)
    code = invite_code(client, wid)
    with db.connect() as conn:
        conn.execute("UPDATE invitations SET expires_at = datetime('now', '-1 minute') WHERE code = ?", (code,))
    other = login(app.test_client(), "Daria")
    resp = other.get(f"/dolacz/{code}", follow_redirects=True)
    assert "Zaproszenie wygasło" in resp.get_data(as_text=True)
    assert other.get(f"/portfel/{wid}").status_code == 404


def test_unknown_invitation_code(client):
    resp = client.get("/dolacz/nie-ma-takiego", follow_redirects=True)
    assert "Zaproszenie wygasło" in resp.get_data(as_text=True)


def test_personal_wallet_has_no_invitations(client):
    assert client.post(f"/portfel/{WALLET['Filip']}/zaproszenie").status_code == 404


def test_user_in_two_shared_wallets(client):
    wid = new_wallet(client)
    html = client.get(f"/portfel/{wid}").get_data(as_text=True)
    assert f"/portfel/{WALLET['shared']}" in html and f"/portfel/{wid}" in html
    assert client.post(f"/portfel/{wid}/dodaj", data={"amount": "10", "category_id": 1}).status_code == 302
    assert query("SELECT COUNT(*) FROM expenses WHERE wallet_id = ?", wid)[0][0] == 1
    assert query("SELECT COUNT(*) FROM expenses WHERE wallet_id = ? AND amount = 1000", WALLET["shared"])[0][0] == 0


# NF4: obcy portfel wygląda jak nieistniejący
@pytest.mark.parametrize("wallet", ["Valentyn", "shared_new"])
def test_user_gets_404_for_foreign_wallet(app, client, wallet):
    wid = new_wallet(client) if wallet == "shared_new" else WALLET[wallet]
    intruder = login(app.test_client(), "Daria") if wallet == "shared_new" else client
    before = query("SELECT COUNT(*) FROM expenses")[0][0]
    assert intruder.get(f"/portfel/{wid}").status_code == 404
    assert intruder.post(f"/portfel/{wid}/dodaj", data={"amount": "5", "category_id": 1}).status_code == 404
    assert intruder.post(f"/portfel/{wid}/zaproszenie").status_code == 404
    assert query("SELECT COUNT(*) FROM expenses")[0][0] == before


def test_nonexistent_wallet_is_404(client):
    assert client.get("/portfel/9999").status_code == 404


def test_new_invitation_link_revokes_previous_one(app, client):
    wid = new_wallet(client)
    old = invite_code(client, wid)
    new = invite_code(client, wid)
    assert old != new
    assert [r["code"] for r in query("SELECT code FROM invitations WHERE wallet_id = ?", wid)] == [new]
    other = login(app.test_client(), "Daria")
    assert "wygasło" in other.get(f"/dolacz/{old}", follow_redirects=True).get_data(as_text=True)
