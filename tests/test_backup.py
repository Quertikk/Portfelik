import sqlite3
import sys
from pathlib import Path

import db

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from backup_db import backup  # noqa: E402


def test_backup_copies_data_and_rotates(app, tmp_path):
    out = tmp_path / "kopie"
    out.mkdir()
    for i in range(3):  # stare kopie; po rotacji zostaje najnowsza z nich i nowa
        (out / f"portfelik-2000010{i}-000000.db").write_bytes(b"")
    copy = backup(db.DB_PATH, out, keep=2)
    assert sorted(p.name for p in out.iterdir()) == ["portfelik-20000102-000000.db", copy.name]
    conn = sqlite3.connect(copy)
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == len(db.USERS)
    conn.close()
