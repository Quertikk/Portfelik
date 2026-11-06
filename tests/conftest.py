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
    db.init_db()
    app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
