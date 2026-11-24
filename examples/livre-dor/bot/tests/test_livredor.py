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
