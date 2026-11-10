"""Baza danych Portfelika (SQLite): schemat i dane demonstracyjne."""
import sqlite3
from datetime import date, timedelta
from functools import cache
from pathlib import Path

from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).with_name("portfelik.db")

# Migracja n+1 to MIGRATIONS[n]; wersja bazy w PRAGMA user_version. Nowe zmiany dopisujemy na końcu, starych nie edytujemy.
MIGRATIONS = ["""
CREATE TABLE IF NOT EXISTS users (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS wallets (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    kind     TEXT NOT NULL CHECK (kind IN ('personal', 'shared')),
    owner_id INTEGER REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS wallet_members (
    wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    user_id   INTEGER NOT NULL REFERENCES users(id),
    PRIMARY KEY (wallet_id, user_id)
);
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    icon TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY,
    wallet_id   INTEGER NOT NULL REFERENCES wallets(id),
    user_id     INTEGER NOT NULL REFERENCES users(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount      INTEGER NOT NULL CHECK (amount > 0),  -- w groszach
    description TEXT NOT NULL DEFAULT '',
    spent_on    TEXT NOT NULL,                        -- RRRR-MM-DD
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""", """
-- F6: logowanie. SQLite nie dodaje kolumny UNIQUE, więc unikalność e-maila daje indeks.
ALTER TABLE users ADD COLUMN email TEXT;
ALTER TABLE users ADD COLUMN password_hash TEXT;
CREATE UNIQUE INDEX users_email ON users(email);
""", """
-- F7: zaproszenia do wspólnego portfela; expires_at w formacie datetime('now') (UTC)
CREATE TABLE invitations (
    id         INTEGER PRIMARY KEY,
    wallet_id  INTEGER NOT NULL REFERENCES wallets(id),
    code       TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL
);
""", """
-- F8: zatwierdzanie wspólnych wydatków powyżej progu (próg w groszach, domyślnie 200 zł)
ALTER TABLE wallets ADD COLUMN approval_threshold INTEGER NOT NULL DEFAULT 20000;
ALTER TABLE expenses ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'
    CHECK (status IN ('pending', 'approved', 'rejected'));
ALTER TABLE expenses ADD COLUMN decided_by INTEGER REFERENCES users(id);
ALTER TABLE expenses ADD COLUMN decided_at TEXT;
""", """
-- F10: miesięczne limity kategorii w portfelu (w groszach)
CREATE TABLE category_limits (
    wallet_id   INTEGER NOT NULL REFERENCES wallets(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount      INTEGER NOT NULL CHECK (amount > 0),
    PRIMARY KEY (wallet_id, category_id)
);
""", """
-- F9: komentarz do wydatku (do 200 znaków, widoczny na liście i przy zatwierdzaniu)
ALTER TABLE expenses ADD COLUMN comment TEXT NOT NULL DEFAULT '';
""", """
-- F13: subskrypcje użytkownika (miesięczne); dzień 29-31 w krótszym miesiącu liczy się jako ostatni dzień
CREATE TABLE subscriptions (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    name         TEXT NOT NULL,
    amount       INTEGER NOT NULL CHECK (amount > 0),
    day_of_month INTEGER NOT NULL CHECK (day_of_month BETWEEN 1 AND 31)
);
""", """
-- F14: skarbonka (wirtualna); jedno przeniesienie na portfel i miesiąc (month = RRRR-MM), kwota w groszach
CREATE TABLE piggy_deposits (
    wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    month     TEXT NOT NULL,
    amount    INTEGER NOT NULL CHECK (amount > 0),
    PRIMARY KEY (wallet_id, month)
);
"""]

