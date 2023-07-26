
import random
from io import BytesIO

import aiohttp


async def random_cat():
    server = "https://cataas.com/"
    src = f"{server}cat"

    async with aiohttp.ClientSession() as session:
        async with session.get(src) as resp:
            if resp.status != 200:
                return "error: could not fetch file from RESTful server."
            return BytesIO(await resp.read())