"""NF11: spójna kopia bazy (odpowiednik `sqlite3 .backup`) do katalogu backups/, zostawia KEEP najnowszych.

Uruchomienie (lokalnie lub jako zadanie okresowe na serwerze):
    python scripts/backup_db.py [katalog_docelowy]
Przywrócenie: zatrzymać aplikację i skopiować wybraną kopię na miejsce portfelik.db.
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP = 14


def backup(db_path, target_dir, keep=KEEP):
    target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)  # kopie zawierają skróty haseł
    target = target_dir / f"portfelik-{datetime.now():%Y%m%d-%H%M%S}.db"
    src, dst = sqlite3.connect(db_path), sqlite3.connect(target)
    try:
        src.backup(dst)  # bezpieczne także przy działającej aplikacji
    finally:
        dst.close()
        src.close()
    for old in sorted(target_dir.glob("portfelik-*.db"))[:-keep]:
        old.unlink()
    return target


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "backups"
    print(backup(ROOT / "portfelik.db", out))
