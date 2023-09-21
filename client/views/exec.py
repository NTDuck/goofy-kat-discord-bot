
from typing import Callable
import discord


class ExecModalMeta(discord.ui.Modal):
    code = discord.ui.TextInput(
        label="insert your code here!",
        style=discord.TextStyle.paragraph,
        placeholder="print('Hello world')",
        required=True,
        max_length=100,   # is this too much?
    )
    def __init__(self, client: discord.Client, msg: str, processor: Callable[[str], str], **kwargs):
        title = f"{client.user.name.lower()}-exec-{msg}!"
        super().__init__(title=title, timeout=None, **kwargs)
        self.processor = processor

    async def on_submit(self, interaction: discord.Interaction):
        input = self.code.value
        output = self.processor(input)
        await interaction.response.send_message(output)