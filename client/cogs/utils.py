
# not to be confused with utils/
import asyncio

import discord
from discord import app_commands

from . import CustomCog, CustomGroupCog
from ..const.command import SUCCESS
from ..utils.cryptography import atbash, caesar, caesar_rev, base64, base64_rev, a1z26, a1z26_rev, morse, morse_rev
from ..utils.formatting import status_update_prefix as sup, c


class EncodeCog(CustomGroupCog, name="encode"):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<a:lock:1153177510356451348>", **kwargs)

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """encode w/ a1z26. replaces letters with their position in the alphabet."""
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        enc_str = a1z26(str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(enc_str)}")
    
    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """encode w/ atbash. basically mirrors the alphabet."""
        enc_str = atbash(str)
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: app_commands.Range[str, 1], shift: app_commands.Range[int, -26, 26] = 3):
        """encode w/ caesar. shifts letters by a fixed value (usually 3)"""
        enc_str = caesar(str, shift=shift)
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """encode w/ base64. returns a binary representation."""
        enc_str = base64(str)
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """encode w/ morse. converts characters into dits and dahs."""
        cfg = interaction.client.config["ENCODING"]["morse"]
        enc_str = morse(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(enc_str)}")


class DecodeCog(CustomGroupCog, name="decode"):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<a:unlock:1153177082113818694>", **kwargs)

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """decode w/ a1z26. converts numbers representing positions back into letters."""
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        dec_str = a1z26_rev(
            str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(dec_str)}")
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """decode w/ atbash. basically mirrors the alphabet."""
        dec_str = atbash(str)
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command(description="decode something using caesar cipher.")
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """decode w/ caesar. three letters back! gravity falls, the good old days."""
        dec_str = caesar_rev(str, shift=interaction.client.config["ENCODING"]["caesar_shift"])
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """decode w/ base64. converts gibberish into readable text."""
        dec_str = base64_rev(str)
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command()
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        """decode w/ morse. converts dits and dahs back into latin characters."""
        cfg = interaction.client.config["ENCODING"]["morse"]
        dec_str = morse_rev(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
            _null_repr=cfg["null_repr"],
        )
        await interaction.response.send_message(content=f"{c(dec_str)}")


class ExecCog(CustomGroupCog, name="exec"):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<a:code:1153182080470089809>", **kwargs)


class UtilityCog(CustomCog, name="utilities"):
    def __init__(self, client: discord.Client, **kwargs):
        super().__init__(client, emoji="<a:cog:1153182523879346287>", **kwargs)

    # should require near-administrative privileges
    @app_commands.command()
    @app_commands.describe(number="the number of messages to delete.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def cls(self, interaction: discord.Interaction, number: app_commands.Range[int, 1, 100]):
        """clear up to 100 messages within current text channel."""
        await self.notify(interaction)
        
        resp = await interaction.original_response()
        limit = number + 1
        
        await interaction.channel.purge(limit=limit, check=lambda msg: msg.id != resp.id, bulk=True)

        await interaction.edit_original_response(content=sup(f"deleted up to {c(number.__str__())} messages in channel {c(interaction.channel.name)}", state=SUCCESS))
        await asyncio.sleep(2)
        await interaction.delete_original_response()