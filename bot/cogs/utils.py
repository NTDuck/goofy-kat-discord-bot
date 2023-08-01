
# not to be confused with utils/

from discord.ext.commands import Bot, Cog, Context, command


class UtilityCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # should require administrative privileges
    @command()
    async def clear(self, ctx: Context, limit: int|str):
        if isinstance(limit, int) and limit > 0:
            limit += + 1
        elif limit == "*":
            limit = None
        else:
            await ctx.send(f"error: param `limit` must be a positive integer or `*`.")
            return
        for perm in ["manage_messages", "read_message_history"]:
            if getattr(ctx.bot_permissions, perm):
                continue
            await ctx.send(f"error: bot does not have `{perm}` permissions.")
            return
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send(f"error: invoker `{ctx.author}` does not have `manage_messages` permission.")   # `kick_members` would be too extreme
            return
        await ctx.channel.delete_messages(
            messages=[msg async for msg in ctx.channel.history(limit=limit)],
            reason=f"command invoked by `{ctx.author}`.",
        )
        if limit is None:
            limit = "all"
        await ctx.channel.send(
            content=f"success: deleted `{limit}` messages in channel `{ctx.channel.name}`.",
            delete_after=float(1),
        )