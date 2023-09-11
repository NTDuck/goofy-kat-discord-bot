
from typing import Iterable, Optional
import logging

import discord
from . import logger


# abc
class ChoiceButton(discord.ui.Button["ChoiceView"]):
    def __init__(self, value: int, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        view: ChoiceView = self.view
        view.value = self.value
        await view.on_timeout()
        await interaction.response.edit_message(view=view)
        
        view.logger.debug(f"button {self.label} invoked by {interaction.user.name} (uid: {interaction.user.id})")

class ChoiceView(discord.ui.View):
    children: Iterable[ChoiceButton]
    def __init__(self, _children: Iterable[ChoiceButton], interaction: discord.Interaction, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.value = None
        self.logger = logger.getChild({self.__class__.__name__})
        for item in _children:
            self.add_item(item)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        self.stop()
        await self.interaction.edit_original_response(view=self)


# practical uses
class MikuView(ChoiceView):
    NO = 0
    YES = 1
    def __init__(self, interaction: discord.Interaction, timeout: float | None = 180):
        _children = [
            ChoiceButton(value=0, style=discord.ButtonStyle.danger, label="no"),
            ChoiceButton(value=1, style=discord.ButtonStyle.success, label="yes"),
        ]
        super().__init__(_children=_children, interaction=interaction, timeout=timeout)