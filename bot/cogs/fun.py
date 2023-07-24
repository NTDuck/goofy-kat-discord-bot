
from random import choice
from discord.ext.commands import command, Cog


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def choose(self, ctx, *args):
        await ctx.send(choice(args))