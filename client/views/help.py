
from typing import Iterable, List, Union
import random

import discord
from discord import app_commands
from discord.ext import commands

from . import EmbedMeta
from ..utils.formatting import b, c, i
from ..utils.fetch import local_asset


async def help_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # retrieve all app commands
    choices = interaction.client.app_commands_mapping.keys()
    return [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice]


class HelpEmbedMeta(EmbedMeta):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, msg="help", **kwargs)
        self.set_fields(self.create_fields())

    def create_fields(self) -> Iterable[str]:
        """remember to manually change the value of property `__fields__`. dev is too lazy to bother using `@property`."""
        pass   # defined by children classes
    
    def edit(self):
        self.clear_fields()
        self.set_fields(self.create_fields())


class HelpEmbedPerCog(HelpEmbedMeta):
    def __init__(self, cog: commands.Cog, client: discord.Client, **kwargs):
        self.cog = cog
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        fields = [f"{self.cog.emoji} {b(self.cog.qualified_name.lower())}: {self.cog.description}"]
        groupname = self.cog.app_command.qualified_name + " " if self.cog.app_command is not None else ""
        fields.extend([f"{self.transparent}{b('/' + groupname + command.name)}: {command.description}" for command in self.cog.walk_app_commands()])   # app commands first
        return fields


class HelpEmbedPerCommand(HelpEmbedMeta):
    def __init__(self, command: app_commands.Command, client: discord.Client, **kwargs):
        self.command = command   # must be placed at this exact position else embed fails
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        name = f"/{self.command.parent.name + ' ' if self.command.parent is not None else ''}{self.command.name}"
        fields = [f"{b(name)}: {self.command.description}"]
        fields.extend([f"{self.transparent}{c(param.name)}{' ' + i('(required)') if param.required else ''}: {param.description}" for param in self.command.parameters])
        return fields
    

class HelpEmbedPlaceholder(HelpEmbedMeta):
    """uses local image for author icon, therefore requires sending image as a `discord.File("path-to-image.png")` before manually calling `set_author()` (after instantiation)"""
    img_name = "konatarayeal.jpg"
    img_path = local_asset("images", "banners", filename=img_name)
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, **kwargs)
        self.file = discord.File(self.img_path, filename=self.img_name)
        self.description = f"welcum to {self.client.user.name.lower()}!"
        self.set_image()

    def create_fields(self) -> Iterable[str]:
        return [f"check out our signature {b('/cat')}!"]
    
    def set_image(self):
        return super().set_image(url="attachment://" + self.img_name)


class HelpButtonMeta(discord.ui.Button):
    def __init__(self, **kwargs):
        super().__init__(row=4, **kwargs)   # placed last

    async def callback(self, interaction: discord.Interaction):
        view: discord.ui.View
        view.interaction = interaction


class HelpButtonInvite(HelpButtonMeta):
    def __init__(self, **kwargs):
        super().__init__(style=discord.ButtonStyle.link, label="add me to ur server!", url="https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=42870253809600&scope=applications.commands%20bot", **kwargs)


class HelpButtonVote(HelpButtonMeta):
    def __init__(self, **kwargs):
        super().__init__(style=discord.ButtonStyle.link, label="vote 4 me pls", url="https://youtu.be/dQw4w9WgXcQ", **kwargs)   # yeah that's rickroll


class HelpSelectMenu(discord.ui.Select["HelpViewPerCog"]):
    """required: call method `set_options()` after instantiation with proper `interaction` param."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.placeholder = "select something, it'll be worth ur time i promise!"
        self.options = self.set_options()

    def set_options(self) -> Iterable[discord.SelectOption]:
        return [discord.SelectOption(label=name, value=name) for name in self.client.cogs_ordered_mapping.keys()]
    
    def set_placeholder(self, interaction_count: int):
        """an unnecessary method to reset `placeholder` per `interaction`. should better be randomized."""
        max_choice = len(self.options)
        if not interaction_count > max_choice:
            mythical = ["ambatukam", "burenyuu", "hello every nyan", "i am emu otori!", "wonderhoy!", "i wish i were a bird", "open na noor", "i am the one who knocks"]
            placeholder = random.choice(mythical)
        else:
            reyeal = ["consider taking a break?", "umm, please stop...", "no easter egg here!", "you ain't done yet?", "be aware of the 1-minute mark..."]
            placeholder = random.choice(reyeal)
        self.placeholder = placeholder

    async def callback(self, interaction: discord.Interaction):
        view: HelpViewPerCog = self.view
        view.interaction = interaction
        cog: commands.Cog = interaction.client.get_cog(self.values[0])   # `self.values` has a `len` of 1
        if not view.interaction_count:   # not 0 == True. well...
            view.embed = HelpEmbedPerCog(cog=cog, client=interaction.client)
        else:
            view.embed.cog = cog
            view.embed.edit()
        view.interaction_count += 1
        self.set_placeholder(interaction_count=view.interaction_count)
        await interaction.response.edit_message(embed=view.embed, view=view, attachments=[])   # file should immediately be removed after first selectmenu interaction


class HelpViewMeta(discord.ui.View):
    children: Iterable[discord.ui.Item]
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.interaction = interaction

        items = [HelpButtonInvite(), HelpButtonVote()]
        for item in items:
            self.add_item(item)

    def disable_items(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self):
        """update last interaction for on_timeout children disabling"""
        self.disable_items()
        self.stop()
        await self.interaction.edit_original_response(view=self)   # could add a timeout embed


class HelpViewPerCog(HelpViewMeta):
    children: Iterable[Union[HelpSelectMenu, HelpButtonMeta]]
    def __init__(self, interaction: discord.Interaction):
        super().__init__(interaction)
        self.interaction_count = 0
        self.embed = HelpEmbedPlaceholder(self.interaction.client)

        item = HelpSelectMenu(self.interaction.client)
        self.add_item(item)

    def disable_items(self):
        for item in self.children:
            item.disabled = True
            if item.type != discord.ComponentType.select:
                continue
            item.placeholder = "time's out, please go away"


class HelpViewPerCommand(HelpViewMeta):
    children: Iterable[HelpButtonMeta]
    def __init__(self, interaction: discord.Interaction, command: Union[app_commands.Command, commands.Command]):
        super().__init__(interaction)
        self.embed = HelpEmbedPerCommand(command, interaction.client)