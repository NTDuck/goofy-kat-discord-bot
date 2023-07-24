
import os


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")
    MESSAGE_CONTENT = True
    COMMAND_PREFIX = "$"


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
https://discord.com/oauth2/authorize?client_id=1132630021140402209&permissions=534995528784&scope=bot
"""