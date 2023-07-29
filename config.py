
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
            "headers": {"x-api-key": os.environ.get("API_KEY_THECATAPI")},
            "params": {"limit": 1},
        },
        "https://cataas.com/": {   # https://cataas.com/doc.html
            "url": "https://cataas.com/c",
        },
        # hey https://http.cat/ is actually a very good one
        "https://shibe.online/": {
            "url": "https://shibe.online/api/cats",   # also works with /api/shibes or /api/birds
            "params": {"count": 1},
        }
        # more lookout here: https://api.publicapis.org/entries, past animals
    }


"""cli
pip install -U discord.py python-dotenv
"""

"""current-target
- play music
"""

"""example-invite-link
https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=40671229897536&scope=applications.commands%20bot
"""