
from discord.ext.commands import command, Cog


class MiscCog(Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @command()
    async def ping(self, ctx):
        await ctx.reply("pong!")