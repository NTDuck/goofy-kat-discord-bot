
import discord
from discord import app_commands

from . import CustomCog


class MiscCog(CustomCog):
    def __init__(self, client: discord.Client):
        super().__init__(client)

    @app_commands.command(description="check whether the bot's up and running.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong!")

    # @app_commands.command(description="see the list of available commands.")
    # async def help(self, interaction: Interaction):
    #     view = ui.View()