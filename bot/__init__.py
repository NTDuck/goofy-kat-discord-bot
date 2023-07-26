
from os.path import basename, dirname
from discord import Intents, Game
from discord.ext.commands import Bot


# app factory pattern similar to flask
async def create_app(config: dict) -> Bot:
    intents = Intents.default()
    intents.message_content = config["MESSAGE_CONTENT"]

    activity = Game(config["GAME_NAME"])

    bot = Bot(command_prefix=config["COMMAND_PREFIX"], intents=intents, activity=activity)
    bot.config = config
    await bot.load_extension(f"{basename(dirname(__file__))}.cogs")

    return bot