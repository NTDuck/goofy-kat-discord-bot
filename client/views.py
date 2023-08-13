
from typing import Union
import discord


class MikuView(discord.ui.View):
    def __init__(self, *, timeout: Union[float, None] = 180):
        super().__init__(timeout=timeout)
        self.value: Union[bool, None] = None

    @discord.ui.button(label="yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction):
        ...