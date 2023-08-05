
import os


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")
    APPLICATION_ID = os.environ.get("ID")

    INTENTS = {
        "MESSAGE_CONTENT": True,
        "TYPING": False,
        "VOICE_STATES": True,
        "PRESENCES": False,
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

    MAX_CLEAR_LIMIT = 100

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
pip install -U discord.py python-dotenv pynacl yt-dlp
be sure to install ffmpeg! just visit the official website/documentation.
pip freeze | % {pip uninstall -y $_.split('==')[0]}
"""

"""current-target
- play music (done)
"""

"""example-invite-link
https://discord.com/api/oauth2/authorize?client_id=1132630021140402209&permissions=40671229897536&scope=applications.commands%20bot
"""