
import os
from redis import UsernamePasswordCredentialProvider


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")
    APPLICATION_ID = int(os.environ.get("ID"))
    UID = int(os.environ.get("UID"))

    INTENTS = {
        "GUILDS": True,
        "GUILD_SCHEDULED_EVENTS": True,
        "MEMBERS": True,
        "MESSAGE_CONTENT": True,
        "MESSAGES": True,
        "MODERATION": False,
        "PRESENCES": True,
        "TYPING": True,
        "VOICE_STATES": True,
    }

    LOGGING_CONFIG = {
        "filename": "discord.log",
        "encoding": "utf-8",
        "mode": "w",
    }

    REDIS_CONFIG = {
        "host": os.environ.get("REDIS_HOST"),
        "port": os.environ.get("REDIS_PORT", 15688),
        "credential_provider": UsernamePasswordCredentialProvider(os.environ.get("REDIS_USERNAME", "default"), os.environ.get("REDIS_PASSWORD"))
    }

    # https://pypi.org/project/yt-dlp/
    # if only this was well documented ...
    YT_DLP_OPTIONS = {
        "format": "m4a/worstaudio",
        "hls-use-mpegts": True,
        "quiet": True,
        "extractaudio": False,
        "source_address": "0.0.0.0",   # bind to ipv4 -> more stable?
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "60",
        }],
    }

    ENCODING = {
        "a1z26": {
            "char_sep": "-",
            "word_sep": " ",
        },
        "morse": {
            "dit": ".",
            "dah": "-",
            "char_sep": " ",
            "word_sep": " / ",
            "null_repr": "#",   # invalid/untranslatable morse code
        }
    }

    MAX_CLEAR_LIMIT = 100
    MAX_AUDIO_QUEUE_LIMIT = 50

    COMMAND_PREFIX = "$"
    GAME_NAME = "goofy cats"

    API = {
        "cat": {
            "thecatapi": {   # https://developers.thecatapi.com/
                "url": "https://api.thecatapi.com/v1/images/search",
                "headers": {"x-api-key": os.environ.get("API_KEY_THECATAPI")},
                "params": {"limit": 1},
            },
            "cataas": {   # https://cataas.com/doc.html
                "url": "https://cataas.com/c",
            },
            # hey https://http.cat/ is actually a very good one
            "shibe": {
                "url": "https://shibe.online/api/cats",   # also works with /api/shibes or /api/birds
                "params": {"count": 1},
            },
        }
        # more lookout here: https://api.publicapis.org/entries, past animals
    }


"""cli
pip install -U discord.py python-dotenv pynacl yt-dlp redis[hiredis]
be sure to install ffmpeg! just visit the official website/documentation.
pip freeze | % {pip uninstall -y $_.split('==')[0]}
"""

"""cli
wsl
redis-server   # optional
redis-cli
---
redis-cli shutdown
exit
"""

"""current-target
- set up logging
- help command (nah)
- server stats thingy
- en/de-coder
"""

"""example-invite-link
https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=40671229897536&scope=applications.commands%20bot
"""