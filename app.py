
from asyncio import run as async_run
from dotenv import load_dotenv
load_dotenv()

from bot import create_app
from config import Config


if __name__ == "__main__":
    async_run(create_app(config=Config.__dict__))