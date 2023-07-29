
import os


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")
    APPLICATION_ID = os.environ.get("ID")
    MESSAGE_CONTENT = True
    TYPING = False
    PRESENCES = False

    COMMAND_PREFIX = "$"
    GAME_NAME = "goofy cats"

    API = {
        "https://thecatapi.com/": {   # https://developers.thecatapi.com/
            "url": "https://api.thecatapi.com/v1/images/search",
            "headers": {"x-api-key": os.environ.get("THECATAPI_API_KEY")},
            "params": {"limit": 1},
        },
    }


"""cli
pip install -U discord.py python-dotenv
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
https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=40671229897536&scope=applications.commands%20bot
"""