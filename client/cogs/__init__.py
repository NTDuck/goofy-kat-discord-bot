
from typing import Optional

from discord import app_commands
from discord.ext import commands
import discord

from logger import logger as root
from ..const.command import PENDING
from ..utils.formatting import status_update_prefix as sup, c


# set up module-specific logger
logger = root.getChild(__name__)


class CustomCog(commands.Cog):
    def __init__(self, client: discord.Client, index: int, emoji: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.index = index   # for arranging cogs order in help command
        self.emoji = emoji   # likely custom emoji taken from master server
        # syntax for inline emojis: ":emoji_name:" for default emoji, "<:emoji_name:emoji_id>" for custom i.e. server-specific emoji
        self.logger = logger.getChild(self.__class__.__name__)

    @staticmethod
    async def notify(interaction: discord.Interaction):
        await interaction.response.send_message(content=sup(f"command processing, please wait a few seconds {c('(╯°□°)╯︵ ┻━┻')}", state=PENDING))

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # avoid full evaluation & if else
        # but still looks pathetic anw
        # children functions take up exactly 1 argument
        def _CheckFailure(interaction: discord.Interaction) -> str:
            return sup("an unknown exception occurred")
        def _Unauthorized(interaction: discord.Interaction) -> str:
            return sup("You don't have the right O you don't have the right")
        def _MissingPermissions(interaction: discord.Interaction) -> str:
            return sup(f"user {c(interaction.user.name)} does not have proper permissions")
        def _BotMissingPermissions(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} does not have proper permissions")
        def _CommandOnCooldown(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is on cooldown")
        def _VoiceClientNotFound(interaction: discord.Interaction) -> str:
            return sup(f"user {c(interaction.user.name)} is not in a voice channel")
        def _BotVoiceClientNotFound(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is not in a voice channel")
        def _BotVoiceClientAlreadyConnected(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is already connected to voice channel {c(self.get_bot_voice_client(interaction).channel.name)}")
        def _BotVoiceClientAlreadyPaused(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is already paused in voice channel {c(self.get_bot_voice_client(interaction).channel.name)}")
        def _BotVoiceClientAlreadyPlaying(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is already playing in voice channel {c(self.get_bot_voice_client(interaction).channel.name)}")
        def _BotVoiceClientIsolation(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} is in {c('isolation')}")
        def _BotVoiceClientQueueEmpty(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)}'s queue is empty")
        def _KeywordNotFound(interaction: discord.Interaction) -> str:
            return sup(f"bot {c(interaction.client.user.name)} could not find video matching provided keyword")
        
        self.logger.error(f"exception {error.__class__.__name__} raised from command /{interaction.command.name} by {interaction.user.name} (uid: {interaction.user.id}) (id: {interaction.id})")
        
        # massive warning right here, exceptions can be unhandled sometimes
        key = f"_{error.__class__.__name__}"
        if key not in locals():
            msg = sup(f"an unknown exception occurred: {c(error.__class__.__name__)}")
        msg = locals()[key](interaction)
        resp = await interaction.original_response()
        if resp is None:
            await interaction.response.send_message(content=msg)
            return
        await interaction.edit_original_response(content=msg)

    
class CustomGroupCog(commands.GroupCog):
    def __init__(self, client: discord.Client, index: int, emoji: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.index = index
        self.emoji = emoji
        self.logger = logger.getChild(self.__class__.__name__)


from .audio import AudioCog
from .fun import FunCog
from .misc import MiscCog
from .utils import DecodeCog, EncodeCog, UtilityCog


async def setup(client: discord.Client):   # register as ext
    cogs = {AudioCog, DecodeCog, EncodeCog, FunCog, MiscCog, UtilityCog}
    for cog in cogs:
        await client.add_cog(cog(client))
    client.logger.info(f"set up {len(cogs)} cogs: {', '.join([cog.__name__ for cog in cogs])}")
    # warning: logger name is app.client.cogs instead of app.cogs