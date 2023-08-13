
import asyncio
from dotenv import load_dotenv


load_dotenv()


from client import create_client
from config import Config


client = create_client(config=Config.__dict__)

if __name__ == "__main__":
    asyncio.run(client.start())