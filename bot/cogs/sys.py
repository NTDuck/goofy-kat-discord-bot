
from discord.ext.commands import command, Cog


class Sys(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def ping(self, ctx):
        await ctx.send("pong!")