import httpx
from discord.utils import escape_markdown, escape_mentions

LIMIT = 2000  # Discord message size limit
ELLIPSIS = " …"


class LivreDorIndisponible(Exception):
    pass


async def fetch_last(client: httpx.AsyncClient, api_url: str, n: int = 5) -> list[dict]:
    try:
        r = await client.get(f"{api_url}/api/messages", params={"limit": n})
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise LivreDorIndisponible from e


def _clean(s: str) -> str:
    return escape_mentions(escape_markdown(s))


def format_messages(messages: list[dict]) -> str:
    if not messages:
        return "Le livre d'or est vide pour l'instant."
    lines = [f"**{_clean(m['auteur'])}** — {_clean(m['texte'])}" for m in messages]
    out = "\n".join(lines)
    if len(out) <= LIMIT:
        return out
    # Cut on a line boundary, then shorten the last kept line; never inside an escape pair.
    out = out[: LIMIT - len(ELLIPSIS)]
    while out.endswith("\\"):
        out = out[:-1]
    return out + ELLIPSIS
