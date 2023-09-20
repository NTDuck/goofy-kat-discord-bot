
# visit /bot/cogs/__init__.py if any changes occur
import logging
from typing import Self

import discord
from discord import app_commands

from .utils.formatting import status_update_prefix as sup, c


class ChildrenCounter(type):   # for tracking children classes
    children = []
    def __new__(cls, *args) -> Self:   # name, bases, attrs (?)
        new = super().__new__(cls, *args)
        cls.children.append(new)
        return new

class AppCommandErrorMeta(app_commands.CheckFailure, metaclass=ChildrenCounter):
    def msg(self, interaction: discord.Interaction) -> str:
        pass

class Unauthorized(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return "you don't have the right o you don't have the right!"

class VoiceClientNotFound(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"user {c(interaction.user.name)} is not in a voice channel")

class BotVoiceClientNotFound(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.user.name)} is not in a voice channel")

class BotVoiceClientAlreadyConnected(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.client.user.name)} is already connected to voice channel {c(interaction.client.get_bot_voice_client(interaction).channel.name)}")

class BotVoiceClientAlreadyPaused(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.client.user.name)} is already paused in voice channel {c(interaction.client.get_bot_voice_client(interaction).channel.name)}")

class BotVoiceClientAlreadyPlaying(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.client.user.name)} is already playing in voice channel {c(interaction.client.get_bot_voice_client(interaction).channel.name)}")

class BotVoiceClientQueueEmpty(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.client.user.name)}'s queue is empty")

class KeywordNotFound(AppCommandErrorMeta):
    def msg(self, interaction: discord.Interaction) -> str:
        return sup(f"bot {c(interaction.client.user.name)} could not find a video matching provided keyword")
    
ChildrenCounter.children.remove(AppCommandErrorMeta)   # remove metaclass since never called
    
    
async def errorhandler(interaction: discord.Interaction, error: app_commands.AppCommandError, logger: logging.Logger):  
    logger.error(f"exception {error.__class__.__name__} raised from command /{interaction.command.name} by {interaction.user.name} (uid: {interaction.user.id}) (id: {interaction.id})")
    
    # warning: this implementation leaves MissingPermissions, BotMissingPermissions, CommandOnCooldown unhandled
    content = error.msg(interaction) if isinstance(error, tuple(ChildrenCounter.children)) else "an unknown exception occurred"
    resp = await interaction.original_response()

    try:   # will change in future commits
        if resp is None:
            await interaction.response.send_message(content)
            return
        await interaction.edit_original_response(content)
    except:
        await interaction.followup.send(content)


# add emoji to emotional class