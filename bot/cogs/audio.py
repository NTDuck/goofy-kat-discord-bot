
from discord.ext.commands import command, Bot, Cog, Context


class AudioCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def join(self, ctx: Context):
        # join current channel\
        if ctx.author.voice is None:
            await ctx.send(f"error: invoker `{ctx.author}` is currently not in a voice channel.")
            return
        if not self.bot.intents.voice_states:
            await ctx.send(f"""
error: bot does not have `voice_states` permissions.
for authenticated users, this can be troubleshooted as follows:
- try re-inviting the bot with said permission enabled.
- try enabling the bot's said permission server-wide and channel-wide.
            """)
            return
        print("voice connect start here!")
        await ctx.author.voice.channel.connect()
        # await ctx.send(f"connected to voice channel `{ctx.author.voice.channel.name}`.")
        
        # await ctx.send(ctx.author.voice.channel.name)

    # @command
    # async def kick(self, ctx: Context):
    #     # kick out of current voice channel
    #     ...

    # @command
    # async def play(self, ctx: Context):
    #     # play 24/7 until server crash (not auto-re-join)
    #     ...

    # @command
    # async def stop(self, ctx: Context):
    #     # there has to be something for it to stop playing
    #     ...