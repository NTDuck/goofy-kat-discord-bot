
from typing import Iterable

import discord
from discord.ext import commands

class HelpSelectMenu(discord.ui.Select["HelpView"]):
    """required: call method `set_options()` after instantiation with proper `interaction` param."""
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(placeholder="hey!", **kwargs)
        self.client = client
        self.options = self.set_options()

    def set_options(self) -> Iterable[discord.SelectOption]:
        return [discord.SelectOption(label=cog.qualified_name.capitalize(), value=name, description=cog.description) for name, cog in self.client.cogs_ordered.items()]

    async def callback(self, interaction: discord.Interaction):
        view: HelpView = self.view
        view.interaction = interaction
        view.embed.cog = interaction.client.get_cog(self.values[0])   # `self.values` has a `len` of 1
        view.edit_embed()
        await interaction.response.edit_message(embed=view.embed)
        

class HelpEmbed(discord.Embed):
    def __init__(self, cog: commands.Cog, **kwargs):
        super().__init__(**kwargs)
        self.cog = cog
        self.colour = discord.Colour.gold()
        self.img_path = "https://i.imgur.com/R2UdNJP.png"

        self.set_author(name="izanami", icon_url=self.img_path)   # local image not working: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-use-a-local-image-file-for-an-embed-image
        self.set_fields()

    def set_fields(self):
        fields = [f"{self.cog.emoji} **{self.cog.qualified_name.capitalize()}:**"]
        fields.extend([f":black_small_square:**/{command.name}**: {command.description}" for command in self.cog.walk_app_commands()])   # bot only use app commands
        for field in fields:
            self.add_field(name="", value=field, inline=False)


class HelpView(discord.ui.View):
    children: Iterable[HelpSelectMenu]
    def __init__(self, interaction: discord.Interaction, **kwargs):
        super().__init__(**kwargs)
        self.interaction = interaction
        self.timeout = 60
        self.embed = HelpEmbed(cog=list(self.interaction.client.cogs_ordered.values())[0])   # first value is default value, will change in future commits

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
        self.embed.clear_fields()
        self.embed.set_fields()