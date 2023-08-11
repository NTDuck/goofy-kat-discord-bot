
import asyncio

from discord import app_commands, Client, Embed, FFmpegPCMAudio, Interaction, PCMVolumeTransformer, VoiceClient, Permissions

from . import CustomCog
from ..const import PAUSED, PLAYING
from ..errors import VoiceClientNotFound, BotVoiceClientNotFound, BotVoiceClientAlreadyConnected, BotVoiceClientAlreadyPaused, BotVoiceClientAlreadyPlaying, BotVoiceClientQueueEmpty, KeywordNotFound
from ..utils.fetch import fetch_ytb_audio_info
from ..utils.formatter import status_update_prefix as sup


class AudioInfo:   # pickle serializable
    def __init__(self, src_url: str, name: str, webpage_url: str):
        self.src_url = src_url
        self.name = name
        self.webpage_url = webpage_url


class AudioCog(CustomCog):
    def __init__(self, client: Client):
        self.client = client

    async def _get(self, interaction: Interaction) -> dict:
        return await interaction.client._get(id=interaction.guild_id)
    
    async def _post(self, interaction: Interaction, value: dict) -> None:
        await interaction.client._post(id=interaction.guild_id, value=value)

    async def reset_queue(self, interaction: Interaction) -> None:
        default_state = {
            "voice": {
                "state": PAUSED,
                "queue": [],
            }
        }
        await self._post(interaction, default_state)

    # @kick.before_invoke
    # @play.before_invoke
    # @pause.before_invoke
    # @resume.before_invoke
    # @vol.before_invoke
    def get_bot_voice_client(self, interaction: Interaction) -> VoiceClient:
        return interaction.client.get_guild(interaction.guild_id).voice_client

    @app_commands.command(description="joins a voice channel.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(connect=True)
    async def join(self, interaction: Interaction):
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
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` connected to voice channel `{interaction.user.voice.channel.name}`", success=True))

    @app_commands.command(description="leaves a voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def leave(self, interaction: Interaction):
        await self.notify(interaction)

        # empty queue upon leave
        await self.reset_queue(interaction)
        
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        await voice_client.disconnect()
        # ctx.voice_client.cleanup()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` disconnected from voice channel `{voice_client.channel.name}`", success=True))

    async def play_next(self, interaction: Interaction, after_func):
        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]

        if state == PLAYING:
            queue.pop(0)
        if len(queue) < 1:
            await interaction.channel.send(content=f"queue exhausted. bot `{interaction.client.user.name}` stopped playing.")
            await self.reset_queue(interaction)
            return
        audio: AudioInfo = queue[0]
        src_url = audio.src_url
        src = FFmpegPCMAudio(src_url, options="-vn")
        self.get_bot_voice_client(interaction).play(PCMVolumeTransformer(src), after=after_func)
        if state == PLAYING:
            data["voice"].update({
                "queue": queue,
            })
        else:
            data["voice"].update({
                "state": PLAYING,
            })
        await self._post(interaction, data)
        await interaction.channel.send(content=sup(f"bot `{interaction.client.user.name}` is playing **{audio.name}** [`(╯°□°)╯︵ ┻━┻`]({audio.webpage_url})", success=True))

    @app_commands.command(description="adds an audio to queue.")
    @app_commands.describe(keyword="simply what you would type into YouTube's search bar.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: Interaction, keyword: app_commands.Range[str, 1, None]):
        def after(error=None):
            if error:
                print(error)
                return
            coro = self.play_next(interaction, after_func=after)
            future = asyncio.run_coroutine_threadsafe(coro, interaction.client.loop)
            future.result()   # must be called to get result from future
        
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise VoiceClientNotFound
        vid_info = fetch_ytb_audio_info(config=interaction.client.config, keyword=keyword)

        if not vid_info["entries"]:
            raise KeywordNotFound
                
        res = vid_info["entries"][0]   # fetch first url from search query
        vid_url = res["url"]
        vid_name = res["title"]
        vid_webpage_url = res["webpage_url"]

        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        queue.append(AudioInfo(vid_url, vid_name, vid_webpage_url))
        data["voice"].update({
            "queue": queue,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot {interaction.client.user.name} added **{vid_name}** to queue", success=True))

        if state == PAUSED:
            await self.play_next(interaction, after_func=after)

    @app_commands.command(description="pauses the audio.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def pause(self, interaction: Interaction):
        await self.notify(interaction)
        
        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        if state == PAUSED:
            raise BotVoiceClientAlreadyPaused
        if not queue:
            raise BotVoiceClientQueueEmpty
        
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        
        voice_client.pause()
        data["voice"].update({
            "state": PAUSED,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` paused in voice channel `{voice_client.channel.name}`", success=True))

    @app_commands.command(description="resumes the audio.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def resume(self, interaction: Interaction):
        await self.notify(interaction)

        data = await self._get(interaction)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        if state == PLAYING:
            raise BotVoiceClientAlreadyPlaying
        if not queue:
            raise BotVoiceClientQueueEmpty
        
        voice_client = self.get_bot_voice_client(interaction)
        if voice_client is None:
            raise BotVoiceClientNotFound
        voice_client.resume()
        data["voice"].update({
            "state": PLAYING,
        })
        await self._post(interaction, data)

        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` resumed in voice channel `{voice_client.channel.name}`", success=True))

    @app_commands.command(description="changes the audio volume.")
    @app_commands.describe(value="new volume value to set.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def volume(self, interaction: Interaction, value: app_commands.Range[int, 0, 100]):
        await self.notify(interaction)

        self.get_bot_voice_client(interaction).source.volume = value / 100
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}`'s volume changed to `{value}%`", success=True))

    @app_commands.command(description="query the current queue.")
    @app_commands.checks.cooldown(rate=1, per=1.0, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: Interaction):
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
    async def skip(self, interaction: Interaction):
        await self.notify(interaction)
    
        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        data = await self._get(interaction)
        queue = data["voice"]["queue"]
        if not queue:
            raise BotVoiceClientQueueEmpty
        
        self.get_bot_voice_client(interaction).stop()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}` skipped **{queue[0].name}**", success=True))

    @app_commands.command(description="clears the current queue.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    async def clear(self, interaction: Interaction):
        await self.notify(interaction)

        if self.get_bot_voice_client(interaction) is None:
            raise BotVoiceClientNotFound

        await self.reset_queue(interaction)
        self.get_bot_voice_client(interaction).stop()
        await interaction.edit_original_response(content=sup(f"bot `{interaction.client.user.name}`'s queue is cleared", success=True))

    # async def cog_before_invoke(self, ctx: Context):
    #     if ctx.bot.intents.voice_states:
    #         return
    #     await ctx.send(err_lack_perm(ctx.bot.user.name, "voice_states"))
    #     raise Exception   # implement a real exception class


"""
warning: personal use only. this violates YouTube's ToS.
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""