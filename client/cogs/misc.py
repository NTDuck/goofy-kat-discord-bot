
import discord
from discord import app_commands

from . import CustomCog
from ..views.help import HelpView


class MiscCog(CustomCog, name="miscellaneous"):
    def __init__(self, client: discord.Client):
        super().__init__(client, index=0, emoji=":frog:")

    @app_commands.command(description="check whether the bot's up and running.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong!")

    @app_commands.command(description="see available commands.")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(interaction=interaction)
        await interaction.response.send_message(view=view, embed=view.embed)