
from typing import Any, Callable, Coroutine, Union
import discord

from . import logger
from ..utils.formatting import c
from ..utils.exec.python import processor as py_processor


def set_textinput(label: str, placeholder: str) -> discord.ui.TextInput:
    return discord.ui.TextInput(label=label, placeholder=placeholder, style=discord.TextStyle.paragraph, required=True, max_length=2000)


class ExecModalMeta(discord.ui.Modal):
    input: discord.ui.TextInput
    def __init__(self, client: discord.Client, processor: Union[Callable[[str], str], Coroutine[str, Any, str]], msg: str, **kwargs):
        title = f"{client.user.name.lower()}-{msg}-exec!"   # msg should be lower
        super().__init__(title=title, **kwargs)
        self.processor = processor
        self.logger = logger.getChild(self.__class__.__name__)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        input = self.input.value
        print(input)
        if isinstance(self.processor, Callable):
            output = self.processor(input)
        else:   # processor is coroutine
            output = await self.processor(input)
        await interaction.followup.send(c(output))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        msg = "an unknown exception occurred."
        self.logger.error(f"exception {error.__class__.__name__} raised during the handling of modal")
        try:
            await interaction.followup.send(msg)
        except:
            await interaction.response.send_message(msg)


class ExecModalPython(ExecModalMeta):
    input = set_textinput("insert your coooode here!", 'print("Hello world")')
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, py_processor, "py", **kwargs)