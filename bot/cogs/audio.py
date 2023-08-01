
from discord import FFmpegPCMAudio, VoiceClient, VoiceChannel
from discord.ext.commands import command, Bot, Cog, Context
from yt_dlp import YoutubeDL


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: Context) -> None:
        if ctx.bot.intents.voice_states:
            return
        await ctx.send(f"""
error: bot does not have `voice_states` permissions.
for authenticated users, this can be troubleshooted as follows:
- try re-inviting the bot with said permission enabled.
- try enabling the bot's said permission server-wide and channel-wide.
        """)
        raise Exception   # implement a real exception class

    @command()
    async def join(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.send(f"error: invoker `{ctx.author}` is currently not in a voice channel.")
            return
        if ctx.voice_client.is_connected():
            await ctx.send(f"error: bot is already connected to voice channel `{ctx.voice_client.channel.name}`.")
            return
        await ctx.author.voice.channel.connect()
        await ctx.send(f"success: connected to voice channel `{ctx.author.voice.channel.name}`.")

    @command()
    async def kick(self, ctx: Context):
        if not ctx.voice_client.is_connected():
            await ctx.send("error: bot is not in a voice channel.")
            return
        if not ctx.voice_client.channel.permissions_for(ctx.author).move_members:
            await ctx.send(f"error: invoker `{ctx.author}` does not have `move_members` permission.")   # `kick_members` would be too extreme
            return
        await ctx.voice_client.disconnect()
        await ctx.send(f"success: disconnected from voice channel `{ctx.voice_client.channel.name}`.")

    @command()
    async def play(self, ctx: Context, *args):
        if not ctx.voice_client.is_connected():
            await ctx.send("error: bot is not in a voice channel.")
            return
        # if the bot is already playing; if the bot has insufficient perms; if args is empty ...

        # requires diving deep into this: https://pypi.org/project/yt-dlp/
        ydl_opts = self.bot.config["YT_DLP_OPTIONS"]
        with YoutubeDL(ydl_opts) as ydl_obj:
            vid_info = ydl_obj.extract_info(f"ytsearch:{''.join(args)}", download=False)
            # print(json.dumps(ydl_obj.sanitize_info(vid_info)))

        # fetch first url from search query
        vid_url = vid_info["entries"][0]["url"]
        ctx.voice_client.play(FFmpegPCMAudio(vid_url, options="-vn"))
        await ctx.send("success: bot is playing something for ya.")

    @command()
    async def stop(self, ctx: Context):
        if not ctx.voice_client.is_connected():
            await ctx.send("error: bot is not in a voice channel.")
            return
        await ctx.voice_client.stop()
        await ctx.send(f"success: bot stop playing in voice channel `{ctx.voice_client.channel.name}`.")

"""
this is far from complete. note-to-self: ensure perms & handle exceptions.
"""