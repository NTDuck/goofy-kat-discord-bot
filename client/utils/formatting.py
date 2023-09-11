
import asyncio
from collections.abc import Mapping
from typing import Any, Callable, Optional, Sequence, Union

import discord

from ..const.command import FAILURE, SUCCESS, PENDING, ANXIOUS


# text formatting
# https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-
def _add_delimiter(s: str, delimiter: str):
    return delimiter + s + delimiter[::-1]   # have to iterate over delimiter -> O(n) -> bad (?)

def italic(s: str) -> str:
    # f"_{s}_" also works
    return _add_delimiter(s, "*")

def bold(s: str) -> str:
    return _add_delimiter(s, "**")

def bold_italic(s: str) -> str:
    return _add_delimiter(s, "***")

def underline(s: str) -> str:
    return _add_delimiter(s, "__")

def underline_italics(s: str) -> str:
    return _add_delimiter(s, "__*")

def underline_bold(s: str) -> str:
    return _add_delimiter(s, "__**")

def underline_bold_italics(s: str) -> str:
    return _add_delimiter(s, "__***")

def strikethrough(s: str) -> str:
    return _add_delimiter(s, "~~")

# organizational text formatting
def header(s: str, level: int = 1) -> str:
    """
    \nparam `level` (1 - 3) indicates the header level.
    \nno inline character should stand before `s`.
    """
    return "#" * level + s

def masked_link(repr: str, url: str) -> str:
    return f"[{repr}]({url})"

def bulleted_list(elements: Mapping[str, int]) -> str:
    """
    returns a bulleted list.
    \nparam `elements` should strictly follow this format: `{"some_element": some_indentation_level}`. If indentation is not desired, `some_indentation_level` should manually be set to `0`.
    """
    return "\n".join([f"{' ' * indent}* {content}" for content, indent in elements.items()])

def code_block(s: str, multiline=False) -> str:
    n = 1 if not multiline else 3
    return _add_delimiter(s, "`" * n)

def block_quote(s: str, multiline=False) -> str:
    n = 1 if not multiline else 3
    return f"{'>' * n} {s}"

def spoiler(s: str) -> str:
    """negated by a code block"""
    return _add_delimiter(s, "||")

# convenience's sake
i = italic
b = bold
bi = bold_italic
u = underline
ui = underline_italics
ub = underline_bold
ubi = underline_bold_italics
st = strikethrough
url = masked_link
seq = bulleted_list
c = code_block
q = block_quote
sp = spoiler

# miscellaneous
def status_update_prefix(msg: str, state=FAILURE) -> str:
    _d = {
        FAILURE: "error",
        SUCCESS: "success",
        PENDING: "pending",
        ANXIOUS: "anxious",
    }
    return f"{b(_d[state])}: {msg}."   # exception handling not required: param not dependent on user input

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

def diff(_d: Mapping[str, Mapping[str, Union[str, Callable[..., str]]]], before: Any, after: Any) -> Sequence[Optional[str]]:
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
    _diff = []
    for attr, data in _d.items():
        if getattr(before, attr) == getattr(after, attr):
            continue
        repr = data.get("repr", attr)
        fmt = data.get("fmt", lambda _: _)
        msg = f"{repr}: {fmt(getattr(before, attr))} -> {fmt(getattr(after, attr))}"
        _diff.append(msg)
    return _diff