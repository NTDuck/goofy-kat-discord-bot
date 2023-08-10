
from discord import app_commands, Client, Interaction
from . import CustomCog


class MiscCog(CustomCog):
    def __init__(self, client: Client):
        self.client = client

    @app_commands.command(description="check whether the bot's up and running.")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message("pong!")