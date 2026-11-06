"""F9 komentarz i F19 edycja wydatku."""
import pytest

from conftest import WALLET, login, query

SHARED = WALLET["shared"]


def add(client, amount="10", wallet=SHARED, **extra):
    client.post(f"/portfel/{wallet}/dodaj", data={"amount": amount, "category_id": 1, **extra})
    return query("SELECT * FROM expenses ORDER BY id DESC LIMIT 1")[0]


def edit(client, e, **changes):
    data = {"amount": f"{e['amount'] / 100:.2f}", "category_id": e["category_id"], "spent_on": e["spent_on"],
            "description": e["description"], "comment": e["comment"], **changes}
    resp = client.post(f"/wydatek/{e['id']}/edytuj", data=data)
    return resp, query("SELECT * FROM expenses WHERE id = ?", e["id"])[0]


@pytest.fixture
def daria(app):
    return login(app.test_client(), "Daria")


def test_comment_saved_and_visible(client):
    e = add(client, comment="Kupione na promocji")
    assert e["comment"] == "Kupione na promocji"
    assert "Kupione na promocji" in client.get(f"/portfel/{SHARED}").get_data(as_text=True)


def test_comment_is_cut_to_200_chars(client):
    assert len(add(client, comment="x" * 300)["comment"]) == 200


def test_comment_visible_when_approving(client, daria):
    add(client, "500", comment="Pralka się zepsuła")
    html = daria.get(f"/portfel/{SHARED}").get_data(as_text=True)
    approval_card = html.split("Do zatwierdzenia")[1].split("Dodaj wydatek")[0]
    assert "Pralka się zepsuła" in approval_card


def test_description_not_hidden_on_mobile(client):
    """NF1: brak reguły CSS chowającej kolumnę z opisem na wąskim ekranie."""
    css = client.get("/static/style.css").get_data(as_text=True)
    assert "nth-child(3)" not in css


def test_edit_own_expense(client):
    e = add(client, "10", description="stary")
    assert client.get(f"/wydatek/{e['id']}/edytuj").status_code == 200
    resp, row = edit(client, e, amount="12,34", category_id=2, spent_on="2026-01-15",
                     description="nowy", comment="poprawka")
    assert resp.status_code == 302
    assert (row["amount"], row["category_id"], row["spent_on"], row["description"], row["comment"]) == \
        (1234, 2, "2026-01-15", "nowy", "poprawka")


def test_cannot_edit_someone_elses_expense(client, daria):
    e = add(client, "10", description="Filipa")
    assert daria.get(f"/wydatek/{e['id']}/edytuj").status_code == 404
    resp, row = edit(daria, e, amount="1", description="podmiana")
    assert resp.status_code == 404 and row["description"] == "Filipa"


def test_invalid_edit_changes_nothing(client):
    e = add(client, "10")
    _, row = edit(client, e, amount="abc")
    assert row["amount"] == 1000


def test_raising_approved_amount_above_threshold_needs_approval_again(client, daria):
    e = add(client, "500")
    daria.post(f"/wydatek/{e['id']}/zatwierdz")
    e = query("SELECT * FROM expenses WHERE id = ?", e["id"])[0]
    _, row = edit(client, e, amount="600")
    assert row["status"] == "pending" and row["decided_by"] is None


def test_approved_expense_edited_below_threshold_stays_approved(client):
    e = add(client, "100")
    _, row = edit(client, e, amount="150")
    assert row["status"] == "approved"


def test_editing_description_only_keeps_approval(client, daria):
    e = add(client, "500")
    daria.post(f"/wydatek/{e['id']}/zatwierdz")
    e = query("SELECT * FROM expenses WHERE id = ?", e["id"])[0]
    _, row = edit(client, e, description="inny opis")
    assert row["status"] == "approved"


def test_rejected_expense_stays_rejected(client, daria):
    e = add(client, "500")
    daria.post(f"/wydatek/{e['id']}/odrzuc")
    e = query("SELECT * FROM expenses WHERE id = ?", e["id"])[0]
    _, row = edit(client, e, amount="50")
    assert row["status"] == "rejected"
