from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Protocol

import psycopg


@dataclass
class Message:
    id: int
    auteur: str
    texte: str
    cree_le: datetime


@dataclass
class DayStat:
    jour: date
    messages: int


class Store(Protocol):
    def list_messages(self, limit: int) -> list[Message]: ...
    def add_message(self, auteur: str, texte: str) -> Message: ...
    def delete_message(self, id: int) -> bool: ...
    def list_stats(self, days: int) -> list[DayStat]: ...


class MemoryStore:
    def __init__(self):
        self.messages: list[Message] = []
        self.stats: list[DayStat] = []

    def list_messages(self, limit):
        return self.messages[::-1][:limit]

    def add_message(self, auteur, texte):
        next_id = self.messages[-1].id + 1 if self.messages else 1
        msg = Message(next_id, auteur, texte, datetime.now(timezone.utc))
        self.messages.append(msg)
        return msg

    def delete_message(self, id):
        before = len(self.messages)
        self.messages = [m for m in self.messages if m.id != id]
        return len(self.messages) < before

    def list_stats(self, days):
        return sorted(self.stats, key=lambda s: s.jour)


class PgStore:
    """One short-lived connection per call: simple, and enough for a guestbook."""

    def __init__(self, dsn: str):
        self.dsn = dsn

    def list_messages(self, limit):
        with psycopg.connect(self.dsn) as conn:
            rows = conn.execute(
                "SELECT id, auteur, texte, cree_le FROM messages ORDER BY id DESC LIMIT %s", (limit,)
            ).fetchall()
        return [Message(*r) for r in rows]

    def add_message(self, auteur, texte):
        with psycopg.connect(self.dsn) as conn:
            row = conn.execute(
                "INSERT INTO messages (auteur, texte) VALUES (%s, %s) RETURNING id, auteur, texte, cree_le",
                (auteur, texte),
            ).fetchone()
        return Message(*row)

    def delete_message(self, id):
        with psycopg.connect(self.dsn) as conn:
            return conn.execute("DELETE FROM messages WHERE id = %s", (id,)).rowcount > 0

    def list_stats(self, days):
        with psycopg.connect(self.dsn) as conn:
            rows = conn.execute(
                "SELECT jour, messages FROM stats WHERE jour > current_date - %s ORDER BY jour", (days,)
            ).fetchall()
        return [DayStat(*r) for r in rows]
