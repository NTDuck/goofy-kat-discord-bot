
import asyncio
import random
from collections.abc import Mapping
from typing import Callable

import discord
from discord import app_commands

from . import CustomCog
from ..const.audio import PAUSED, PLAYING, ISOLATED
from ..const.command import SUCCESS
from ..errors import *
from ..utils.fetch import fetch_ytb_audio_info, assets
from ..utils.formatter import status_update_prefix as sup


class AudioData:   # pickle serializable
    def __init__(self, src_url: str, name: str, webpage_url: str):
        self.src_url = src_url
        self.name = name
        self.webpage_url = webpage_url


class AudioCog(CustomCog):
    def __init__(self, client: discord.Client):
        self.client = client

    async def _get(self, interaction: discord.Interaction) -> Mapping:
        return await interaction.client._get(id=interaction.guild_id)
    
    async def _post(self, interaction: discord.Interaction, value: Mapping) -> None:
        await interaction.client._post(id=interaction.guild_id, value=value)

    async def reset_queue(self, interaction: discord.Interaction) -> None:
        default_state = {
            "voice": {
                "state": PAUSED,
                "queue": [],
            }
        }
        await self._post(interaction, default_state)

    def get_bot_voice_client(self, interaction: discord.Interaction) -> discord.VoiceClient:
        return interaction.client.get_guild(interaction.guild_id).voice_client

    @app_commands.command(description="joins a voice channel.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(connect=True)
    async def join(self, interaction: discord.Interaction):
        await self.notify(interaction)

        voice_state = interaction.user.voice
        if voice_state is None:
            raise VoiceClientNotFound
        
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is not None:
            raise BotVoiceClientAlreadyConnected

        # empty queue upon join
        await self.reset_queue(interaction)

        await interaction.user.voice.channel.connect()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` connected to voice channel `{interaction.user.voice.channel.name}`", state=SUCCESS))

    @app_commands.command(description="leaves a voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def leave(self, interaction: discord.Interaction):
        await self.notify(interaction)

        # empty queue upon leave
        await self.reset_queue(interaction)
        
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        
        data = await self._get(interaction)
        state = data["voice"]["state"]
        if state == ISOLATED:
            raise BotVoiceClientIsolation
        
        await voice_client.disconnect()
        # ctx.voice_client.cleanup()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` disconnected from voice channel `{voice_client.channel.name}`", state=SUCCESS))

    async def play_next(self, interaction: discord.Interaction, after_func: Callable):
        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]

        if state == PLAYING:
            queue.pop(0)
        if len(queue) < 1:
            await interaction.channel.send(content=f"queue exhausted. bot `{interaction.client.user.name}` stopped playing.")
            await self.reset_queue(interaction)
            return
        audio: AudioData = queue[0]
        src_url = audio.src_url
        src = discord.FFmpegPCMAudio(src_url, options="-vn")
        self.get_bot_voice_client(interaction).play(discord.PCMVolumeTransformer(src), after=after_func)
        if state == PLAYING:
            data["voice"].update({
                "queue": queue,
            })
        else:
            data["voice"].update({
                "state": PLAYING,
            })
        await self._post(interaction, data)
        await interaction.channel.send(content=sup(f"bot `{interaction.client.user.name}` is playing **{audio.name}** [`(╯°□°)╯︵ ┻━┻`]({audio.webpage_url})", state=SUCCESS))

    @app_commands.command(description="adds an audio to queue.")
    @app_commands.describe(keyword="simply what you would type into YouTube's search bar.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, keyword: app_commands.Range[str, 1, None]):
        def after():
            coro = self.play_next(interaction, after_func=after)
            future = asyncio.run_coroutine_threadsafe(coro, interaction.client.loop)
            future.result()   # must be called to get result from future
        
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise VoiceClientNotFound
        
        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        if state == ISOLATED:
            raise BotVoiceClientIsolation
        
        vid_info = fetch_ytb_audio_info(config=interaction.client.config, keyword=keyword)
        if not vid_info["entries"]:
            raise KeywordNotFound
                
        res = vid_info["entries"][0]   # fetch first url from search query
        vid_url = res["url"]
        vid_name = res["title"]
        vid_webpage_url = res["webpage_url"]

        queue.append(AudioData(vid_url, vid_name, vid_webpage_url))
        data["voice"].update({
            "queue": queue,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot {interaction.client.user.name} added **{vid_name}** to queue", state=SUCCESS))

        if state == PAUSED:
            await self.play_next(interaction, after_func=after)

    """
    a special command only accessible through a selected few.
    when called, immediately terminates the queue (if any) and switches to ISOLATED state; then play desired audio 24/7.
    only stops when forced kick.
    """

    async def iso_play_next(self, interaction: discord.Interaction, after_func: Callable):
        data = await self._get(interaction)
        state = data["voice"]["state"]

        if state != ISOLATED:
            file = assets("audio", "__secret__")
            src = discord.FFmpegPCMAudio(file)
            self.get_bot_voice_client(interaction).play(discord.PCMVolumeTransformer(src), after=after_func)

            data["voice"].update({
                "state": ISOLATED,   # force switch state
                "queue": [],
            })
            await self._post(interaction, data)
            await interaction.channel.send(content=sup(f"bot `{interaction.client.user.name}` entered `isolation`", state=SUCCESS))
        
        else:
            data["voice"].update({
                "state": PAUSED,
            })
            await self._post(interaction, data)
            await interaction.channel.send(content=sup(f"bot `{interaction.client.user.name}` is back to normal", state=SUCCESS))

    @app_commands.command(description="adds a special audio to the queue. requires above-admin privileges.")
    async def isoplay(self, interaction: discord.Interaction):
        def after():
            coro = self.play_next(interaction, after_func=after)
            future = asyncio.run_coroutine_threadsafe(coro, interaction.client.loop)
            future.result()
        
        await self.notify(interaction)
        if interaction.user.id != interaction.client.config["UID"]:
            raise Unauthorized
        if self.get_bot_voice_client(interaction) is None:
            raise VoiceClientNotFound
        
        await self.reset_queue(interaction)
        self.get_bot_voice_client(interaction).stop()

        await self.iso_play_next(interaction, after_func=after)

    @app_commands.command(description="pauses the audio.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def pause(self, interaction: discord.Interaction):
        await self.notify(interaction)
        
        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        if state == ISOLATED:
            raise BotVoiceClientIsolation
        if not queue:
            raise BotVoiceClientQueueEmpty
        if state == PAUSED:
            raise BotVoiceClientAlreadyPaused
        
        voice_client.pause()
        data["voice"].update({
            "state": PAUSED,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` paused in voice channel `{voice_client.channel.name}`", state=SUCCESS))

    @app_commands.command(description="resumes the audio.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def resume(self, interaction: discord.Interaction):
        await self.notify(interaction)

        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        if state == ISOLATED:
            raise BotVoiceClientIsolation
        if not queue:
            raise BotVoiceClientQueueEmpty
        if state == PLAYING:
            raise BotVoiceClientAlreadyPlaying
        
        voice_client.resume()
        data["voice"].update({
            "state": PLAYING,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` resumed in voice channel `{voice_client.channel.name}`", state=SUCCESS))

    @app_commands.command(description="changes the audio volume.")
    @app_commands.describe(value="new volume value to set.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def volume(self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]):
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        self.get_bot_voice_client(interaction).source.volume = value / 100
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}`'s volume changed to `{value}%`", state=SUCCESS))

    @app_commands.command(description="query the current queue.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound
        
        data = await self._get(interaction)
        queue = data["voice"]["queue"]
        if not queue:
            raise BotVoiceClientQueueEmpty
        
        msg = f"\n".join([f"currently playing: **{queue[0].name}**"] + [f"{ind}. {elem.name}" for ind, elem in enumerate(queue[1:])])
        await interaction.edit_original_response(content=msg)

    @app_commands.command(description="skips the current audio in queue.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def skip(self, interaction: discord.Interaction):
        await self.notify(interaction)
    
        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        data = await self._get(interaction)
        queue, state = data["voice"]["queue"], data["voice"]["state"]
        if state == ISOLATED:
            raise BotVoiceClientIsolation
        if not queue:
            raise BotVoiceClientQueueEmpty
        
        self.get_bot_voice_client(interaction).stop()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` skipped **{queue[0].name}**", state=SUCCESS))

    @app_commands.command(description="clears the current queue.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def clear(self, interaction: discord.Interaction):
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound
        
        data = await self._get(interaction)
        state = data["voice"]["state"]
        if state == ISOLATED:
            raise BotVoiceClientIsolation

        await self.reset_queue(interaction)
        self.get_bot_voice_client(interaction).stop()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}`'s queue is cleared", state=SUCCESS))

    # async def cog_before_invoke(self, ctx: Context):
    #     if ctx.bot.intents.voice_states:
    #         return
    #     await ctx.send(err_lack_perm(ctx.bot.user.name, "voice_states"))
    #     raise Exception   # implement a real exception class


"""
warning: personal use only. this violates YouTube's ToS.
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""