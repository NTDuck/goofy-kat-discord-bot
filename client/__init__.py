
from collections.abc import Mapping
from typing import Any, Union
import pickle

from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands
from redis.asyncio import Redis
import discord

from .annotations import GuildDataMapping, GuildVoiceDataMapping
from .const.audio import PAUSED
from logger import logger, queue_listener


class CustomClient(commands.Bot):
    def __init__(self, config: Mapping[str, Any], redis_cli: Redis, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.redis_cli = redis_cli
        self.logger = logger

    async def _get(self, id: int) -> GuildDataMapping:
        raw = await self.redis_cli.get(id)
        return pickle.loads(raw)

    async def _post(self, id: int, value: GuildDataMapping) -> None:
        raw = pickle.dumps(value)
        await self.redis_cli.set(id, raw)
    
    async def on_app_command_completion(self, interaction: discord.Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]):
        cmd = f"/{command.name}" if command.parent is None else f"/{command.parent.name} {command.name}"
        self.logger.debug(f"command {cmd} invoked by {interaction.user.name} (uid: {interaction.user.id}) completed without error")

    async def setup_hook(self):
        default_state: GuildVoiceDataMapping = {
            "voice": {
                "state": PAUSED,
                "queue": [],
            }
        }
        data = pickle.dumps(default_state)   # pickle serialization is done once & populate all guilds
        
        counter = 0
        guilds: list[discord.Guild] = []
        async for guild in self.fetch_guilds():
            counter += 1
            guilds.append(guild)
            await self.redis_cli.set(guild.id, data)
        self.logger.info(f"connected to {counter} guilds: {', '.join([f'{guild.name} (id: {guild.id})' for guild in guilds])}")

        await self.load_extension("client.cogs")

        app_commands = await self.tree.fetch_commands()
        await self.tree.sync()
        self.logger.info(f"synced {len(app_commands)} app commands: {', '.join(['/' + i.name for i in app_commands])}")

    async def on_ready(self):
        self.logger.info(f"logged in as {self.user.name} (id: {self.user.id})")

    async def start(self, session=None):
        if session is None:
            session = ClientSession()
        queue_listener.start()   # will sit in isolated thread
        async with (session, self):
            self.session = session
            await super().start(token=self.config["SECRET_TOKEN"])


# app factory pattern similar to flask
def create_client(config: Mapping[str, Any]):
    intents = discord.Intents.default()
    for attr, value in config["INTENTS"].items():
        setattr(intents, attr.lower(), value)

    activity = discord.Game(config["GAME_NAME"])
    redis_cli = Redis(**config["REDIS_CONFIG"])   # async cli

    client = CustomClient(
        intents=intents,
        command_prefix=commands.when_mentioned_or(config["COMMAND_PREFIX"]),
        activity=activity,
        config=config,
        redis_cli=redis_cli,
    )

    return client