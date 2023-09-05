
import asyncio
from collections.abc import Mapping
from typing import Any, Callable, Optional, Sequence, Union

import discord

from ..const.command import FAILURE, SUCCESS, PENDING, ANXIOUS


def status_update_prefix(msg: str, state=FAILURE) -> str:
    _d = {
        FAILURE: "error",
        SUCCESS: "success",
        PENDING: "pending",
        ANXIOUS: "anxious",
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

def _diff(_d: Mapping[str, Mapping[str, Union[str, Callable[..., str]]]], before: Any, after: Any) -> Sequence[Optional[str]]:
    """
    `_d` is usually a dict that looks like this:
    ```
    _d = {
        "attr1": {
            "repr": "somestring",
            "fmt": "someconverter",
            # other keys not allowed
        },
    }
    ```
    """
    diff = []
    for attr, data in _d.items():
        if getattr(before, attr) == getattr(after, attr):
            continue
        repr = data.get("repr", attr)
        fmt = data.get("fmt", lambda _: _)
        msg = f"{repr}: {fmt(getattr(before, attr))} -> {fmt(getattr(after, attr))}"
        diff.append(msg)
    return diff