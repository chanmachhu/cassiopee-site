import hmac
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import psycopg
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from pydantic import BaseModel, StringConstraints

from limits import Limiter
from store import PgStore, Store

log = logging.getLogger("livre-dor")

Auteur = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=280)]


class NewMessage(BaseModel):
    auteur: Auteur
    texte: Texte


def create_app(store: Store, admin_token: str | None, limiter: Limiter) -> FastAPI:
    app = FastAPI(title="Livre d'or")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/messages")
    def list_messages(limit: Annotated[int, Query(ge=1, le=50)] = 20):
        return [asdict(m) for m in store.list_messages(limit)]

    @app.post("/api/messages", status_code=201)
    def add_message(body: NewMessage, request: Request):
        if not limiter.allow(request.headers.get("x-forwarded-for")):
            raise HTTPException(429, "Trop de messages, réessayez dans une minute")
        return asdict(store.add_message(body.auteur, body.texte))

    @app.delete("/api/messages/{id}", status_code=204)
    def delete_message(id: int, authorization: Annotated[str | None, Header()] = None):
        if not admin_token:  # never open when the secret is missing
            raise HTTPException(403, "Suppression désactivée")
        scheme, _, token = (authorization or "").partition(" ")
        if scheme != "Bearer" or not hmac.compare_digest(token.encode(), admin_token.encode()):
            raise HTTPException(401, "Jeton invalide", headers={"WWW-Authenticate": "Bearer"})
        if not store.delete_message(id):
            raise HTTPException(404, "Message inconnu")
        return Response(status_code=204)

    @app.get("/api/stats")
    def stats():
        return [asdict(s) for s in store.list_stats(30)]

    return app


def apply_schema(dsn: str, attempts: int = 3, delay: float = 5):
    schema = (Path(__file__).parent.parent / "schema.sql").read_text()
    for n in range(1, attempts + 1):
        try:
            with psycopg.connect(dsn) as conn:
                conn.execute(schema)
            return
        except psycopg.OperationalError as e:
            log.error("database not ready (%d/%d): %s", n, attempts, e)
            if n == attempts:
                # Exit so the platform restarts us and shows why in the status.
                raise SystemExit(f"database unreachable after {attempts} attempts: {e}")
            time.sleep(delay)


def from_env() -> FastAPI:
    dsn = os.environ["DATABASE_URL"]
    apply_schema(dsn)
    limiter = Limiter(
        global_per_min=int(os.environ.get("RATE_GLOBAL_PER_MIN", 30)),
        per_client_per_min=int(os.environ.get("RATE_PER_CLIENT_PER_MIN", 5)),
        trust_forwarded_for=os.environ.get("TRUST_FORWARDED_FOR", "false").lower() == "true",
    )
    return create_app(PgStore(dsn), os.environ.get("ADMIN_TOKEN"), limiter)


def __getattr__(name):
    # `uvicorn app:app` builds the app on first access, so importing this module (tests) needs no database.
    if name == "app":
        globals()["app"] = from_env()
        return globals()["app"]
    raise AttributeError(name)
