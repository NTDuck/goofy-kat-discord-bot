
import pickle

from aiohttp import ClientSession
from discord import Intents, Game
from discord.ext.commands import Bot
from redis.asyncio import Redis

from .const import PAUSED


class CustomClient(Bot):
    def __init__(self, config: dict, session: ClientSession, redis_cli: Redis, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.session = session
        self.redis_cli = redis_cli

    async def _get(self, id) -> dict:
        raw = await self.redis_cli.get(id)
        return pickle.loads(raw)

    async def _post(self, id, value) -> None:
        raw = pickle.dumps(value)
        await self.redis_cli.set(id, raw)

    async def setup_hook(self):
        default_state = {
            "voice": {
                "state": PAUSED,
                "queue": [],
            }
        }
        data = pickle.dumps(default_state)   # pickle serialization is done once & populate all guilds
        async for guild in self.fetch_guilds():
            await self.redis_cli.set(guild.id, data)
        await self.load_extension("bot.cogs")
        # for c in self.tree.get_commands():
        #     print(c.name)
        await self.tree.sync()
        # await self.wait_until_ready()

    async def on_ready(self):
        print(f"logged in as {self.user} (id: {self.user.id})")
        print("----")

    async def start(self):
        async with (self.session, self):
            await super().start(token=self.config["SECRET_TOKEN"])

# app factory pattern similar to flask
def create_client(config: dict):
    intents = Intents.default()
    for attr, value in config["INTENTS"].items():
        setattr(intents, attr.lower(), value)

    activity = Game(config["GAME_NAME"])
    session = ClientSession()

    redis_cli = Redis(**config["REDIS_CONFIG"])   # async cli

    client = CustomClient(
        intents=intents,
        command_prefix=config["COMMAND_PREFIX"],
        activity=activity,
        config=config,
        session=session,
        redis_cli=redis_cli,
    )

    return client