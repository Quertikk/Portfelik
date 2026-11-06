import tempfile
from pathlib import Path

import pytest

import db

# app.py wywołuje db.init_db() przy imporcie, więc ścieżkę podmieniamy przed importem (nie dotykamy portfelik.db).
db.DB_PATH = Path(tempfile.mkdtemp()) / "import.db"

import app as app_module  # noqa: E402


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Aplikacja z czystą bazą (dane demo) w katalogu tymczasowym i wyłączonym CSRF."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db(demo=True)
    app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app_module.app


def login(client, name="Filip"):
    resp = client.post("/logowanie", data={"email": f"{name.lower()}@demo.pl", "password": db.DEMO_PASSWORD})
    assert resp.status_code == 302, resp.get_data(as_text=True)
    return client


@pytest.fixture
def anon(app):
    """Klient bez logowania."""
    return app.test_client()


@pytest.fixture
def client(app):
    """Klient zalogowany jako Filip (konto demo)."""
    return login(app.test_client())


def query(sql, *args):
    with db.connect() as conn:
        return conn.execute(sql, args).fetchall()


# Identyfikatory portfeli demo wynikają z kolejności w db._seed (sprawdza je test_db).
WALLET = {"Valentyn": 1, "Daria": 2, "Filip": 3, "shared": 4}
