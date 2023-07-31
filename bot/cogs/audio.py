
import json
from discord import FFmpegPCMAudio, VoiceClient
from discord.ext.commands import command, Bot, Cog, Context
from yt_dlp import YoutubeDL


async def check_intents(ctx: Context):
    if not ctx.bot.intents.voice_states:
        await ctx.send(f"""
error: bot does not have `voice_states` permissions.
for authenticated users, this can be troubleshooted as follows:
- try re-inviting the bot with said permission enabled.
- try enabling the bot's said permission server-wide and channel-wide.
        """)
        return


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def join(self, ctx: Context):
        # join current channel\
        if ctx.author.voice is None:
            await ctx.send(f"error: invoker `{ctx.author}` is currently not in a voice channel.")
            return
        await check_intents(ctx=ctx)
        await ctx.author.voice.channel.connect()
        await ctx.send(f"connected to voice channel `{ctx.author.voice.channel.name}`.")

    @command()
    async def kick(self, ctx: Context):
        voice_client: VoiceClient = ctx.voice_client
        if voice_client is None:
            await ctx.send("error: bot is not in a voice channel.")
            return
        await voice_client.disconnect()
        await ctx.send(f"disconnected from voice channel `{voice_client.channel.name}`.")


    # # here is a local version of the `play` command
    # @command()
    # async def play(self, ctx: Context):
    #     # play 24/7 until server crash (not auto-re-join)
    #     await check_intents(ctx=ctx)
    #     v: VoiceClient = ctx.voice_client   # type annotation for easier interaction
    #     if v is None:
    #         await ctx.send("error: bot is not in a voice channel.")
    #         return
    #     mp3_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'audio', 'wonderhoy.mp3')
    #     v.play(FFmpegPCMAudio(mp3_file_path))

    @command()
    async def play(self, ctx: Context, *args):
        voice_client: VoiceClient = ctx.voice_client   # type annotation for easier interaction
        if voice_client is None:
            await ctx.send("error: bot is not in a voice channel.")
            return
        await check_intents(ctx=ctx)
        # if the bot is already playing; if the bot has insufficient perms; if args is empty ...

        # requires diving deep into this: https://pypi.org/project/yt-dlp/
        ydl_opts = {
            "format": "m4a/worstaudio",
            "hls-use-mpegts": True,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "60",
            }],
        }
        with YoutubeDL(ydl_opts) as ydl_obj:
            vid_info = ydl_obj.extract_info(f"ytsearch:{''.join(args)}", download=False)
            # print(json.dumps(ydl_obj.sanitize_info(vid_info)))

        # fetch first url from search query
        vid_url = vid_info["entries"][0]["url"]
        voice_client.play(FFmpegPCMAudio(vid_url, options="-vn"))
        await ctx.send("bot is playing something for ya.")

    @command()
    async def stop(self, ctx: Context):
        voice_client: VoiceClient = ctx.voice_client
        if voice_client is None:
            await ctx.send("error: bot is not in a voice channel.")
            return
        await check_intents(ctx=ctx)
        await voice_client.stop()
        await ctx.send(f"bot stop palying in voice channel `{voice_client.channel.name}`.")

"""
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""