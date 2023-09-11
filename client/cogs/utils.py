
# not to be confused with utils/
import asyncio

import discord
from discord import app_commands

from . import CustomCog, CustomGroupCog
from ..const.command import SUCCESS
from ..utils.cryptography import atbash, caesar, caesar_rev, base64, base64_rev, a1z26, a1z26_rev, morse, morse_rev
from ..utils.formatting import status_update_prefix as sup, c


class EncodeCog(CustomGroupCog, name="encode"):
    def __init__(self, client: discord.Client):
        super().__init__(client, index=4, emoji=":onion:")

    @app_commands.command(description="encode something using a1z26 cipher.")
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        enc_str = a1z26(str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(enc_str)}")
    
    @app_commands.command(description="encode something using atbash cipher.")
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        enc_str = atbash(str)
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command(description="encode something using caesar cipher.")
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        enc_str = caesar(str, shift=interaction.client.config["ENCODING"]["caesar"]["shift"])
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command(description="encode something using base64.")
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        enc_str = base64(str)
        await interaction.response.send_message(content=f"{c(enc_str)}")

    @app_commands.command(description="encode something using international morse code.")
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        cfg = interaction.client.config["ENCODING"]["morse"]
        enc_str = morse(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(enc_str)}")


class DecodeCog(CustomGroupCog, name="decode"):
    def __init__(self, client: discord.Client):
        super().__init__(client, index=5, emoji=":garlic:")

    @app_commands.command(description="decode something using a1z26 cipher.")
    @app_commands.describe(str="anything really")
    async def a1z26(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        cfg = interaction.client.config["ENCODING"]["a1z26"]
        dec_str = a1z26_rev(
            str,
            char_sep=cfg["char_sep"],
            word_sep=cfg["word_sep"],
        )
        await interaction.response.send_message(content=f"{c(dec_str)}")
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command(description="decode something using atbash cipher.")
    @app_commands.describe(str="anything really")
    async def atbash(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        dec_str = atbash(str)
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command(description="decode something using caesar cipher.")
    @app_commands.describe(str="anything really")
    async def caesar(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        dec_str = caesar_rev(str, shift=interaction.client.config["ENCODING"]["caesar_shift"])
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command(description="decode something using base64.")
    @app_commands.describe(str="anything really")
    async def base64(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        dec_str = base64_rev(str)
        await interaction.response.send_message(content=f"{c(dec_str)}")

    @app_commands.command(description="decode something using international morse code.")
    @app_commands.describe(str="anything really")
    async def morse(self, interaction: discord.Interaction, str: app_commands.Range[str, 1]):
        cfg = interaction.client.config["ENCODING"]["morse"]
        dec_str = morse_rev(str,
            _dit=cfg["dit"],
            _dah=cfg["dah"],
            _char_sep=cfg["char_sep"],
            _word_sep=cfg["word_sep"],
            _null_repr=cfg["null_repr"],
        )
        await interaction.response.send_message(content=f"{c(dec_str)}")


class UtilityCog(CustomCog, name="utilities"):
    def __init__(self, client: discord.Client):
        super().__init__(client, index=3, emoji=":gear:")

    # should require near-administrative privileges
    @app_commands.command(description="clear messages within the current text channel.")
    @app_commands.describe(number="the number of messages to delete.")
    @app_commands.checks.cooldown(rate=1, per=3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def cls(self, interaction: discord.Interaction, number: app_commands.Range[int, 1, 100]):
        await self.notify(interaction)
        
        resp = await interaction.original_response()
        limit = number + 1
        
        await interaction.channel.purge(limit=limit, check=lambda msg: msg.id != resp.id, bulk=True)

        await interaction.edit_original_response(content=sup(f"deleted up to {c(number.__str__())} messages in channel {c(interaction.channel.name)}", state=SUCCESS))
        await asyncio.sleep(2)
        await interaction.delete_original_response()