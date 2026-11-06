import pytest

import db
from conftest import query


def register(client, name="Ola", email="ola@example.com", password="tajnehaslo", **extra):
    return client.post("/rejestracja", data={"name": name, "email": email, "password": password, **extra})


def test_register_creates_user_with_hash_and_personal_wallet(anon):
    resp = register(anon)
    assert resp.status_code == 302
    user = query("SELECT * FROM users WHERE email = 'ola@example.com'")[0]
    assert user["password_hash"] != "tajnehaslo" and user["password_hash"].startswith(("scrypt:", "pbkdf2:"))
    assert query("SELECT kind FROM wallets WHERE owner_id = ?", user["id"])[0]["kind"] == "personal"
    assert anon.get("/").status_code == 302  # zalogowany od razu: / prowadzi do portfela, nie do logowania
    assert "/logowanie" not in anon.get("/").location


@pytest.mark.parametrize("data", [
    {"password": "krotkie"},             # 7 znaków
    {"email": "bez-malpy"},
    {"name": "  "},
    {"email": "FILIP@demo.pl"},          # e-mail zajęty (wielkość liter bez znaczenia)
    {"name": "Filip"},                   # nazwa zajęta
])
def test_register_rejects_invalid_data(anon, data):
    before = query("SELECT COUNT(*) FROM users")[0][0]
    assert register(anon, **data).status_code == 400
    assert query("SELECT COUNT(*) FROM users")[0][0] == before


def test_login_and_logout(anon):
    resp = anon.post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD})
    assert resp.status_code == 302
    assert anon.get("/portfel/personal").status_code == 200
    anon.post("/wyloguj")
    assert "/logowanie" in anon.get("/portfel/personal").location


def test_wrong_password_and_unknown_email_give_same_message(anon):
    wrong_pass = anon.post("/logowanie", data={"email": "filip@demo.pl", "password": "zlehaslo1"})
    no_user = anon.post("/logowanie", data={"email": "nikt@demo.pl", "password": "zlehaslo1"})
    assert wrong_pass.status_code == no_user.status_code == 401
    msg = "Nieprawidłowy e-mail lub hasło."
    assert msg in wrong_pass.get_data(as_text=True) and msg in no_user.get_data(as_text=True)


@pytest.mark.parametrize("url", ["/", "/portfel/personal", "/portfel/shared"])
def test_pages_require_login(anon, url):
    resp = anon.get(url)
    assert resp.status_code == 302 and "/logowanie" in resp.location


def test_post_requires_login(anon):
    resp = anon.post("/portfel/personal/dodaj", data={"amount": "5", "category_id": 1})
    assert "/logowanie" in resp.location
    assert query("SELECT COUNT(*) FROM expenses WHERE description = ''")[0][0] == 0


def test_login_redirects_back_to_next(anon):
    resp = anon.post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD,
                                         "next": "/portfel/shared"})
    assert resp.location.endswith("/portfel/shared")


@pytest.mark.parametrize("evil", ["https://evil.example", "//evil.example", "/\\evil.example"])
def test_login_ignores_external_next(anon, evil):
    resp = anon.post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD, "next": evil})
    assert "evil" not in resp.location


def test_user_switcher_removed(client):
    assert client.post("/user", data={"user_id": 1}).status_code in (404, 405)
    assert "Jestem:" not in client.get("/portfel/personal").get_data(as_text=True)
