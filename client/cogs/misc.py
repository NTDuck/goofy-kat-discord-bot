
from typing import Optional

import discord
from discord import app_commands

from . import CustomCog, CustomGroupCog
from ..views.help import HelpViewPerCog, HelpViewPerCommand, help_autocomplete
from ..utils.formatting import b, status_update_prefix as sup


class MiscCog(CustomCog, name="miscellaneous"):
    """you need help with the commands, you come here."""
    def __init__(self, client: discord.Client):
        super().__init__(client, emoji="<:question:1153688209688113192>")

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """check whether the bot's up and running."""
        await interaction.response.send_message("pong!")

    @app_commands.command()
    @app_commands.describe(command="show a specific command in even greater detail!")
    @app_commands.autocomplete(command=help_autocomplete)
    async def help(self, interaction: discord.Interaction, command: Optional[str]):
        """see the full list of available commands."""
        await interaction.response.defer()   # last resort - process takes up too much time
        if not command:
            view = HelpViewPerCog(interaction=interaction)
            await interaction.followup.send(file=view.embed.file, embed=view.embed, view=view)
            return
        _command = interaction.client.app_commands_mapping.get(command)
        if _command is None:
            await interaction.followup.send(sup(f"command {b(command)} does not exist. try our provided options"))
            return
        view = HelpViewPerCommand(interaction, command=_command)
        await interaction.followup.send(embed=view.embed, view=view)


class InfoCog(CustomGroupCog, name="info"):
    """everything you'll ever need to know about us."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client=client, emoji="<:info:1153628812395950091>", **kwargs)
    
    @app_commands.command()
    async def forbidden(self, interaction: discord.Interaction):
        """just don't."""
        bleh = """
🟥🟥🟥🟥🟥🟥🟥🟥🟥
🟥⬜⬜⬜⬜⬜⬜⬜🟥
🟥⬜⬛⬜⬛⬛⬛⬜🟥
🟥⬜⬛⬜⬛⬜⬜⬜🟥
🟥⬜⬛⬛⬛⬛⬛⬜🟥
🟥⬜⬜⬜⬛⬜⬛⬜🟥
🟥⬜⬛⬛⬛⬜⬛⬜🟥
🟥⬜⬜⬜⬜⬜⬜⬜🟥
🟥🟥🟥🟥🟥🟥🟥🟥🟥
        """
        await interaction.response.send_message(content="you asked for it.\n" + bleh)