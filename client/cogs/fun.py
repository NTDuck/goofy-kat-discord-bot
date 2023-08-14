
import random
import secrets
from collections.abc import Mapping

import discord
from discord import app_commands

from . import CustomCog
from ..const.command import SUCCESS
from ..const.fetch import JSON, BINARY
from ..utils.fetch import fetch
from ..utils.formatter import status_update_prefix as sup, incremental_response
from ..views.choice import MikuView


class FunCog(CustomCog):
    def __init__(self, client: discord.Client):
        self.client = client

    @app_commands.command(description="receive a random cat! yay!")
    @app_commands.checks.cooldown(rate=1, per=2.0, key=lambda i: (i.guild_id, i.user.id))
    async def cat(self, interaction: discord.Interaction):
        # children functions should return exactly 2 values
        async def _cataas(cfg: Mapping):
            url = cfg["url"]
            filename = secrets.token_hex(4) + ".png"
            return url, filename
        
        async def _thecatapi(cfg: Mapping):
            response = await fetch(interaction.client.session, url=cfg["url"], format=JSON, headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await interaction.edit_original_response(content=sup("cat don't wanna"))
                return
            url = response[0]["url"]
            filename = secrets.token_hex(4) + "." + url.split(".")[-1]
            return url, filename
        
        async def _shibe(cfg: Mapping):
            response = await fetch(interaction.client.session, url=cfg["url"], format=JSON, headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await interaction.edit_original_response(content=sup("cat don't wanna"))
                return
            url = response[0]
            filename = secrets.token_hex(4) + "." + url.split(".")[-1]
            return url, filename
        
        await self.notify(interaction)
        resp = await interaction.original_response()
        await resp.add_reaction(random.choice([
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]))

        cfg = interaction.client.config["API"]["cat"]
        src = random.choice(list(cfg))
        url, filename = await locals()[f"_{src}"](cfg[src])

        await interaction.edit_original_response(
            content=sup(f"bot `{interaction.client.user.name}` sent a cat", state=SUCCESS),
            attachments=[discord.File(fp=await fetch(interaction.client.session, url=url, format=BINARY), filename=filename)]
        )

    @app_commands.command(description="seek audience with the vocaloid anthropomorphism.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def miku(self, interaction: discord.Interaction):
        view = MikuView()
        await interaction.response.send_message(content="excuse me? are you british?", view=view)
        await view.wait()
        _d = {
            view.NO: "kiss your homie",
            view.YES: "oh no. oh no no no no no. hatsune miku does not talk to british people. the only pounds i need are me pounding your mom. se ka~",
            None: "kiss your sister",
        }
        await incremental_response(interaction, msg=_d[view.value])
            

    # gtn
    # rps
    @app_commands.command(description="play some tic-tac-toe.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def tictactoe(self, interaction: discord.Interaction):
        ...