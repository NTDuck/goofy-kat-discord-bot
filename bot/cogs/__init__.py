
from discord import app_commands, Client, Interaction
from discord.ext.commands import Cog

from ..utils.formatter import status_update_prefix as sup


class CustomCog(Cog):
    def __init__(self, client: Client) -> None:
        super().__init__()
        self.client = client

    @staticmethod
    async def notify(interaction: Interaction):
        await interaction.response.send_message("command processing, please wait a few seconds `(╯°□°)╯︵ ┻━┻`")

    async def cog_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        # avoid full evaluation & if else
        # but still looks pathetic anw
        # children functions takes up exactly 1 argument
        def _MissingPermissions(interaction: Interaction):
            return sup(f"user `{interaction.user.name}` does not have proper permissions")
        def _BotMissingPermissions(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` does not have proper permissions")
        def _CommandOnCooldown(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` is on cooldown")
        def _VoiceClientNotFound(interaction: Interaction):
            return sup(f"user `{interaction.user.name}` is not in a voice channel")
        def _BotVoiceClientNotFound(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` is not in a voice channel")
        def _BotVoiceClientAlreadyConnected(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` is already connected to voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientAlreadyPaused(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` is already paused in voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientAlreadyPlaying(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` is already playing in voice channel `{self.get_bot_voice_client(interaction).channel.name}`")
        def _BotVoiceClientQueueEmpty(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}`'s queue is empty")
        def _KeywordNotFound(interaction: Interaction):
            return sup(f"bot `{interaction.client.user.name}` could not find video matching provided keyword")
        
        msg = locals()[f"_{error.__class__.__name__}"](interaction)
        resp = await interaction.original_response()
        if resp is None:
            await interaction.response.send_message(content=msg)
            return
        await interaction.edit_original_response(content=msg)


from .audio import AudioCog
from .fun import FunCog
from .misc import MiscCog
from .utils import UtilityCog


async def setup(client):   # register as ext
    cogs = {AudioCog, FunCog, MiscCog, UtilityCog}
    for cog in cogs:
        await client.add_cog(cog(client))