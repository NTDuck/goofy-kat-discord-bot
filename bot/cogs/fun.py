
import random

from discord import File
from discord.ext.commands import Cog, Context, command
from ..utils import fetch


class FunCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def choose(self, ctx: Context, *args):
        await ctx.send(random.choice(args) if args else "there's nothing to choose you idiot")

    @command()
    async def miku(self, ctx: Context):
        await ctx.send("are you british?")

    @command()
    async def cat(self, ctx: Context):
        await ctx.message.add_reaction(random.choice([
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]))
        cfg = self.bot.config["API"]["https://thecatapi.com/"]
        response = await fetch(self.bot.session, url=cfg["url"], return_format="json", headers=cfg["headers"], params=cfg["params"])
        if response is None:
            await ctx.send("cat don't wanna.")
            return
        response_url = response[0]["url"]
        await ctx.send(file=File(fp=await fetch(self.bot.session, url=response_url, return_format="bin"), filename=response_url))