
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext.commands import command, Bot, Cog, Context
from yt_dlp import YoutubeDL

from ..utils.fetch import fetch_ytb_audio_info
from ..utils.formatter import status_update_prefix as sup, err_lack_perm


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: Context) -> None:
        if ctx.bot.intents.voice_states:
            return
        await ctx.send(err_lack_perm(ctx.bot.user.name, "voice_states"))
        raise Exception   # implement a real exception class

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
        await ctx.author.voice.channel.connect()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` connected to voice channel `{ctx.author.voice.channel.name}`", is_success=True))

    @command()
    async def kick(self, ctx: Context):
        if not get(ctx.bot.voice_clients, guild=ctx.guild):
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is currently not in a voice channel"))
            return
        if not ctx.voice_client.channel.permissions_for(ctx.author).move_members:
            await ctx.send(err_lack_perm(ctx.author.name, "move_members"))   # `kick_members` would be too extreme
            return
        name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` disconnected from voice channel `{name}`", is_success=True))

    @command()
    async def play(self, ctx: Context, *args):
        if not args:
            await ctx.send(sup("please provide a valid keyword"))
            return
        if not get(ctx.bot.voice_clients, guild=ctx.guild):
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is currently not in a voice channel"))
            return
        if ctx.voice_client.is_playing():
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is already playing in voice channel `{ctx.voice_client.channel.name}`"))
            return
        vid_info = fetch_ytb_audio_info(config=ctx.bot.config, search="".join(args))
        res = vid_info["entries"][0]   # fetch first url from search query
        vid_url = res["url"]
        vid_name = res["title"]
        vid_webpage_url = res["webpage_url"]
        ctx.voice_client.play(FFmpegPCMAudio(vid_url, options="-vn"))
        await ctx.send(sup(f"bot {ctx.bot.user.name} is currently playing [`{vid_name}`]({vid_webpage_url})", is_success=True))

    @command()
    async def stop(self, ctx: Context):
        if not get(ctx.bot.voice_clients, guild=ctx.guild):
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is currently not in a voice channel"))
            return
        if ctx.voice_client.is_paused():   # does not actually work
            await ctx.send(sup(f"bot `{ctx.bot.user.name}` is currently not playing in voice channel `{ctx.voice_client.channel.name}`"))
            return
        ctx.voice_client.stop()
        await ctx.send(sup(f"bot `{ctx.bot.user.name}` stopped playing in voice channel `{ctx.voice_client.channel.name}`", is_success=True))

"""
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""