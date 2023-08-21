
# visit /bot/cogs/__init__.py if any changes occur
from discord import app_commands


class Unauthorized(app_commands.CheckFailure):
    pass

class VoiceClientNotFound(app_commands.CheckFailure):
    pass

class BotVoiceClientNotFound(app_commands.CheckFailure):
    pass

class BotVoiceClientAlreadyConnected(app_commands.CheckFailure):
    pass

class BotVoiceClientAlreadyPaused(app_commands.CheckFailure):
    pass

class BotVoiceClientAlreadyPlaying(app_commands.CheckFailure):
    pass

class BotVoiceClientIsolation(app_commands.CheckFailure):
    pass

class BotVoiceClientQueueEmpty(app_commands.CheckFailure):
    pass

class KeywordNotFound(app_commands.CheckFailure):
    pass