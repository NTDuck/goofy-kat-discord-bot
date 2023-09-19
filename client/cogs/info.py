
import discord
from discord import app_commands

from . import CustomGroupCog


class InfoCog(CustomGroupCog, name="info"):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client=client, emoji="<a:info:1153177790133325954>", **kwargs)