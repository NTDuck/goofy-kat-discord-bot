
from discord.ext.commands import Bot, Cog, Context, command


class MiscCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def ping(self, ctx: Context):
        await ctx.send("pong!")