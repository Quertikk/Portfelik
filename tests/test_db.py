import sqlite3

import db


def test_init_db_sets_version_and_seeds(app):
    with db.connect() as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRATIONS)
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == len(db.USERS)


def test_migrate_is_idempotent(app):
    with db.connect() as conn:
        db.migrate(conn)
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRATIONS)


def test_migrate_upgrades_legacy_db_without_user_version(tmp_path, monkeypatch):
    """Baza sprzed migracji (schemat jest, user_version = 0) dostaje wersję 1 i zachowuje dane."""
    path = tmp_path / "legacy.db"
    legacy = sqlite3.connect(path)
    legacy.executescript(db.MIGRATIONS[0])
    legacy.execute("INSERT INTO users (name) VALUES ('Stary')")
    legacy.commit()
    legacy.close()

    monkeypatch.setattr(db, "DB_PATH", path)
    db.init_db()
    with db.connect() as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRATIONS)
        assert [r["name"] for r in conn.execute("SELECT name FROM users")] == ["Stary"]


def test_failed_migration_rolls_back(tmp_path, monkeypatch):
    path = tmp_path / "broken.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    monkeypatch.setattr(db, "MIGRATIONS", [*db.MIGRATIONS, "CREATE TABLE t (id INTEGER); BOOM;"])
    try:
        db.init_db()
    except sqlite3.Error:
        pass
    with db.connect() as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRATIONS) - 1
        assert conn.execute("SELECT name FROM sqlite_master WHERE name = 't'").fetchone() is None


def test_init_db_without_demo_has_categories_but_no_users(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "prod.db")
    db.init_db()
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == len(db.CATEGORIES)


def test_demo_wallet_ids_match_conftest(app):
    from conftest import WALLET
    rows = db.connect().execute(
        "SELECT w.id, COALESCE(CASE w.kind WHEN 'personal' THEN u.name END, 'shared') AS who"
        " FROM wallets w LEFT JOIN users u ON u.id = w.owner_id").fetchall()
    assert {r["who"]: r["id"] for r in rows} == WALLET
