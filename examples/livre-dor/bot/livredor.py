import httpx
from discord.utils import escape_markdown, escape_mentions

LIMIT = 2000  # Discord message size limit
ELLIPSIS = " …"
# Discord wants an acknowledgement within 3 s, so the whole API call must stay well under it.
API_TIMEOUT = httpx.Timeout(1.5, connect=1.0)  # connect + read <= 2.5 s


class LivreDorIndisponible(Exception):
    pass


async def fetch_last(client: httpx.AsyncClient, api_url: str, n: int = 5) -> list[dict]:
    try:
        r = await client.get(f"{api_url}/api/messages", params={"limit": n})
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise LivreDorIndisponible from e
    if not isinstance(data, list):
        raise LivreDorIndisponible(f"unexpected payload: {type(data).__name__}")
    return data


def _clean(s: str) -> str:
    return escape_mentions(escape_markdown(s))


def format_messages(messages: list[dict]) -> str:
    if not messages:
        return "Le livre d'or est vide pour l'instant."
    lines = [f"**{_clean(m['auteur'])}** — {_clean(m['texte'])}" for m in messages]
    out = "\n".join(lines)
    if len(out) <= LIMIT:
        return out
    # Hard cut (not on a line boundary); drop a trailing backslash so it cannot escape the ellipsis.
    out = out[: LIMIT - len(ELLIPSIS)]
    while out.endswith("\\"):
        out = out[:-1]
    return out + ELLIPSIS
