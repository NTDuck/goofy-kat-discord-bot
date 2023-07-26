
import os


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")
    MESSAGE_CONTENT = True

    COMMAND_PREFIX = "$"
    GAME_NAME = "goofy cats"


"""cli
pip install -U discord.py python-dotenv aiohttp
"""

""".env
TOKEN=very_secret_token_here
"""

"""current-target
- do the ping pong thing
- play music
- delete msg
- send nukes
"""

"""example-invite-link
https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=401616400070&scope=bot
"""