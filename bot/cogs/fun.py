
import random
import secrets

from discord import File
from discord.ext.commands import Bot, Cog, Context, command
from ..utils import fetch


class FunCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def choose(self, ctx: Context, *args):
        await ctx.send(random.choice(args) if args else "there's nothing to choose you idiot")

    @command()
    async def miku(self, ctx: Context):
        await ctx.send("are you british?")

    @command()
    async def cat(self, ctx: Context):

        # children functions should return exactly 2 values
        async def _cataas(cfg: dict):
            url = cfg["url"]
            filename = secrets.token_hex(4) + ".png"
            return url, filename
        
        async def _thecatapi(cfg: dict):
            response = await fetch(self.bot.session, url=cfg["url"], format="json", headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await ctx.send("cat don't wanna.")
                return
            url = response[0]["url"]
            filename = secrets.token_hex(4) + "." + url.split(".")[-1]
            return url, filename
        
        async def _shibe(cfg: dict):
            response = await fetch(self.bot.session, url=cfg["url"], format="json", headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await ctx.send("cat don't wanna.")
                return
            url = response[0]
            filename = secrets.token_hex(4) + "." + url.split(".")[-1]
            return url, filename
        
        await ctx.message.add_reaction(random.choice([
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]))

        cfg = self.bot.config["API"]["cat"]
        src = random.choice(list(cfg))

        url, filename = await locals()[f"_{src}"](cfg[src])

        await ctx.send(file=File(fp=await fetch(self.bot.session, url=url, format="bin"), filename=filename))