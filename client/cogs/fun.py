
import random
import secrets
from collections.abc import Mapping

import discord
from discord import app_commands
from discord.ext import commands

from . import CustomCog
from ..const.command import SUCCESS
from ..const.fetch import JSON, BINARY
from ..utils.cryptography import atbash, caesar, caesar_rev, base64, base64_rev, a1z26, a1z26_rev, morse, morse_rev
from ..utils.fetch import fetch
from ..utils.formatter import status_update_prefix as sup, incremental_response
from ..views.choice import MikuView
from ..views.tictactoe import TicTacToeView


class EncodeCog(commands.GroupCog, name="encode"):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__()

    @app_commands.command(description="encode something using a1z26 cipher.")
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: str):
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        enc_str = a1z26(str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"`{enc_str}`")
    
    @app_commands.command(description="encode something using atbash cipher.")
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: str):
        enc_str = atbash(str)
        await interaction.response.send_message(content=f"`{enc_str}`")

    @app_commands.command(description="encode something using caesar cipher.")
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: str):
        enc_str = caesar(str, shift=interaction.client.config["ENCODING"]["caesar"]["shift"])
        await interaction.response.send_message(content=f"`{enc_str}`")

    @app_commands.command(description="encode something using base64.")
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: str):
        enc_str = base64(str)
        await interaction.response.send_message(content=f"`{enc_str}`")

    @app_commands.command(description="encode something using international morse code.")
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: str):
        cfg = interaction.client.config["ENCODING"]["morse"]
        enc_str = morse(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"`{enc_str}`")


class DecodeCog(commands.GroupCog, name="decode"):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__()

    @app_commands.command(description="decode something using a1z26 cipher.")
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: str):
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        dec_str = a1z26_rev(
            str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"`{dec_str}`")

    @app_commands.command(description="decode something using atbash cipher.")
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: str):
        dec_str = atbash(str)
        await interaction.response.send_message(content=f"`{dec_str}`")

    @app_commands.command(description="decode something using caesar cipher.")
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: str):
        dec_str = caesar_rev(str, shift=interaction.client.config["ENCODING"]["caesar_shift"])
        await interaction.response.send_message(content=f"`{dec_str}`")

    @app_commands.command(description="decode something using base64.")
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: str):
        dec_str = base64_rev(str)
        await interaction.response.send_message(content=f"`{dec_str}`")

    @app_commands.command(description="decode something using international morse code.")
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: str):
        cfg = interaction.client.config["ENCODING"]["morse"]
        dec_str = morse_rev(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
            _null_repr=cfg["null_repr"],
        )
        await interaction.response.send_message(content=f"`{dec_str}`")


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
    @app_commands.command(description="play some tic-tac-toe with the bot.")
    @app_commands.describe(size="the size of the board")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def tictactoe(self, interaction: discord.Interaction, size: app_commands.Range[int, 3, 5]):
        await interaction.response.send_message(content="play a game of tic-tac-toe.", view=TicTacToeView(user=interaction.user, size=(size, size)))

    @app_commands.command(description="reverse provided string (really useful!)")
    @app_commands.describe(string="anything really")
    async def rev(self, interaction: discord.Interaction, string: str):
        await interaction.response.send_message(content=f"`{string[::-1]}`")