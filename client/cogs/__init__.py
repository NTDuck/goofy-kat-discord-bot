
from typing import Sequence
import logging

from discord import app_commands
from discord.ext import commands
import discord

from ..const.command import PENDING
from ..utils.formatter import status_update_prefix as sup


# set up module-specific logger
logger = logging.getLogger("cogs")


class CustomCog(commands.Cog):
    def __init__(self, client: discord.Client) -> None:
        super().__init__()
        self.client = client

    @staticmethod
    async def notify(interaction: discord.Interaction):
        await interaction.response.send_message(content=sup("command processing, please wait a few seconds `(╯°□°)╯︵ ┻━┻`", state=PENDING))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # decoy check - exists solely for logging purposes
        logger.debug(f"command /{interaction.command.name} invoked by {interaction.user.name} (uid: {interaction.user.id})")
        return True

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # avoid full evaluation & if else
        # but still looks pathetic anw
        # children functions take up exactly 1 argument
        def _CheckFailure(interaction: discord.Interaction) -> str:
            return sup("an unknown exception occurred")
        def _Unauthorized(interaction: discord.Interaction) -> str:
            return sup("You don't have the right O you don't have the right")
        def _MissingPermissions(interaction: discord.Interaction) -> str:
            return sup(f"user `{interaction.user.name}` does not have proper permissions")
        def _BotMissingPermissions(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` does not have proper permissions")
        def _CommandOnCooldown(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is on cooldown")
        def _VoiceClientNotFound(interaction: discord.Interaction) -> str:
            return sup(f"user `{interaction.user.name}` is not in a voice channel")
        def _BotVoiceClientNotFound(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is not in a voice channel")
        def _BotVoiceClientAlreadyConnected(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is already connected to voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientAlreadyPaused(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is already paused in voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientAlreadyPlaying(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is already playing in voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientIsolation(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` is in `isolation`")
        def _BotVoiceClientQueueEmpty(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}`'s queue is empty")
        def _KeywordNotFound(interaction: discord.Interaction) -> str:
            return sup(f"bot `{interaction.client.user.name}` could not find video matching provided keyword")
        
        logger.error(f"exception {error.__class__.__name__} raised from command /{interaction.command.name} by {interaction.user.name} (uid: {interaction.user.id}) (id: {interaction.id})")
        
        key = f"_{error.__class__.__name__}"
        if key not in locals():
            msg = sup(f"an unknown exception occurred: `{error.__class__.__name__}`")
        msg = locals()[key](interaction)
        resp = await interaction.original_response()
        if resp is None:
            await interaction.response.send_message(content=msg)
            return
        await interaction.edit_original_response(content=msg)

    
class CustomGroupCog(commands.GroupCog):
    def __init__(self, client: discord.Client) -> None:
        super().__init__()
        self.client = client

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # decoy check - exists solely for logging purposes
        logger.debug(f"command /{interaction.command.parent.name} {interaction.command.name} invoked by {interaction.user.name} (uid: {interaction.user.id})")
        return True


from .audio import AudioCog
from .fun import FunCog
from .misc import MiscCog
from .utils import DecodeCog, EncodeCog, UtilityCog


async def setup(client: discord.Client):   # register as ext
    cogs = {AudioCog, DecodeCog, EncodeCog, FunCog, MiscCog, UtilityCog}
    for cog in cogs:
        await client.add_cog(cog(client))
    logger.info(f"set up {len(cogs)} cogs")