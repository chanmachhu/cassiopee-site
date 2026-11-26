import asyncio

import httpx
import pytest

from livredor import API_TIMEOUT, LivreDorIndisponible, fetch_last, format_messages


def test_format_escapes_discord_markup():
    out = format_messages([{"auteur": "**x**", "texte": "@everyone <@123456789012345678>"}])
    assert "@everyone" not in out.replace("@​everyone", "")
    assert "<@123456789012345678>" not in out
    assert "\\*\\*x\\*\\*" in out


def test_format_fits_discord_limit():
    msgs = [{"auteur": "a" * 50, "texte": "t" * 500} for _ in range(50)]
    assert len(format_messages(msgs)) <= 2000


def test_format_empty():
    assert format_messages([]) == "Le livre d'or est vide pour l'instant."


async def test_fetch_last_returns_messages():
    data = [{"id": 1, "auteur": "a", "texte": "b", "cree_le": "x"}]
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json=data))
    async with httpx.AsyncClient(transport=transport) as client:
        assert await fetch_last(client, "http://api") == data


async def test_fetch_last_handles_api_down():
    def down(request):
        raise httpx.ConnectError("boom")

    async with httpx.AsyncClient(transport=httpx.MockTransport(down)) as client:
        with pytest.raises(LivreDorIndisponible):
            await fetch_last(client, "http://api")


async def test_fetch_last_handles_timeout():
    def slow(request):
        raise httpx.ReadTimeout("slow")

    async with httpx.AsyncClient(transport=httpx.MockTransport(slow)) as client:
        with pytest.raises(LivreDorIndisponible):
            await fetch_last(client, "http://api")


def test_api_timeout_fits_discord_deadline():
    assert API_TIMEOUT.connect + API_TIMEOUT.read <= 2.5


def test_bot_client_uses_api_timeout():
    import bot

    assert bot.bot.http_client.timeout == API_TIMEOUT


async def test_fetch_last_rejects_non_list_payload():
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"detail": "oops"}))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(LivreDorIndisponible):
            await fetch_last(client, "http://api")


async def test_setup_hook_registers_sigterm_handler(monkeypatch):
    import signal

    import bot

    client = bot.Bot()
    calls = []
    monkeypatch.setattr(client.tree, "sync", lambda: asyncio.sleep(0))
    monkeypatch.setattr(
        asyncio.get_running_loop().__class__, "add_signal_handler", lambda self, sig, cb: calls.append(sig)
    )
    # discord.Client.loop is only available once login ran; set the running loop by hand.
    client.loop = asyncio.get_running_loop()
    await client.setup_hook()
    assert calls == [signal.SIGTERM]
    await client.http_client.aclose()
