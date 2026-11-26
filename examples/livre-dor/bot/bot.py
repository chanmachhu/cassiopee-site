import asyncio
import os
import signal
import sys

import discord
import httpx
from discord import app_commands

from livredor import API_TIMEOUT, LivreDorIndisponible, fetch_last, format_messages

API_URL = os.environ.get("API_URL", "http://livre-dor-api")


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())  # no privileged intents
        self.tree = app_commands.CommandTree(self)
        self.http_client = httpx.AsyncClient(timeout=API_TIMEOUT)

    async def setup_hook(self):
        # run() ignores SIGTERM and we are PID 1: close cleanly instead of waiting for SIGKILL.
        self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.close()))
        await self.tree.sync()  # global registration; can take a few minutes to show up

    async def close(self):
        await self.http_client.aclose()
        await super().close()


bot = Bot()


@bot.tree.command(name="livredor", description="Les derniers messages du livre d'or")
async def livredor(interaction: discord.Interaction):
    try:
        messages = await fetch_last(bot.http_client, API_URL)
    except LivreDorIndisponible:
        await interaction.response.send_message(
            "Le livre d'or ne répond pas pour l'instant.", ephemeral=True
        )
        return
    await interaction.response.send_message(
        format_messages(messages), allowed_mentions=discord.AllowedMentions.none()
    )


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        sys.exit("DISCORD_TOKEN is not set")
    bot.run(token)
