
from discord import Intents
from discord.ext.commands import Bot
from .cogs import Sys, Fun


# app factory pattern similar to flask
async def create_app(config) -> Bot:
    intents = Intents.default()
    intents.message_content = getattr(config, "MESSAGE_CONTENT")

    bot = Bot(command_prefix=getattr(config, "COMMAND_PREFIX"), intents=intents)
    
    cogs = [Sys, Fun]
    for cog in cogs:
        await bot.add_cog(cog(bot))

    return bot