
from typing import Optional

import discord
from discord import app_commands

from . import CustomCog
from ..views.help import HelpViewPerCog, HelpEmbedPerCommand, help_autocomplete
from ..utils.formatting import b, status_update_prefix as sup


class MiscCog(CustomCog, name="miscellaneous"):
    def __init__(self, client: discord.Client):
        super().__init__(client, emoji="<a:find:1153184607903162369>")

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """check whether the bot's up and running."""
        await interaction.response.send_message("pong!")

    @app_commands.command()
    @app_commands.describe(command="show a specific command in even greater detail!")
    @app_commands.autocomplete(command=help_autocomplete)
    async def help(self, interaction: discord.Interaction, command: Optional[str]):
        """see the full list of available commands."""
        if not command:
            view = HelpViewPerCog(interaction=interaction)
            await interaction.response.send_message(view=view, file=view.embed.file, embed=view.embed)
            return
        _command = interaction.client.app_commands_mapping.get(command)
        if _command is None:
            await interaction.response.send_message(content=sup(f"command {b(command)} does not exist. try our provided options"))
            return
        embed = HelpEmbedPerCommand(command=_command, client=interaction.client)
        await interaction.response.send_message(embed=embed)