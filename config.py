
import os


class Config:   # requires populating/"loading" environment variables before import
    SECRET_TOKEN = os.environ.get("TOKEN")


"""cli
pip install -U discord.py python-dotenv
"""

""".env
TOKEN=very_secret_token_here
"""