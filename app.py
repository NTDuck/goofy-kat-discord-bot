
from asyncio import run as async_run
from dotenv import load_dotenv
load_dotenv()

from bot import create_app
from config import Config


bot = async_run(create_app(config=Config))

if __name__ == "__main__":
    bot.run(Config.SECRET_TOKEN)