
from typing import Iterable
import discord

from . import EmbedMeta
from ..utils.formatting import b, field_fmt as fmt


class InfoEmbedMeta(EmbedMeta):
    dtfmt = "%Y/%m/%d %H:%M:%S"
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, fields=self.create_fields(), msg="info", **kwargs)

    def create_fields(self) -> Iterable[str]:
        pass   # fields not affected by additional interaction therefore finalized upon instantiation


class InfoEmbedGeneral(InfoEmbedMeta):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        fields = [
            fmt("name", self.client.user.name),
            fmt("description", self.client.description),
            fmt("id", self.client.application_id),
            fmt("uid", self.client.user.id),
            fmt("command prefix", self.client.command_prefix),
            fmt("invite url", self.client.application.custom_install_url),
        ]
        return fields    


class InfoEmbedStatus(InfoEmbedMeta):
    def __init__(self, client: discord.Client, *kwargs):
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        fields = [
            fmt("status", "up and running"),
            fmt("joined (utc)", self.client.user.created_at.strftime(self.dtfmt)),
            fmt("guilds connected", len(self.client.guilds)),
            fmt("messages sent", "a lot really"),
            # fmt("intents", "?"),
            fmt("is_public", "yep, bot can be invited by anyone" if self.client.application.bot_public else "nein, bot is locked to owner"),
            fmt("require_code_grant", "yes, bot requires full oauth2 code grant flow to join" if self.client.application.bot_require_code_grant else "not at all"),
            fmt("websocket latency", self.client.latency),
            fmt("verification", " nah"),
            fmt("k/d/a", "0/17/5"),
        ]
        return fields
    

class InfoEmbedMisc(InfoEmbedMeta):   # policies, tos, data collection, etc.
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        fields = [
            fmt("policies", self.client.application.privacy_policy_url),
            fmt("tos", self.client.application.terms_of_service_url),
        ]
        return fields
    

class InfoEmbedOwner(InfoEmbedMeta):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        owner = self.client.application.owner
        fields = [
            fmt("username", owner.name),
            fmt("uid", owner.id),
            fmt("joined (utc)", owner.created_at.strftime(self.dtfmt)),
            f"wanna know more? there's a {b('special place')} for it.",
        ]
        return fields
    

class InfoEmbedEmojis(InfoEmbedMeta):
    def __init__(self, interaction: discord.Interaction, **kwargs):
        self.interaction = interaction
        super().__init__(interaction.client, **kwargs)

    def create_fields(self) -> Iterable[str]:
        fields = [fmt(f"<:{emoji.name}:{emoji.id}>", f"{emoji.name} ({emoji.id})") for emoji in self.interaction.guild.emojis]
        return fields