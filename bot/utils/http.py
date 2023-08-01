
from io import BytesIO
from aiohttp import ClientSession, ClientResponse
            

async def fetch(session: ClientSession, url: str, format: str, **kwargs):   # kwargs expect headers & query params

    # children functions should take exactly 1 argument
    async def _json(response: ClientResponse) -> dict:
        return await response.json()
    
    async def _bin(response: ClientResponse) -> BytesIO:
        return BytesIO(await response.read())
    
    async with session.get(url, **kwargs) as response:
        if response.status != 200:
            return None
        return await locals()[f"_{format}"](response)   # format param never depends on external dependencies there for does not need try-catch AttributeError