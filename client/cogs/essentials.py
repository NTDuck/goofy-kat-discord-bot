
import random

import discord
from discord import app_commands

from . import CustomCog
from ..const.command import SUCCESS
from ..const.fetch import BINARY
from ..utils.fetch import fetch, callables
from ..utils.formatting import status_update_prefix as sup, incremental_response, c
from ..utils.media.cat import CatApiHandler
from ..views.choice import MikuView
from ..views.tictactoe import TicTacToeView


class MediaCog(CustomCog, name="media"):
    """we offer cat images. may the cat be with you."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<:layout_fluid:1153888205762990090>", **kwargs)

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=2.0, key=lambda i: (i.guild_id, i.user.id))
    async def cat(self, interaction: discord.Interaction):
        """receive a random cat! yay!"""       
        await interaction.response.defer()
        resp = await interaction.original_response()

        reactions = [
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]
        await resp.add_reaction(random.choice(reactions))

        cfg = interaction.client.config["API"]["cat"]
        src = random.choice(list(cfg))

        _callables = callables(CatApiHandler)
        
        url, filename = await _callables[f"_{src}"](interaction, cfg[src])

        fp = await fetch(interaction.client.session, url=url, format=BINARY)
        file = discord.File(fp=fp, filename=filename)

        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} sent a cat", state=SUCCESS), file=file)


class CasualGamesCog(CustomCog, name="games"):
    """behold, joy! have a little fun, enjoy yourself."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<:knight:1153695165286989874>", **kwargs)

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def miku(self, interaction: discord.Interaction):
        """seek audience with the vocaloid anthropomorphism."""
        view = MikuView(interaction=interaction)
        await interaction.response.send_message(content="excuse me? are you british?", view=view)
        await view.wait()
        _d = {
            view.NO: "k y s",
            view.YES: "oh no. oh no no no no no. hatsune miku does not talk to british people. the only pounds i need are me pounding your mom. se ka~",
            None: "k y s",
        }
        await incremental_response(interaction, msg=_d[view.value])

    # gtn
    # rps
    @app_commands.command()
    @app_commands.describe(size="the size of the board")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def tictactoe(self, interaction: discord.Interaction, size: app_commands.Range[int, 3, 5]):
        """play a game you can't lose. unless you're really dumb."""
        await interaction.response.defer()
        await interaction.followup.send("play a game of tic-tac-toe.", view=TicTacToeView(user=interaction.user, size=(size, size), interaction=interaction))


class EquilibriumCog(CustomCog, name="stories untold"):
    """countless stories untold - about the author."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<:shatter:1154051133824843809>", **kwargs)

    @app_commands.command()
    async def listen(self, interaction: discord.Interaction):
        """listen to a random story."""
        await interaction.response.send_message("i wish i were a bird")