
import random
import secrets

from discord import File
from discord.ext.commands import Cog, Context, command
from ..utils import fetch


class FunCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def choose(self, ctx: Context, *args):
        await ctx.send(random.choice(args) if args else "there's nothing to choose you idiot")

    @command()
    async def miku(self, ctx: Context):
        await ctx.send("are you british?")

    @command()
    async def cat(self, ctx: Context):
        await ctx.message.add_reaction(random.choice([
            "🐱", "😿", "🙀", "😾", "😹", "😼", "😺", "😽", "😸", "😻",
        ]))

        cfg = self.bot.config["API"]
        choice = random.choice(list(cfg))
        cfg = cfg[choice]
        
        # disclaimer: the following block of code looks like the work of a 3-year-old. a lot of jerky if else.
        # note-to-self: definitely needs re-implementing.

        if choice == "https://cataas.com/":
            response_url = cfg["url"]
            filename = secrets.token_hex(4) + ".png"
        else:
            response = await fetch(self.bot.session, url=cfg["url"], return_format="json", headers=cfg.get("headers"), params=cfg.get("params"))
            if response is None:
                await ctx.send("cat don't wanna.")
                return
            if choice == "https://thecatapi.com/":
                response_url = response[0]["url"]
            elif choice == "https://shibe.online/":
                response_url = response[0]
            filename = secrets.token_hex(4) + "." + response_url.split(".")[-1]

        await ctx.send(file=File(fp=await fetch(self.bot.session, url=response_url, return_format="bin"), filename=filename))