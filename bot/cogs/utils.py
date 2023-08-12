
# not to be confused with utils/
import asyncio
from discord import app_commands, Client, Interaction

from . import CustomCog
from ..const.command import SUCCESS
from ..utils.formatter import status_update_prefix as sup


class UtilityCog(CustomCog):
    def __init__(self, client: Client):
        self.client = client

    # should require near-administrative privileges
    @app_commands.command(description="clear messages within the current text channel.")
    @app_commands.describe(number="the number of messages to delete.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def cls(self, interaction: Interaction, number: app_commands.Range[int, 1, 100]):
        await self.notify(interaction)
        
        resp = await interaction.original_response()
        limit = number + 1
        
        await interaction.channel.purge(limit=limit, check=lambda m: m.id != resp.id, bulk=True)

        await interaction.edit_original_response(content=sup(f"deleted up to `{number}` messages in channel `{interaction.channel.name}`", state=SUCCESS))
        await asyncio.sleep(2)
        await interaction.delete_original_response()