USERS = ["Valentyn", "Daria", "Filip"]
DEMO_PASSWORD = "demo1234"  # opisane w README; konta demo tylko w trybie deweloperskim
CATEGORIES = [
    ("Jedzenie", "🛒"), ("Restauracje i kawiarnie", "☕"), ("Transport", "🚌"),
    ("Rachunki", "💡"), ("Rozrywka", "🎬"), ("Zakupy", "🛍️"),
    ("Subskrypcje", "🔁"), ("Inne", "📦"),
]
SHARED_WALLET = "Wspólne mieszkanie"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn):
    """Stosuje brakujące migracje; każda w jednej transakcji razem z podniesieniem user_version."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    for n, script in enumerate(MIGRATIONS[version:], start=version + 1):
        conn.executescript(f"BEGIN;{script};PRAGMA user_version = {n};COMMIT;")


def init_db(demo=False):
    """Migruje schemat i dodaje kategorie; z demo=True pusta baza dostaje konta i wydatki demonstracyjne."""
    with connect() as conn:
        migrate(conn)
        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            conn.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", CATEGORIES)
        if demo and conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            _seed(conn)


@cache
def demo_hash():
    return generate_password_hash(DEMO_PASSWORD)  # jeden skrót na proces: scrypt jest celowo wolny


def _seed(conn):
    for name in USERS:
        conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                     (name, f"{name.lower()}@demo.pl", demo_hash()))

    users = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM users ORDER BY id")}
    for name, uid in users.items():
        wid = conn.execute(
            "INSERT INTO wallets (name, kind, owner_id) VALUES (?, 'personal', ?)",
            (f"Portfel: {name}", uid)).lastrowid
        conn.execute("INSERT INTO wallet_members VALUES (?, ?)", (wid, uid))
    shared = conn.execute(
        "INSERT INTO wallets (name, kind, owner_id) VALUES (?, 'shared', ?)",
        (SHARED_WALLET, users[USERS[0]])).lastrowid
    for uid in users.values():
        conn.execute("INSERT INTO wallet_members VALUES (?, ?)", (shared, uid))

    cats = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM categories")}
    personal = {r["owner_id"]: r["id"] for r in
                conn.execute("SELECT id, owner_id FROM wallets WHERE kind = 'personal'")}
    first = date.today().replace(day=1)
    prev = (first - timedelta(days=1)).replace(day=1)

    # (portfel, kto, kategoria, kwota zł, opis, dzień miesiąca, który miesiąc)
    demo = [
        (shared, "Daria", "Rachunki", 240.00, "Prąd i gaz", 3, first),
        (shared, "Valentyn", "Jedzenie", 186.40, "Zakupy w Biedronce", 4, first),
        (shared, "Filip", "Rachunki", 60.00, "Internet", 2, first),
        (shared, "Filip", "Jedzenie", 74.15, "Lidl", 9, prev),
        (shared, "Daria", "Zakupy", 129.99, "Odkurzacz na promocji", 18, prev),
        (shared, "Valentyn", "Rachunki", 300.00, "Prąd i gaz", 3, prev),
        (personal[users["Valentyn"]], "Valentyn", "Restauracje i kawiarnie", 32.50, "Kawa z Darią", 2, first),
        (personal[users["Valentyn"]], "Valentyn", "Transport", 110.00, "Bilet miesięczny MPK", 1, first),
        (personal[users["Valentyn"]], "Valentyn", "Subskrypcje", 23.99, "Spotify", 4, first),
        (personal[users["Valentyn"]], "Valentyn", "Restauracje i kawiarnie", 89.00, "Pizza", 20, prev),
        (personal[users["Daria"]], "Daria", "Rozrywka", 45.00, "Kino", 3, first),
        (personal[users["Filip"]], "Filip", "Zakupy", 199.00, "Słuchawki", 1, first),
    ]
    for wallet, who, cat, zl, desc, day, month in demo:
        spent = month.replace(day=min(day, 28))
        if spent > date.today():
            spent = date.today()
        conn.execute(
            "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, spent_on)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (wallet, users[who], cats[cat], round(zl * 100), desc, spent.isoformat()))
    # wydatek powyżej progu 200 zł, czeka na decyzję kogoś innego niż Daria
    conn.execute(
        "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, spent_on, status)"
        " VALUES (?, ?, ?, 34900, 'Nowa pralka (połowa ceny)', ?, 'pending')",
        (shared, users["Daria"], cats["Zakupy"], first.isoformat()))
