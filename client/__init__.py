
from collections import OrderedDict
from collections.abc import Mapping
from typing import Any, List, Optional, Union
import datetime
import pickle

from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands
from redis.asyncio import Redis
import discord

from logger import logger, queue_listener
from .annotations import GuildDataMapping, GuildVoiceDataMapping
from .const.audio import PAUSED
from .utils.formatting import diff


class CustomClient(commands.Bot):
    def __init__(self, config: Mapping[str, Any], redis_cli: Redis, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.redis_cli = redis_cli
        self.logger = logger

    # minimal redis read-write
    async def _get(self, id: int) -> GuildDataMapping:
        raw = await self.redis_cli.get(id)
        return pickle.loads(raw)

    async def _post(self, id: int, value: GuildDataMapping) -> None:
        raw = pickle.dumps(value)
        await self.redis_cli.set(id, raw)
    
    # event monitoring
    # required intents: guilds, messages, members
    async def on_app_command_completion(self, interaction: discord.Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]):
        cmd = f"/{command.name}" if command.parent is None else f"/{command.parent.name} {command.name}"
        self.logger.debug(f"command {cmd} invoked by {interaction.user.name} (uid: {interaction.user.id}) completed without error")

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        self.logger.debug(f"channel {channel.name} (id: {channel.id}) in guild {channel.guild.name} (id: {channel.id}) created (url: {channel.jump_url})")
    
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        self.logger.debug(f"channel {channel.name} (id: {channel.id}) in guild {channel.guild.name} (id: {channel.id}) deleted (url: {channel.jump_url})")

    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        self.logger.debug(f"channel {before.name} -> {after.name} (id: {after.id}) in guild {after.guild.name} (id: {after.guild.id}) updated (url: {after.jump_url})")

    async def on_guild_channel_pins_update(self, channel: Union[discord.abc.GuildChannel, discord.Thread], last_pin: Optional[datetime.datetime]):
        self.logger.debug(f"channel {channel.name} in guild {channel.guild.name} (id: {channel.id}) pinned/unpinned a message (url: {channel.jump_url})")

    async def on_private_channel_update(self, before: discord.GroupChannel, after: discord.GroupChannel):
        self.logger.debug(f"private group channel {before.name} -> {after.name} (id: {after.id}) in guild {after.guild.name} (id: {after.guild.id}) updated (url: {after.jump_url})")

    async def on_private_channel_pins_update(self, channel: discord.abc.PrivateChannel, last_pin: Optional[datetime.datetime]):
        if isinstance(channel, discord.GroupChannel):   # else discord.DMChannel
            self.logger.debug(f"private group channel {channel.name} in guild {channel.guild.name} (id: {channel.id}) pinned/unpinned a message (url: {channel.jump_url})")
            return
        self.logger.debug(f"DM channel with recipient {channel.recipient.name if channel.recipient is not None else '[unresolved] (information unavailable, channel received through gateway)'} (id: {channel.id}) pinned/unpinned a message (url: {channel.jump_url})")

    # async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
    #     # already handled via on_app_command_error (?)
    #     return await super().on_error(event_method, *args, **kwargs)
    
    async def on_guild_available(self, guild: discord.Guild):
        self.logger.debug(f"{'large' if guild.large else ''} guild {guild.name} (id: {guild.id}) changed availability to available")

    # only id available, other attrs might be None
    async def on_guild_unavailable(self, guild: discord.Guild):
        self.logger.debug(f"guild {guild.name if guild.name is not None else '[unresolved]'} (id: {guild.id}) changed availability to unavailable")

    async def on_guild_join(self, guild: discord.Guild):
        self.logger.debug(f"joined guild {guild.name} (id: {guild.id})")

    async def on_guild_remove(self, guild: discord.Guild):
        self.logger.debug(f"removed from guild {guild.name} (id: {guild.id})")

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        self.logger.debug(f"guild {before.name} -> {after.name} (id: {after.id}) updated")

    async def on_member_join(self, member: discord.Member):
        self.logger.debug(f"member {member.name} (uid: {member.id}) joined guild {member.guild.name} (id: {member.guild.id})")

    async def on_member_remove(self, member: discord.Member):
        self.logger.debug(f"member {member.name} (uid: {member.id}) removed from guild {member.guild.name} (id: {member.guild.id})")

    # # called instead when guild/member not found in internal cache
    # async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent):
    #     self.logger.debug(f"member {payload.user.name} (uid: {payload.user.id}) removed from guild [unresolved] (id: {payload.guild_id})")

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_update
        _d = {
            "nick": {
                "repr": "nickname",
            },
            "roles": {
                "fmt": lambda _roles: ', '.join([role.name for role in _roles]),
            },
            "pending": {
                "repr": "pending verification",
            },
            "timed_out_until": {
                "repr": "timeout",
                "fmt": lambda _dtobj: _dtobj.strftime("%Y/%m/%d %H:%M:%S"),
            },
            "guild_avatar": {
                "repr": "guild avatar",
                "fmt": lambda _asset: f"{_asset.key} (url: {_asset.url})", 
            },
            "flags": {
                "fmt": lambda _memberflags: ', '.join([f"{attr}: {getattr(_memberflags, attr)}" for attr in {"value", "did_rejoin", "completed_onboarding", "bypasses_verification", "started_onboarding"}]),   # https://discordpy.readthedocs.io/en/stable/api.html#discord.MemberFlags
            },
        }
        _diff = diff(_d, before, after)
        self.logger.debug(f"member {after.name} (uid: {after.id}) in guild {after.guild.name} (id: {after.guild.id}) updated profile: {', '.join(_diff)}")

    async def on_user_update(self, before: discord.User, after: discord.User):
        # similar implementation to self.on_member_update
        _d = {
            "avatar": {
                "fmt": lambda _asset: f"{_asset.key} (url: {_asset.url})", 
            },
            "name": {
                "repr": "username",
            },
            "discriminator": None,   # legacy
        }
        _diff = diff(_d, before, after)
        self.logger.debug(f"user {after.name} (uid: {after.id}) updated profile: {', '.join(_diff)}")

    # required intents: moderation
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        self.logger.debug(f"user {user.name} (uid: {user.id}) banned from guild {guild.name} (id: {guild.id})")

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        self.logger.debug(f"user {user.name} (uid: {user.id}) unbanned from guild {guild.name} (id: {guild.id})")

    # required intents: presences, members
    # omitted due to spam
    # async def on_presence_update(self, before: discord.Member, after: discord.Member):
    #     _d = {
    #         "status": None,
    #         "activity": {
    #             "fmt": lambda _activity: _activity.name,
    #         }
    #     }
    #     _diff = diff(_d, before, after)
    #     self.logger.debug(f"member {after.name} (uid: {after.id}) in guild {after.guild.name} (id: {after.guild.id}) updated presence: {', '.join(_diff)}")

    # required intents: messages
    # omitted to avoid log spam
    # async def on_message(self, message: discord.Message):
    #     ...

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.id == self.user.id:
            return
        self.logger.debug(f"message {before.content} -> {after.content} (id: {after.id}) from member {after.author.name} (uid: {after.author.id}) in channel {before.channel.name} (id: {before.channel.id}) in guild {after.guild} {id: {after.guild.id}} edited (url: {after.jump_url})")

    async def on_message_delete(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        self.logger.debug(f"message {message.content} (id: {message.id}) from member {message.author.name} (uid: {message.author.id}) in channel {message.channel.name} (id: {message.channel.id}) in guild {message.guild} (id: {message.guild.id}) deleted")

    async def on_bulk_message_delete(self, messages: List[discord.Message]):
        _first = messages[0]
        self.logger.debug(f"{len(messages)} {', '.join([message.content for message in messages])} in channel {_first.channel.name} (id: {_first.channel.id}) in guild {_first.guild.name} (id: {_first.guild.id}) bulk-deleted")

    # # called regardless of internal message cache state
    # async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
    #     self.logger.debug(f"message {payload.cached_message.content if payload.cached_message is not None else '[unresolved]'} (id: {payload.message_id}) in channel [unresolved] (id: {payload.channel_id}) in guild [unresolved] (id: {payload.guild_id}) edited")

    # # called regardless of internal message cache state
    # async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
    #     self.logger.debug(f"message {payload.cached_message.content if payload.cached_message is not None else '[unresolved]'} (id: {payload.message_id}) in channel [unresolved] (id: {payload.channel_id}) in guild [unresolved] (id: {payload.guild_id}) deleted")

    # # called regardless of internal message cache state
    # async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
    #     self.logger.debug(f"{len({payload.cached_messages})} messages in channel [unresolved] (id: {payload.channel_id}) in guild [unresolved] (id: {payload.guild_id}) bulk-deleted")

    # do not listen to reactions

    # required intents: guilds
    async def on_guild_role_create(self, role: discord.Role):
        self.logger.debug(f"role {role.name} (id: {role.id}) in guild {role.guild.name} (id: {role.guild.id}) created")

    async def on_guild_role_delete(self, role: discord.Role):
        self.logger.debug(f"role {role.name} (id: {role.id}) in guild {role.guild.name} (id: {role.guild.id}) deleted")

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        attrs = ["id", "name", "guild", "hoist", "position", "unicode_emoji", "managed", "mentionable", "tags", "permissions", "color", "icon", "display_icon", "created_at", "mention", "members"]
        for attr in attrs:
            if getattr(before, attr) == getattr(after, attr):
                attrs.remove(attr)
        self.logger.debug(f"role {before.name} -> {after.name} updated: {', '.join(attrs)}")

    # required intents: guild_scheduled_events
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        self.logger.debug(f"scheduled event {event.name} (id: {event.id}) in channel {event.channel} (id: {event.channel_id}) in guild {event.guild.name} (id: {event.guild_id}) created by user {event.creator.name} (uid: {event.creator_id})")

    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent):
        self.logger.debug(f"scheduled event {event.name} (id: {event.id}) in channel {event.channel} (id: {event.channel_id}) in guild {event.guild.name} (id: {event.guild_id}) deleted")

    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent):
        attrs = ["id", "name", "description", "entity_type", "entity_id", "start_time", "end_time", "privacy_level", "status", "user_count", "creator", "creator_id", "location", "cover_image", "channel", "url"]
        for attr in attrs:
            if getattr(before, attr) == getattr(after, attr):
                attrs.remove(attr)
        self.logger.debug(f"scheduled event {before.name} -> {after.name} (id: {after.id}) in channel {after.channel.name} (id: {after.channel_id}) in guild {after.guild.name} (id: {after.guild_id}) updated: {', '.join(attrs)}")

    async def on_scheduled_event_user_add(self, event: discord.ScheduledEvent, user: discord.User):
        self.logger.debug(f"user {user.name} (uid: {user.id}) added to scheduled event {event.name} (id: {event.id}) in channel {event.channel} (id: {event.channel_id}) in guild {event.guild.name} (id: {event.guild_id})")

    async def on_scheduled_event_user_remove(self, event: discord.ScheduledEvent, user: discord.User):
        self.logger.debug(f"user {user.name} (uid: {user.id}) removed from scheduled event {event.name} (id: {event.id}) in channel {event.channel} (id: {event.channel_id}) in guild {event.guild.name} (id: {event.guild_id})")

    # let's skip the stage stuff
    # also skip the thread
    # the voice should not matter (that much) as well

    # real stuff
    async def setup_hook(self):
        await self.populate_data()
        await self.load_extension("client.cogs")
        self.create_cogs_mapping()
        await self.sync_app_commands()

    def create_cogs_mapping(self):
        """modify `self.cogs` into a `collections.OrderedDict` for help command purposes"""
        self.cogs_ordered = OrderedDict(sorted(self.cogs.items(), key=lambda item: item[1].index))   # don't know how this works

    async def populate_data(self):
        default_state: GuildVoiceDataMapping = {
            "voice": {
                "state": PAUSED,
                "queue": [],   # list[client.cogs.audio.AudioData]
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

    async def sync_app_commands(self):
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