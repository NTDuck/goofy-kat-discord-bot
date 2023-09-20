
import asyncio
from typing import Callable

import discord
from discord import app_commands

from . import CustomCog
from ..const.audio import PAUSED, PLAYING
from ..const.command import SUCCESS
from ..errors import *
from ..utils.audio import siget, siset, qiclear, qiappend, qipop, qigetone, qiindexall, qiindexone, qilen, name
from ..utils.fetch import fetch_ytb_audio_info
from ..utils.formatting import status_update_prefix as sup, b, c, url


class AudioCog(CustomCog, name="audio"):
    """a music player typically seen in discord bots. warning: prone to bugs."""
    tableflip = "(╯°□°)╯︵ ┻━┻"
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<:audio_wave:1153626821548593202>", **kwargs)
        self.qlim: int = client.config["MAX_AUDIO_QUEUE_LIMIT"]

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(connect=True)
    async def join(self, interaction: discord.Interaction):
        """joins a voice/stage channel."""
        await interaction.response.defer()

        voice_state = interaction.user.voice
        if voice_state is None:
            raise VoiceClientNotFound
        
        voice_client = interaction.client.get_bot_voice_client(interaction)
        if voice_client is not None:
            raise BotVoiceClientAlreadyConnected

        # empty queue upon join
        await qiclear(interaction)

        await interaction.user.voice.channel.connect()
        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} connected to voice channel {c(interaction.user.voice.channel.name)}", state=SUCCESS))

    @app_commands.command()
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def leave(self, interaction: discord.Interaction):
        """leaves the current voice/stage channel."""
        await interaction.response.defer()

        # empty queue upon leave
        await qiclear(interaction)
        
        voice_client = interaction.client.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
                
        await voice_client.disconnect()
        # ctx.voice_client.cleanup()
        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} disconnected from voice channel {c(voice_client.channel.name)}", state=SUCCESS))

    async def play_next(self, interaction: discord.Interaction, after_func: Callable):
        state = await siget(interaction)
        _len = await qilen(interaction)

        if state == PLAYING:
            await qipop(interaction)   # pop
        if _len < 1:   # check if queue is empty
            await interaction.channel.send(content=f"queue exhausted. bot {c(interaction.client.user.name)} stopped playing.")
            await qiclear(interaction)
            return
        
        src_url, name, webpage_url = await qiindexall(interaction, index=0)   # retrieve first element
        src = discord.FFmpegPCMAudio(src_url, options="-vn")
        interaction.client.get_bot_voice_client(interaction).play(discord.PCMVolumeTransformer(src), after=after_func)
        if state == PAUSED:
            await siset(interaction, PLAYING)
        await interaction.channel.send(sup(f"bot {c(interaction.client.user.name)} is playing {name} {url(c(self.tableflip), webpage_url)}", state=SUCCESS))

    @app_commands.command()
    @app_commands.describe(keyword="simply what you would type into YouTube's search bar.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, keyword: app_commands.Range[str, 1, None]):
        """adds an audio to the current queue."""
        def after(error=None):
            if error:
                self.logger.error(error)
                return
            coro = self.play_next(interaction, after_func=after)
            future = asyncio.run_coroutine_threadsafe(coro, interaction.client.loop)
            future.result()   # must be called to get result from future
        
        await interaction.response.defer()

        if interaction.client.get_bot_voice_client(interaction) is None:
            raise VoiceClientNotFound
        
        state = await siget(interaction)
        _len = await qilen(interaction)
        if _len > self.qlim:   # will need to look back on this
            await interaction.followup.send(sup(f"failed to add new audio - queue limit exceeded"))
            return
        
        vid_info = fetch_ytb_audio_info(config=interaction.client.config, keyword=keyword)
        if not vid_info["entries"]:
            raise KeywordNotFound
                
        res = vid_info["entries"][0]   # fetch first url from search query
        vid_url = res["url"]
        vid_name = res["title"]
        vid_webpage_url = res["webpage_url"]

        await qiappend(interaction, (vid_url, vid_name, vid_webpage_url))

        await interaction.followup.send(sup(f"bot {interaction.client.user.name} added {b(vid_name)} to queue", state=SUCCESS))

        if state == PAUSED:
            await self.play_next(interaction, after_func=after)

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def pause(self, interaction: discord.Interaction):
        """pauses the current queue."""
        await interaction.response.defer()
        
        state = await siget(interaction)
        _len = await qilen(interaction)
        voice_client = interaction.client.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        if _len <= 0:
            raise BotVoiceClientQueueEmpty
        if state == PAUSED:
            raise BotVoiceClientAlreadyPaused
        
        voice_client.pause()
        await siset(interaction, PAUSED)

        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} paused in voice channel {c(voice_client.channel.name)}", state=SUCCESS))

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def resume(self, interaction: discord.Interaction):
        """resumes the current queue."""
        await interaction.response.defer()

        state = await siget(interaction)
        _len = await qilen(interaction)
        voice_client = interaction.client.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        if _len <= 0:
            raise BotVoiceClientQueueEmpty
        if state == PLAYING:
            raise BotVoiceClientAlreadyPlaying
        
        voice_client.resume()
        await siset(interaction, PLAYING)

        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} resumed in voice channel {c(voice_client.channel.name)}", state=SUCCESS))

    @app_commands.command()
    @app_commands.describe(value="new volume value to set.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def volume(self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]):
        """change the volume. works separately with the interactable slider."""
        await interaction.response.defer()

        if interaction.client.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        interaction.client.get_bot_voice_client(interaction).source.volume = value / 100
        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)}'s volume changed to {c(value.__str__() + '%')}", state=SUCCESS))

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        """view all audios in the current queue."""
        await interaction.response.defer()

        if interaction.client.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound
        
        nameq = await qigetone(interaction, name)
        if not nameq:
            raise BotVoiceClientQueueEmpty
        
        qrepr = [f"currently playing: {b(nameq[0])}"]
        if len(nameq) > 0:
            qrepr.extend([f"{ind}. {_name}" for ind, _name in enumerate(nameq[1:])])
        await interaction.followup.send(f"\n".join(qrepr))

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def skip(self, interaction: discord.Interaction):
        """skips to next audio in the queue."""
        await interaction.response.defer()
    
        if interaction.client.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        first = await qiindexone(interaction, name, 0)
        if not first:   # first only exists if queue does
            raise BotVoiceClientQueueEmpty
        
        interaction.client.get_bot_voice_client(interaction).stop()
        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)} skipped {b(first)}", state=SUCCESS))

    @app_commands.command()
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def clear(self, interaction: discord.Interaction):
        """empties the current queue."""
        await interaction.response.defer()

        if interaction.client.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound
        
        await qiclear(interaction)
        interaction.client.get_bot_voice_client(interaction).stop()
        await interaction.followup.send(sup(f"bot {c(interaction.client.user.name)}'s queue is cleared", state=SUCCESS))


"""
warning: personal use only. this violates YouTube's ToS.
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""