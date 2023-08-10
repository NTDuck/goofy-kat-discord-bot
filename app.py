
from asyncio import run as async_run
from dotenv import load_dotenv
load_dotenv()

from bot import create_client
from config import Config


client = create_client(config=Config.__dict__)

if __name__ == "__main__":
    async_run(client.start())