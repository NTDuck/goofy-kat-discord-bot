
import asyncio
from collections.abc import Mapping
from typing import Sequence, Union

import discord

from ..const.command import FAILURE, SUCCESS, PENDING


def status_update_prefix(msg: str, state=FAILURE) -> str:
    _d = {
        FAILURE: "error",
        SUCCESS: "success",
        PENDING: "pending",
    }
    return f"**{_d[state]}**: {msg}."   # exception handling not required: param not dependent on user input

def incremental_string(s: str, signals: Mapping[str, Union[float, int]]) -> Sequence[Sequence[Union[str, float, int]]]:
    seq = []
    tmp = ""   # tracking purposes
    for chr in s:
        tmp += chr
        if chr not in signals.keys():
            continue
        seq.append([tmp, signals[chr]])
        tmp = ""   # reset
    if tmp not in signals.keys():
        seq.append([tmp, signals.get(" ", 0.1)])
    return seq

async def incremental_response(interaction: discord.Interaction, msg: str, signals: Mapping[str, Union[float, int]] = {" ": 0.1, ".": 0.5}):   # poor performance
    """requirements: interaction have a response message i.e. `await interaction.response.original_response() is not None`"""
    seq = incremental_string(s=msg, signals=signals)
    tmp = ""
    for _s, _t in seq:
        tmp += _s
        await interaction.edit_original_response(content=tmp)
        await asyncio.sleep(_t)