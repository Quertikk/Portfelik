import re

import app as app_module


def test_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "z-env")
    assert app_module.load_secret_key() == "z-env"


def test_secret_key_file_is_stable(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert app_module.load_secret_key() == app_module.load_secret_key()


def test_session_cookie_flags(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_post_without_csrf_token_is_rejected(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    resp = client.post("/portfel/personal/dodaj", data={"amount": "5", "category_id": 1})
    assert resp.status_code == 400


def test_forms_carry_csrf_token(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    html = client.get("/portfel/personal").get_data(as_text=True)
    # przełącznik użytkownika, formularz dodawania i po jednym formularzu usuwania na własny wydatek
    assert len(re.findall(r'name="csrf_token" value="[^"]+"', html)) >= 2


def test_post_with_csrf_token_is_accepted(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    token = re.search(r'name="csrf_token" value="([^"]+)"',
                      client.get("/portfel/personal").get_data(as_text=True)).group(1)
    resp = client.post("/portfel/personal/dodaj",
                       data={"amount": "5", "category_id": 1, "csrf_token": token})
    assert resp.status_code == 302


def test_infinite_amount_does_not_crash(client):
    for amount in ("inf", "nan", "1e999", "-5", "0"):
        resp = client.post("/portfel/personal/dodaj", data={"amount": amount, "category_id": 1})
        assert resp.status_code == 302  # komunikat błędu, nie 500
