
import asyncio

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.utils import get
from discord.ext.commands import command, Bot, Cog, Context

from ..const import PAUSED, PLAYING
from ..utils.fetch import fetch_ytb_audio_info
from ..utils.formatter import status_update_prefix as sup, err_lack_perm


class AudioInfo:
    def __init__(self, src: FFmpegPCMAudio, name: str, webpage_url: str):
        self.src = src
        self.name = name
        self.webpage_url = webpage_url


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    def reset_queue(self, ctx: Context):
        ctx.bot.g[ctx.guild.id]["voice"].update({
            "state": PAUSED,
            "queue": [],
        })

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
        self.reset_queue(ctx=ctx)

        await ctx.author.voice.channel.connect()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` connected to voice channel `{ctx.author.voice.channel.name}`", is_success=True))

    @command()
    async def kick(self, ctx: Context):        
        if not ctx.voice_client.channel.permissions_for(ctx.author).move_members:
            await ctx.send(err_lack_perm(ctx.author.name, "move_members"))   # `kick_members` would be too extreme
            return
        
        # empty queue upon leave
        self.reset_queue(ctx=ctx)
        
        name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        # ctx.voice_client.cleanup()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` disconnected from voice channel `{name}`", is_success=True))

    async def play_next(self, ctx: Context, after_func):
        v = ctx.bot.g[ctx.guild.id]["voice"]
        state, queue = v["state"], v["queue"]
        if state == PLAYING:
            queue.pop(0)
        if len(queue) < 1:
            await ctx.send(f"queue exhausted, bot `{ctx.bot.user.name}` stopped playing.")
            v.update({
                "state": PAUSED,
            })
            return
        audio: AudioInfo = queue[0]
        src = audio.src
        ctx.voice_client.play(PCMVolumeTransformer(src), after=after_func)
        if state == PLAYING:
            v.update({
                "queue": queue,
            })
        else:
            v.update({
                "state": PLAYING,
            })
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

        queue = ctx.bot.g[ctx.guild.id]["voice"]["queue"]
        src = FFmpegPCMAudio(vid_url, options="-vn")
        queue.append(AudioInfo(src, vid_name, vid_webpage_url))
        ctx.bot.g[ctx.guild.id]["voice"].update({
            "queue": queue,
        })

        await ctx.send(sup(f"bot {ctx.bot.user.name} added **{vid_name}** to queue", is_success=True))

        if ctx.bot.g[ctx.guild.id]["voice"]["state"] == PAUSED:
            await self.play_next(ctx=ctx, after_func=after)

    @command()
    async def pause(self, ctx: Context):
        if ctx.bot.g[ctx.guild.id]["voice"]["state"] == PAUSED:
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already paused in voice channel `{ctx.voice_client.channel.name}`"))
            return
        
        ctx.voice_client.pause()
        ctx.bot.g[ctx.guild.id]["voice"].update({
            "state": PAUSED,
        })

        await ctx.send(sup(f"bot `{ctx.bot.user.name}` paused in voice channel `{ctx.voice_client.channel.name}`", is_success=True))

    @command()
    async def resume(self, ctx: Context):
        if ctx.bot.g[ctx.guild.id]["voice"]["state"] == PLAYING:
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already playing in voice channel `{ctx.voice_client.channel.name}`"))
            return
        
        ctx.voice_client.resume()
        ctx.bot.g[ctx.guild.id]["voice"].update({
            "state": PLAYING,
        })

        await ctx.send(sup(f"bot `{ctx.bot.user.name}` resumed in voice channel `{ctx.voice_client.channel.name}`", is_success=True))

    @command()
    async def vol(self, ctx: Context, volume: int):
        if not isinstance(volume, int):
            await ctx.send(sup("param `volume` must be a positive integer"))
            return
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` changed volume to `{volume}%`", is_success=True))

    @command()
    async def queue(self, ctx: Context):
        queue = ctx.bot.g[ctx.guild.id]["voice"]["queue"]
        msg = f"\n".join([f"currently playing: **{queue[0].name}**"] + [f"{ind}. {elem.name}" for ind, elem in enumerate(queue[1:])]) if queue else "queue is currently empty."
        await ctx.send(msg)

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