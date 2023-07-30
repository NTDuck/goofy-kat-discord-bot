
from aiohttp import ClientSession
from discord import Intents, Game
from discord.ext.commands import Bot


class CustomBot(Bot):
    def __init__(self, config: dict, session: ClientSession, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.session = session


# app factory pattern similar to flask
async def create_app(config: dict) -> None:
    intents = Intents.default()
    for attr, value in config["INTENTS"].items():
        setattr(intents, attr.lower(), value)

    activity = Game(config["GAME_NAME"])
    session = ClientSession()

    bot = CustomBot(command_prefix=config["COMMAND_PREFIX"], intents=intents, activity=activity, config=config, session=session)

    await bot.load_extension("bot.cogs")

    # @bot.event
    # async def on_ready():
    #     await bot.tree.sync()

    async with (bot.session, bot):
        try:
            await bot.start(bot.config["SECRET_TOKEN"])
        except KeyboardInterrupt:
            return
        except Exception as exc:
            print(exc)   # replace with logging