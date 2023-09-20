
from typing import Optional

from discord import app_commands
from discord.ext import commands
import discord

from logger import logger as root
from ..errors import errorhandler

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
        return await errorhandler(interaction, error, logger=self.logger)

    
class CustomGroupCog(commands.GroupCog):
    def __init__(self, client: discord.Client, emoji: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.emoji = emoji
        self.logger = logger.getChild(self.__class__.__name__)

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        return await errorhandler(interaction, error, logger=self.logger)


from .audio import AudioCog
from .essentials import MediaCog, CasualGamesCog, EquilibriumCog
from .misc import MiscCog, InfoCog
from .utils import DecodeCog, EncodeCog, ExecCog, UtilityCog


async def setup(client: discord.Client):   # register as ext
    cogs = (MiscCog, InfoCog, MediaCog, CasualGamesCog, AudioCog, EncodeCog, DecodeCog, ExecCog, UtilityCog, EquilibriumCog)
    for ind, cog in enumerate(cogs):
        cog.index = ind   # for help command
        await client.add_cog(cog(client))
    client.logger.info(f"set up {len(cogs)} cogs: {', '.join([cog.__name__ for cog in cogs])}")
    # warning: logger name is app.client.cogs instead of app.cogs