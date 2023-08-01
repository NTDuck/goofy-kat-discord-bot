
from io import BytesIO
from aiohttp import ClientSession, ClientResponse
from yt_dlp import YoutubeDL
            

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
    

def fetch_ytb_audio_info(config: dict, search: str) -> dict:
    # requires diving deep into this: https://pypi.org/project/yt-dlp/
    ydl_opts = config["YT_DLP_OPTIONS"]
    with YoutubeDL(ydl_opts) as ydl_obj:
        vid_info = ydl_obj.extract_info(f"ytsearch:{search}", download=False)
    return vid_info