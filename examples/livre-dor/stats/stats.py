import os
import sys
from pathlib import Path

import psycopg

# Same schema file as the API (next to stats/ locally, in /srv in the image).
SCHEMA = Path(__file__).parents[1] / "schema.sql"


def refresh(conn) -> int:
    """Recompute messages per UTC day for the last 30 days; returns days written."""
    return conn.execute(
        """
        INSERT INTO stats (jour, messages)
        SELECT (cree_le AT TIME ZONE 'UTC')::date AS jour, count(*)
        FROM messages
        WHERE cree_le >= date_trunc('day', now() AT TIME ZONE 'UTC') - interval '29 days'
        GROUP BY jour
        ON CONFLICT (jour) DO UPDATE SET messages = EXCLUDED.messages
        """
    ).rowcount


def main() -> int:
    try:
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            conn.execute(SCHEMA.read_text())
            n = refresh(conn)
    except psycopg.Error as e:
        # Print the error only: the connection string holds the password.
        print(f"stats: error: {e}", file=sys.stderr)
        return 1
    print(f"stats: {n} jours mis à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
