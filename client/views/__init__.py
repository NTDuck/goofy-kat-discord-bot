
from typing import Iterable

import discord

from logger import logger as root
logger = root.getChild(__name__)


"""
also handles embed
"""

class EmbedMeta(discord.Embed):
    transparent = "<:transparent:1152925713704439890>"
    def __init__(self, client: discord.Client, fields: Iterable[str], msg: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.colour = discord.Colour.gold()   #f1c40f
        self.set_author(msg)
        self.set_fields(fields)

    def set_author(self, msg: str):
        return super().set_author(
            name=f"{self.client.user.name.lower()}-{msg}!",
            icon_url=self.client.user.avatar.url,
        )   # assume that the hyphen is used as a separator. a more generic approach could be implemented instead however dev is too unmotivated

    def set_fields(self, fields: Iterable[str]):
        for field in fields:
            self.add_field(name="", value=field, inline=False)