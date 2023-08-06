
# not to be confused with utils/

from discord.ext.commands import Bot, Cog, Context, command
from ..utils.formatter import status_update_prefix as sup, err_lack_perm


class UtilityCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # should require administrative privileges
    @command()
    async def cls(self, ctx: Context, limit: int | str):
        max_limit = ctx.bot.config["MAX_CLEAR_LIMIT"]
        if isinstance(limit, int):
            if limit > 0:
                if limit >= max_limit:
                    limit = max_limit
                else:
                    limit += 1
        elif limit == "*":
            limit = max_limit
        else:
            await ctx.send(sup("param `limit` must be a positive integer or string `*`"))
            return
        
        for perm in ["manage_messages", "read_message_history"]:
            if getattr(ctx.bot_permissions, perm):
                continue
            await ctx.send(err_lack_perm(ctx.bot.user.name, perm))
            return
        
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send(err_lack_perm(ctx.author.name, "manage_messages"))   # `kick_members` would be too extreme
            return
        
        await ctx.channel.delete_messages(
            messages=[msg async for msg in ctx.channel.history(limit=limit)],
            reason=f"command invoked by `{ctx.author.name}`.",
        )
        await ctx.channel.send(
            content=sup(f"deleted at most `{limit}` messages in channel `{ctx.channel.name}`", is_success=True),
            delete_after=float(1),
        )