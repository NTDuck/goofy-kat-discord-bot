
import random

from discord import File
from discord.ext.commands import Cog, command

from ..utils import random_cat


class FunCog(Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @command()
    async def choose(self, ctx, *args):
        await ctx.send(random.choice(args))

    @command()
    async def cat(self, ctx):
        await ctx.message.add_reaction(random.choice([
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]))
        await ctx.send(file=File(fp=await random_cat(), filename="cat.png", spoiler=True))