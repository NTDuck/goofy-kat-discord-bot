
import asyncio

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.utils import get
from discord.ext.commands import command, Bot, Cog, Context

from ..const import PAUSED, PLAYING
from ..utils.fetch import fetch_ytb_audio_info
from ..utils.formatter import status_update_prefix as sup, err_lack_perm


class AudioInfo:
    def __init__(self, src_url: str, name: str, webpage_url: str):
        self.src_url = src_url
        self.name = name
        self.webpage_url = webpage_url


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def _get(self, ctx: Context) -> dict:
        return await self.bot._get(id=ctx.guild.id)
    
    async def _post(self, ctx: Context, value) -> None:
        await self.bot._post(id=ctx.guild.id, value=value)

    async def reset_queue(self, ctx: Context):
        default_state = {
            "voice": {
                "state": PAUSED,
                "queue": [],
            }
        }
        await self._post(ctx, default_state)

    @command()
    async def join(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.send(sup(f"invoker `{ctx.author.name}` is currently not in a voice channel"))
            return
        
        if get(ctx.bot.voice_clients, guild=ctx.guild):
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already connected to voice channel `{ctx.voice_client.channel.name}`"))
            return
        
        # if not ctx.bot_permissions.connect:
        #     await ctx.send(err_lack_perm(ctx.bot.user.name, "connect"))
        #     return

        # empty queue upon join
        await self.reset_queue(ctx)

        await ctx.author.voice.channel.connect()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` connected to voice channel `{ctx.author.voice.channel.name}`", is_success=True))

    @command()
    async def kick(self, ctx: Context):        
        if not ctx.voice_client.channel.permissions_for(ctx.author).move_members:
            await ctx.send(err_lack_perm(ctx.author.name, "move_members"))   # `kick_members` would be too extreme
            return
        
        # empty queue upon leave
        await self.reset_queue(ctx)
        
        name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        # ctx.voice_client.cleanup()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` disconnected from voice channel `{name}`", is_success=True))

    async def play_next(self, ctx: Context, after_func):
        data = await self._get(ctx)
        state, queue = data["voice"]["state"], data["voice"]["queue"]

        if state == PLAYING:
            queue.pop(0)
        if len(queue) < 1:
            await ctx.send(f"queue exhausted, bot `{ctx.bot.user.name}` stopped playing.")
            await self.reset_queue(ctx)
            return
        audio: AudioInfo = queue[0]
        src_url = audio.src_url
        src = FFmpegPCMAudio(src_url, options="-vn")
        ctx.voice_client.play(PCMVolumeTransformer(src), after=after_func)
        if state == PLAYING:
            data["voice"].update({
                "queue": queue,
            })
        else:
            data["voice"].update({
                "state": PLAYING,
            })
        await self._post(ctx, data)
        await ctx.send(sup(f"bot {ctx.bot.user.name} is currently [playing]({audio.webpage_url}) **{audio.name}**", is_success=True))

    @command()
    async def play(self, ctx: Context, *args):
        def after(error=None):
            if error:
                print(error)
                return
            coro = self.play_next(ctx=ctx, after_func=after)
            future = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
            future.result()   # must be called to get result from future

        if not args:
            await ctx.send(sup("please provide a valid keyword"))
            return
        
        search = " ".join(args)
        vid_info = fetch_ytb_audio_info(config=ctx.bot.config, search=search)

        if not vid_info["entries"]:
            await ctx.send(sup(f"cannot find video that matches keyword `{search}`"))
            return
                
        res = vid_info["entries"][0]   # fetch first url from search query
        vid_url = res["url"]
        vid_name = res["title"]
        vid_webpage_url = res["webpage_url"]

        data = await self._get(ctx)
        state, queue = data["voice"]["state"], data["voice"]["queue"]
        queue.append(AudioInfo(vid_url, vid_name, vid_webpage_url))
        data["voice"].update({
            "queue": queue,
        })
        await self._post(ctx, data)

        await ctx.send(sup(f"bot {ctx.bot.user.name} added **{vid_name}** to queue", is_success=True))

        if state == PAUSED:
            await self.play_next(ctx=ctx, after_func=after)

    @command()
    async def pause(self, ctx: Context):
        data = await self._get(ctx)
        state = data["voice"]["state"]
        if state == PAUSED:
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already paused in voice channel `{ctx.voice_client.channel.name}`"))
            return
        
        ctx.voice_client.pause()
        data["voice"].update({
            "state": PAUSED,
        })
        await self._post(ctx, data)

        await ctx.send(sup(f"bot `{ctx.bot.user.name}` paused in voice channel `{ctx.voice_client.channel.name}`", is_success=True))

    @command()
    async def resume(self, ctx: Context):
        data = await self._get(ctx)
        state = data["voice"]["state"]
        if state == PLAYING:
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already playing in voice channel `{ctx.voice_client.channel.name}`"))
            return
        
        ctx.voice_client.resume()
        data["voice"].update({
            "state": PLAYING,
        })
        await self._post(ctx, data)

        await ctx.send(sup(f"bot `{ctx.bot.user.name}` resumed in voice channel `{ctx.voice_client.channel.name}`", is_success=True))

    @command()
    async def vol(self, ctx: Context, volume: int):
        if not all([
            isinstance(volume, int),
            0 <= volume <= 100,
        ]):
            await ctx.send(sup("param `volume` must be a suitable positive integer"))
            return
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` changed volume to `{volume}%`", is_success=True))

    @command()
    async def queue(self, ctx: Context):
        data = await self._get(ctx)
        queue = data["voice"]["queue"]
        msg = f"\n".join([f"currently playing: **{queue[0].name}**"] + [f"{ind}. {elem.name}" for ind, elem in enumerate(queue[1:])]) if queue else "queue is currently empty."
        await ctx.send(msg)

    @command()
    async def skip(self, ctx: Context):
        data = await self._get(ctx)
        queue = data["voice"]["queue"]
        ctx.voice_client.stop()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` skipped **{queue[0].name}**", is_success=True))

    @command()
    async def clear(self, ctx: Context):
        await self.reset_queue(ctx=ctx)
        ctx.voice_client.stop()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` cleared current queue", is_success=True))

    async def cog_before_invoke(self, ctx: Context):
        if ctx.bot.intents.voice_states:
            return
        await ctx.send(err_lack_perm(ctx.bot.user.name, "voice_states"))
        raise Exception   # implement a real exception class

    @kick.before_invoke
    @play.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @vol.before_invoke
    async def ensure_voice(self, ctx: Context):
        if ctx.bot.get_guild(ctx.guild.id).voice_client:
            return
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` is currently not in a voice channel"))
        raise Exception


"""
warning: personal use only. this violates YouTube's ToS.
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""