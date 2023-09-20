
from collections.abc import Mapping
import secrets

import discord

from ..fetch import fetch
from ..formatting import status_update_prefix as sup
from ...const.fetch import JSON


class CatApiHandler:
    """
    helper functions takes up exactly 2 arguments: `cfg` and `interaction` even if unused and return exactly 2 arguments: `url` and `filename`
    """
    @staticmethod
    async def _cataas(interaction: discord.Interaction, cfg: Mapping):
        url = cfg["url"]
        filename = secrets.token_hex(4) + ".png"
        return url, filename

    @staticmethod
    async def _thecatapi(interaction: discord.Interaction, cfg: Mapping):
        response = await fetch(interaction.client.session, url=cfg["url"], format=JSON, headers=cfg.get("headers"), params=cfg.get("params"))
        if response is None:
            await interaction.followup.send(sup("cat don't wanna"))
            return
        url: str = response[0]["url"]
        filename = secrets.token_hex(4) + "." + url.split(".")[-1]
        return url, filename

    @staticmethod
    async def _shibe(interaction: discord.Interaction, cfg: Mapping):
        response = await fetch(interaction.client.session, url=cfg["url"], format=JSON, headers=cfg.get("headers"), params=cfg.get("params"))
        if response is None:
            await interaction.followup.send(sup("cat don't wanna"))
            return
        url: str = response[0]
        filename = secrets.token_hex(4) + "." + url.split(".")[-1]
        return url, filename
    

