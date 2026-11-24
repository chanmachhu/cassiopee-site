from datetime import date

from fastapi.testclient import TestClient

from app import create_app
from limits import Limiter
from store import DayStat, MemoryStore


def post(client, auteur="Ada", texte="Bonjour", **kw):
    return client.post("/api/messages", json={"auteur": auteur, "texte": texte}, **kw)


def test_post_then_list_newest_first(client):
    first = post(client, texte="un")
    assert first.status_code == 201
    post(client, texte="deux")
    body = client.get("/api/messages").json()
    assert [m["texte"] for m in body] == ["deux", "un"]
    assert set(body[0]) == {"id", "auteur", "texte", "cree_le"}
    assert body[0]["cree_le"].endswith("+00:00")


def test_limit_param(client):
    for i in range(3):
        post(client, texte=str(i))
    assert len(client.get("/api/messages?limit=2").json()) == 2
    assert client.get("/api/messages?limit=51").status_code == 422


def test_rejects_blank_or_too_long(client):
    assert post(client, auteur="   ").status_code == 422
    assert post(client, texte="   ").status_code == 422
    assert post(client, auteur="a" * 41).status_code == 422
    assert post(client, texte="t" * 281).status_code == 422
    assert post(client, auteur="a" * 40, texte="t" * 280).status_code == 201
    assert post(client, auteur="Ada", texte="🏛️🌿").status_code == 201


def test_strips_whitespace(client):
    assert post(client, auteur="  Ada ", texte=" hi ").json()["auteur"] == "Ada"


def test_keeps_markup_as_text(client):
    texte = "<img src=x onerror=alert(1)> @everyone"
    post(client, texte=texte)
    assert client.get("/api/messages").json()[0]["texte"] == texte


def test_delete_requires_token(client):
    mid = post(client).json()["id"]
    url = f"/api/messages/{mid}"
    assert client.delete(url).status_code == 401
    assert client.delete(url, headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.delete(url, headers={"Authorization": "Basic s3cret"}).status_code == 401
    assert client.delete(url, headers={"Authorization": "Bearer s3cret"}).status_code == 204
    assert client.delete(url, headers={"Authorization": "Bearer s3cret"}).status_code == 404


def test_delete_disabled_without_token():
    for token in (None, ""):
        c = TestClient(create_app(MemoryStore(), token, Limiter()))
        r = c.delete("/api/messages/1", headers={"Authorization": "Bearer "})
        assert r.status_code == 403


def test_global_rate_limit(client, clock):
    for i in range(30):
        assert post(client, auteur=f"a{i}", **{"headers": {"X-Forwarded-For": f"10.0.0.{i}"}}).status_code == 201
    assert post(client).status_code == 429
    clock.now += 61
    assert post(client).status_code == 201


def test_per_client_limit_only_when_trusted(clock):
    def make(trust):
        limiter = Limiter(global_per_min=30, per_client_per_min=2, trust_forwarded_for=trust, clock=clock)
        return TestClient(create_app(MemoryStore(), "t", limiter))

    def ip(n):
        return {"headers": {"X-Forwarded-For": f"{n}, 10.0.0.1"}}

    untrusted = make(False)
    assert [post(untrusted, **ip("1.1.1.1")).status_code for _ in range(3)] == [201, 201, 201]

    trusted = make(True)
    assert [post(trusted, **ip("1.1.1.1")).status_code for _ in range(3)] == [201, 201, 429]
    assert post(trusted, **ip("2.2.2.2")).status_code == 201


def test_stats_and_health(store, client):
    store.stats.append(DayStat(jour=date(2026, 1, 2), messages=4))
    assert client.get("/api/stats").json() == [{"jour": "2026-01-02", "messages": 4}]
    assert client.get("/health").status_code == 200
