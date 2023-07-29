
from io import BytesIO

from aiohttp import ClientSession
            

async def fetch(session: ClientSession, url: str, return_format: str, **kwargs) -> dict | BytesIO | None:   # kwargs expect headers & query params
    async with session.get(url, **kwargs) as response:
        if response.status != 200:
            return None
        # please do not force me to use if else, it's ugly af
        if return_format == "json":
            return await response.json()
        elif return_format == "bin":
            return BytesIO(await response.read())