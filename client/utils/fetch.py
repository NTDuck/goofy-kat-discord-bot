
import os
import random
from collections.abc import Mapping
from typing import Callable, Iterable, Optional, Union

from io import BytesIO
from aiohttp import ClientSession, ClientResponse
from yt_dlp import YoutubeDL

from . import logger
from ..const.fetch import JSON, BINARY


def local_asset(*dirs: str, basedir=["client", "assets"], filename: str) -> str:
    asset = os.path.join(*basedir, *dirs, filename)
    return asset

def rand_local_asset(*dirs: str, basedir=["client", "assets"]) -> Optional[Iterable[str]]:   # might raise OSError if path fails
    dir = os.path.join(*basedir, *dirs)
    # return os.listdir(dir)   # all files in specified directory
    asset = os.path.join(*basedir, *dirs, random.choice(os.listdir(dir)))
    return asset
            
async def fetch(session: ClientSession, url: str, format: int, **kwargs):   # kwargs expect headers & query params

    # children functions should take exactly 1 argument
    async def _json(response: ClientResponse) -> Mapping:
        return await response.json()
    
    async def _bin(response: ClientResponse) -> BytesIO:
        return BytesIO(await response.read())
    
    _d = {
        JSON: _json,
        BINARY: _bin,
    }
    
    async with session.get(url, **kwargs) as response:
        if response.status != 200:
            return None
        return await _d[format](response)   # format param never depends on external dependencies there for does not need try-catch AttributeError
    
def fetch_ytb_audio_info(config: Mapping, keyword: str) -> Union[Mapping, None]:
    # requires diving deep into this: https://pypi.org/project/yt-dlp/
    ydl_opts = config["YT_DLP_OPTIONS"]
    with YoutubeDL(ydl_opts) as ydl_obj:
        vid_info = ydl_obj.extract_info(f"ytsearch:{keyword}", download=False)
    return vid_info

def callables(cls) -> Iterable[Callable]:
    """returns an iterable containing the class's methods (functions and coroutines alike). omits dunderscored methods (e.g. `__init__`) if any."""
    return {k: v for k, v in cls.__dict__.items() if all([
        isinstance(v, Callable),
        not k.startswith("__"),
        not k.endswith("__")
    ])}

print("done")