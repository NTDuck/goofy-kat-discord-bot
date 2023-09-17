
from typing import Iterable, List
import random

import discord
from discord import app_commands
from discord.ext import commands

from ..utils.formatting import b, c, i
from ..utils.fetch import local_asset


async def help_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # retrieve all app commands
    choices = interaction.client.app_commands_mapping.keys()
    return [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice]


class HelpEmbedMeta(discord.Embed):
    transparent = "<:transparent:1152925713704439890>"
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.colour = discord.Colour.gold()
        self.set_author()

        self.__fields__ = self.create_fields()
        self.set_fields()

    def create_fields(self) -> List[str]:
        """remember to manually change the value of property `__fields__`. dev is too lazy to bother using `@property`."""
        pass   # defined by children classes

    def set_fields(self):
        """to register changes, call method `create_fields()` immediately prior."""
        for field in self.__fields__:
            self.add_field(name="", value=field, inline=False)

    def set_author(self):
        return super().set_author(name=self.client.user.name.lower() + "-help!", icon_url=self.client.user.avatar.url)   # assume that the hyphen is used as a separator. a more generic approach could be implemented instead however dev is too unmotivated
        

class HelpEmbedPerCog(HelpEmbedMeta):
    def __init__(self, cog: commands.Cog, client: discord.Client, **kwargs):
        self.cog = cog
        super().__init__(client=client, **kwargs)

    def create_fields(self) -> List[str]:
        fields = [f"{self.cog.emoji} {b(self.cog.qualified_name.capitalize())}:"]
        fields.extend([f"{self.transparent}{b('/' + command.name)}: {command.description}" for command in self.cog.walk_app_commands()])   # bot only use app commands
        return fields


class HelpEmbedPerCommand(HelpEmbedMeta):
    def __init__(self, command: app_commands.Command, client: discord.Client, **kwargs):
        self.command = command
        super().__init__(client=client, **kwargs)

    def create_fields(self) -> List[str]:
        name = f"/{self.command.parent.name + ' ' if self.command.parent is not None else ''}{self.command.name}"
        fields = [f"{b(name)}: {self.command.description}"]
        for param in self.command.parameters:
            fields.extend([f"{self.transparent}{c(param.name)}{' ' + i('(required)') if param.required else ''}: {param.description}"])
        return fields
    

class HelpEmbedPlaceholder(HelpEmbedMeta):
    """uses local image for author icon, therefore requires sending image as a `discord.File("path-to-image.png")` before manually calling `set_author()` (after instantiation)"""
    img_name = "anakin.png"
    img_path = local_asset("images", filename=img_name)
    def __init__(self, client: discord.Client, **kwargs):
        self.file = discord.File(self.img_path, filename=self.img_name)
        self.description = f"welcum to {client.user.name.lower()}!"
        self.set_image()
        super().__init__(client=client, **kwargs)

    def create_fields(self) -> List[str]:
        return [f"check out our signature {b('/cat')}!"]
    
    def set_image(self):
        return super().set_image(url="attachment://" + self.img_name)


class HelpSelectMenu(discord.ui.Select["HelpViewPerCog"]):
    """required: call method `set_options()` after instantiation with proper `interaction` param."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.placeholder = "select something, it'll be worth ur time i promise!"
        self.options = self.set_options()

    def set_options(self) -> Iterable[discord.SelectOption]:
        return [discord.SelectOption(label=cog.qualified_name.capitalize(), value=name, description=cog.description) for name, cog in self.client.cogs_ordered_mapping.items()]
    
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
            view.edit_embed()
        view.interaction_count += 1
        self.set_placeholder(interaction_count=view.interaction_count)
        await interaction.response.edit_message(embed=view.embed, view=view, attachments=[])   # file should immediately be removed after first selectmenu interaction


class HelpViewPerCog(discord.ui.View):
    children: Iterable[HelpSelectMenu]
    def __init__(self, interaction: discord.Interaction, **kwargs):
        super().__init__(**kwargs)
        self.interaction = interaction
        self.timeout = 60
        self.embed = HelpEmbedPlaceholder(client=interaction.client)
        self.interaction_count = 0

        item = HelpSelectMenu(client=self.interaction.client)
        self.add_item(item)

    async def on_timeout(self) -> None:
        """update last interaction for on_timeout children disabling"""
        for item in self.children:
            item.disabled = True
        self.stop()
        await self.interaction.edit_original_response(view=self)   # could add a timeout embed
            
    def edit_embed(self):
        """modify `self.embed`"""
        embed = self.embed
        embed.clear_fields()
        embed.__fields__ = embed.create_fields()
        embed.set_fields()