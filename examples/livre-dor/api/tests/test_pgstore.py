import os
from pathlib import Path

import pytest

psycopg = pytest.importorskip("psycopg")
from store import PgStore  # noqa: E402

DSN = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="TEST_DATABASE_URL not set")


@pytest.fixture
def pg():
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP TABLE IF EXISTS messages, stats")
        conn.execute((Path(__file__).parents[2] / "schema.sql").read_text())
    return PgStore(DSN)


def test_messages_roundtrip(pg):
    a = pg.add_message("Ada", "un")
    b = pg.add_message("Bob", "deux")
    assert [m.id for m in pg.list_messages(10)] == [b.id, a.id]
    assert len(pg.list_messages(1)) == 1
    assert b.cree_le.tzinfo is not None
    assert pg.delete_message(a.id) is True
    assert pg.delete_message(a.id) is False


def test_stats_last_days(pg):
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("INSERT INTO stats VALUES (current_date, 3), (current_date - 40, 9)")
    assert [s.messages for s in pg.list_stats(30)] == [3]
