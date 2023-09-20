
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
    """
    \nemoji inline/string repr: `:name:` (default), `<:name:id:>` (custom), `<a:name:id>` (animated custom)
    \nemoji ids could be retrieved using something like this:
    ```
    @app_commands.command()
    async def retrieve_emoji(self, interaction: discord.Interaction):
        await interaction.response.send_message(", ".join([f"{emoji.name}: {emoji.id}" for emoji in interaction.guild.emojis]))
    ```
    """
    def __init__(self, client: discord.Client, emoji: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.emoji = emoji
        self.logger = logger.getChild(self.__class__.__name__)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # avoid full evaluation & if else
        # but still looks pathetic anw
        # children functions take up exactly 1 argument
        def _CheckFailure(interaction: discord.Interaction) -> str:   # default
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
        msg = locals().get(key, _CheckFailure)(interaction)
        resp = await interaction.original_response()
        try:   # will change in future commits
            if resp is None:
                await interaction.response.send_message(msg)
                return
            await interaction.edit_original_response(msg)
        except:
            await interaction.followup.send(msg)

    
class CustomGroupCog(commands.GroupCog):
    def __init__(self, client: discord.Client, emoji: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.emoji = emoji
        self.logger = logger.getChild(self.__class__.__name__)


from .audio import AudioCog
from .essentials import MediaCog, CasualGamesCog
from .misc import MiscCog, InfoCog
from .utils import DecodeCog, EncodeCog, ExecCog, UtilityCog


async def setup(client: discord.Client):   # register as ext
    cogs = (MiscCog, InfoCog, MediaCog, CasualGamesCog, AudioCog, EncodeCog, DecodeCog, ExecCog, UtilityCog)
    for ind, cog in enumerate(cogs):
        cog.index = ind   # for help command
        await client.add_cog(cog(client))
    client.logger.info(f"set up {len(cogs)} cogs: {', '.join([cog.__name__ for cog in cogs])}")
    # warning: logger name is app.client.cogs instead of app.cogs