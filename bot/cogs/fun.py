
from random import choice
from discord.ext.commands import command, Cog


class FunCog(Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @command()
    async def choose(self, ctx, *args):
        await ctx.reply(choice(args))