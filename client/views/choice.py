
from typing import Iterable, Optional, Union
import discord

from . import logger


# abc
class ChoiceButton(discord.ui.Button["ChoiceView"]):
    def __init__(self, value: int, style: Optional[discord.ButtonStyle] = discord.ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Union[str, discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, None] = None, row: Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        view: ChoiceView = self.view
        view.value = self.value
        await view.on_timeout()
        await interaction.response.edit_message(view=view)
        
        logger.debug(f"button {self.label} invoked by {interaction.user.name} (uid: {interaction.user.id})")

class ChoiceView(discord.ui.View):
    children: Iterable[ChoiceButton]
    def __init__(self, _children: Iterable[ChoiceButton], timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.value = None
        for item in _children:
            self.add_item(item)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        self.stop()


# practical uses
class MikuView(ChoiceView):
    NO = 0
    YES = 1
    def __init__(self, timeout: float | None = 180):
        _children = [
            ChoiceButton(value=0, style=discord.ButtonStyle.danger, label="no"),
            ChoiceButton(value=1, style=discord.ButtonStyle.success, label="yes"),
        ]
        super().__init__(_children=_children, timeout=timeout)