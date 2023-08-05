
from aiohttp import ClientSession
from discord import Intents, Game
from discord.ext.commands import Bot

from .const import PAUSED, PLAYING


class CustomBot(Bot):
    def __init__(self, config: dict, session: ClientSession, g: dict, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.session = session
        self.g = g   # aim to achieve flask's global object

    async def on_ready(self):
        print(f"logged in as {self.user} (id: {self.user.id})")
        print("----")

    async def setup_hook(self):
        async for guild in self.fetch_guilds():
            self.g.update({
                guild.id: {
                    "voice": {
                        "state": PAUSED,
                        "queue": [],
                    },
                },
            })
        # await self.tree.sync()
        await self.load_extension("bot.cogs")
        # await self.wait_until_ready()



# app factory pattern similar to flask
async def create_app(config: dict) -> None:
    intents = Intents.default()
    for attr, value in config["INTENTS"].items():
        setattr(intents, attr.lower(), value)

    activity = Game(config["GAME_NAME"])
    session = ClientSession()

    bot = CustomBot(command_prefix=config["COMMAND_PREFIX"], intents=intents, activity=activity, config=config, session=session, g={})

    async with (bot.session, bot):
        await bot.start(bot.config["SECRET_TOKEN"])