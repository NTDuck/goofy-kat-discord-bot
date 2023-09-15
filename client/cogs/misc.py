
import discord
from discord import app_commands

from . import CustomCog
from ..views.help import HelpView


class MiscCog(CustomCog, name="miscellaneous"):
    def __init__(self, client: discord.Client):
        super().__init__(client, index=0, emoji=":frog:")

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """check whether the bot's up and running."""
        await interaction.response.send_message("pong!")

    @app_commands.command()
    async def help(self, interaction: discord.Interaction):
        """see the full list of available commands."""
        view = HelpView(interaction=interaction)
        await interaction.response.send_message(view=view, embed=view.embed)