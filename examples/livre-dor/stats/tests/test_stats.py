import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import pytest

import stats

DSN = os.environ.get("TEST_DATABASE_URL")
SCHEMA = Path(__file__).parents[2] / "schema.sql"


@pytest.mark.skipif(not DSN, reason="TEST_DATABASE_URL not set")
def test_refresh_counts_per_day_and_is_idempotent():
    now = datetime.now(timezone.utc).replace(hour=12)
    d1, d2 = now - timedelta(days=2), now - timedelta(days=1)
    with psycopg.connect(DSN) as conn:
        conn.execute(SCHEMA.read_text())
        conn.execute("TRUNCATE messages, stats")
        for when in (d1, d1, d2):
            conn.execute("INSERT INTO messages (auteur, texte, cree_le) VALUES ('a', 't', %s)", (when,))
        for _ in range(2):
            assert stats.refresh(conn) == 2
            rows = conn.execute("SELECT jour, messages FROM stats ORDER BY jour").fetchall()
            assert rows == [(d1.date(), 2), (d2.date(), 1)]


def test_main_failure_exits_1_without_leaking_dsn(monkeypatch, capsys):
    def boom(*a, **k):
        raise psycopg.OperationalError("connection refused")

    monkeypatch.setenv("DATABASE_URL", "postgresql://u:hunter2@h:5432/d")
    monkeypatch.setattr(psycopg, "connect", boom)
    assert stats.main() == 1
    out = capsys.readouterr()
    assert "hunter2" not in out.out + out.err
