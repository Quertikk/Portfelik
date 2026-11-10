"""NF7: czas ładowania portfela przy 1000 wydatków (cel: poniżej 1 s).

    python scripts/perf_check.py [liczba_wydatków]

Baza jest tymczasowa (portfelik.db nie jest ruszana). Wszystkie wydatki trafiają do bieżącego miesiąca
wspólnego portfela, bo widok miesiąca wypisuje wszystkie jego wydatki, a to najgorszy przypadek.
Mierzy aplikację bez sieci, czyli czas renderowania strony po stronie serwera.
"""
import statistics
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db  # noqa: E402

LIMIT_S = 1.0
RUNS = 10


def seed_expenses(n):
    """Dopisuje n zatwierdzonych wydatków do wspólnego portfela demo (id 4), rozłożonych na członków i kategorie."""
    today = date.today()
    with db.connect() as conn:
        users = [r[0] for r in conn.execute("SELECT id FROM users ORDER BY id")]
        cats = [r[0] for r in conn.execute("SELECT id FROM categories ORDER BY id")]
        conn.executemany(
            "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, comment, spent_on)"
            " VALUES (4, ?, ?, ?, ?, ?, ?)",
            [(users[i % len(users)], cats[i % len(cats)], 100 + i * 7 % 9000, f"Wydatek testowy {i}", "komentarz",
              today.replace(day=1 + i % min(today.day, 28)).isoformat()) for i in range(n)])


def measure(n=1000):
    """Zwraca (mediana, maksimum) czasu pobrania /portfel/4 w sekundach."""
    old_path = db.DB_PATH
    db.DB_PATH = Path(tempfile.mkdtemp()) / "perf.db"
    try:
        import app as app_module  # po podmianie ścieżki: import app tworzy bazę
        db.init_db(demo=True)
        seed_expenses(n)
        app_module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        client = app_module.app.test_client()
        client.post("/logowanie", data={"email": "valentyn@demo.pl", "password": db.DEMO_PASSWORD})
        client.get("/portfel/4")  # rozgrzewka: pierwszy render kompiluje szablony
        times = []
        for _ in range(RUNS):
            start = time.perf_counter()
            resp = client.get("/portfel/4")
            times.append(time.perf_counter() - start)
            assert resp.status_code == 200 and resp.get_data(as_text=True).count("Wydatek testowy") >= n
        return statistics.median(times), max(times)
    finally:
        db.DB_PATH = old_path


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    median, worst = measure(count)
    print(f"{count} wydatkow: mediana {median * 1000:.0f} ms, maksimum {worst * 1000:.0f} ms (limit {LIMIT_S * 1000:.0f} ms)")
    sys.exit(0 if worst < LIMIT_S else 1)
