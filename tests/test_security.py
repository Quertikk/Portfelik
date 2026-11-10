import re

import app as app_module
import auth as auth_module
import db

TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')


def csrf_client(app):
    """Klient z włączonym CSRF, zalogowany przez formularz z tokenem."""
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    token = TOKEN.search(client.get("/logowanie").get_data(as_text=True)).group(1)
    resp = client.post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD,
                                           "csrf_token": token})
    assert resp.status_code == 302
    return client


def test_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "z-env")
    assert app_module.load_secret_key() == "z-env"


def test_secret_key_file_is_stable(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert app_module.load_secret_key() == app_module.load_secret_key()


def test_session_cookie_flags(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_login_without_csrf_token_is_rejected(app):
    app.config["WTF_CSRF_ENABLED"] = True
    resp = app.test_client().post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD})
    assert resp.status_code == 400


def test_post_without_csrf_token_is_rejected(app):
    client = csrf_client(app)
    resp = client.post("/portfel/3/dodaj", data={"amount": "5", "category_id": 1})
    assert resp.status_code == 400


def test_forms_carry_csrf_token(app):
    html = csrf_client(app).get("/portfel/3").get_data(as_text=True)
    # wylogowanie, formularz dodawania i po jednym formularzu usuwania na własny wydatek
    assert len(TOKEN.findall(html)) >= 2


def test_post_with_csrf_token_is_accepted(app):
    client = csrf_client(app)
    token = TOKEN.search(client.get("/portfel/3").get_data(as_text=True)).group(1)
    resp = client.post("/portfel/3/dodaj",
                       data={"amount": "5", "category_id": 1, "csrf_token": token})
    assert resp.status_code == 302


def test_infinite_amount_does_not_crash(client):
    for amount in ("inf", "nan", "1e999", "-5", "0"):
        resp = client.post("/portfel/3/dodaj", data={"amount": amount, "category_id": 1})
        assert resp.status_code == 302  # komunikat błędu, nie 500


def test_security_headers(client):
    resp = client.get("/portfel/3")
    csp = resp.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in csp and "'unsafe-inline'" not in csp.split("style-src")[0]  # skrypty tylko 'self'
    assert resp.headers["X-Frame-Options"] == "DENY" and resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["Cache-Control"] == "no-store"
    html = resp.get_data(as_text=True)
    assert "onsubmit" not in html and "onfocus" not in html


def test_session_cookie_is_secure_by_default(app):
    assert app.config["SESSION_COOKIE_SECURE"] is True


def test_login_is_throttled_after_repeated_failures(anon):
    for _ in range(auth_module.LOGIN_TRIES):
        assert anon.post("/logowanie", data={"email": "filip@demo.pl", "password": "zle"}).status_code == 401
    # po limicie blokada działa także dla poprawnego hasła
    resp = anon.post("/logowanie", data={"email": "filip@demo.pl", "password": db.DEMO_PASSWORD})
    assert resp.status_code == 429
    assert anon.post("/logowanie", data={"email": "daria@demo.pl", "password": db.DEMO_PASSWORD}).status_code == 302


def test_unknown_email_also_checks_a_hash(anon, monkeypatch):
    checked = []
    monkeypatch.setattr(auth_module, "check_password_hash", lambda h, p: checked.append(h) is None and False)
    anon.post("/logowanie", data={"email": "nikt@example.com", "password": "x"})
    assert checked == [db.demo_hash()]  # czas odpowiedzi nie zdradza, że konta nie ma


def test_register_rejects_overlong_password(anon):
    resp = anon.post("/rejestracja", data={"name": "Ola", "email": "ola@example.com", "password": "x" * 129})
    assert resp.status_code == 400
