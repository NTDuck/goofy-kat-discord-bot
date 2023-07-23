
# hey, this is the beginning of the project!

from discord import Intents, Client
from dotenv import load_dotenv

load_dotenv()
from config import Config


intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)


@client.event
async def on_ready():
    print(f"logged in as {client.user}.")


@client.event
async def on_message(message):
    if getattr(message, "author") == client.user:
        return
    
    if getattr(message, "content") == "ping":   # yeah this is from redis
        await getattr(message, "channel").send("pong!")


# example_link = "https://discord.com/oauth2/authorize?client_id=1132630021140402209&permissions=534995528784&scope=bot"
if __name__ == "__main__":
    client.run(Config.SECRET_TOKEN)