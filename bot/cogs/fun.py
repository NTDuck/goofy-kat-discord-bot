
import random
import secrets

from discord import app_commands, Client, File, Interaction

from . import CustomCog
from ..const.command import SUCCESS
from ..utils.fetch import fetch
from ..utils.formatter import status_update_prefix as sup


class FunCog(CustomCog):
    def __init__(self, client: Client):
        self.client = client

    # @app_commands.command(description="average miku conversation")
    # async def miku(self, interaction: Interaction):
    #     await interaction.response.send_message("are you british?")

    @app_commands.command(description="receive a random cat! yay!")
    @app_commands.checks.cooldown(rate=1, per=2.0, key=lambda i: (i.guild_id, i.user.id))
    async def cat(self, interaction: Interaction):
        # children functions should return exactly 2 values
        async def _cataas(cfg: dict):
            url = cfg["url"]
            filename = secrets.token_hex(4) + ".png"
            return url, filename
        
        async def _thecatapi(cfg: dict):
            response = await fetch(interaction.client.session, url=cfg["url"], format="json", headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await interaction.edit_original_response(content=sup("cat don't wanna"))
                return
            url = response[0]["url"]
            filename = secrets.token_hex(4) + "." + url.split(".")[-1]
            return url, filename
        
        async def _shibe(cfg: dict):
            response = await fetch(interaction.client.session, url=cfg["url"], format="json", headers=cfg.get("headers"), params=cfg.get("params"))
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
            attachments=[File(fp=await fetch(interaction.client.session, url=url, format="bin"), filename=filename)]
        )