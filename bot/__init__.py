
from aiohttp import ClientSession
from discord import Intents, Game
from discord.ext.commands import Bot


# app factory pattern similar to flask
async def create_app(config: dict) -> None:
    intents = Intents.default()
    intents.message_content = config["MESSAGE_CONTENT"]
    intents.typing = config["TYPING"]
    intents.presences = config["PRESENCES"]

    activity = Game(config["GAME_NAME"])
    session = ClientSession()

    bot = Bot(command_prefix=config["COMMAND_PREFIX"], intents=intents, activity=activity, session=session)

    bot.config = config
    bot.session = session

    await bot.load_extension("bot.cogs")

    # @bot.event
    # async def on_ready():
    #     await bot.tree.sync()

    async with (session, bot):
        try:
            await bot.start(config["SECRET_TOKEN"])
        except KeyboardInterrupt:
            return
        except Exception as exc:
            print(exc)   # replace with logging