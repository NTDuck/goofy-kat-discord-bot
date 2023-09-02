
# from collections.abc import Mapping
# from typing import Any, Optional
# import logging


# class CustomLoggingFormatter(logging.Formatter):
#     def __init__(self, style="%", validate: bool = True, *, defaults: Optional[Mapping[str, Any]] = None):
#         fmt = '%(levelname)s [%(asctime)s] "%(pathname)s", line %(lineno)d, in <%(module)s> :: %(message)s'   # https://docs.python.org/3/library/logging.html#logrecord-attributes
#         datefmt = "%m/%d/%Y %H:%M:%S"   # https://docs.python.org/3/library/time.html#time.strftime
#         super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults)


# class CustomLoggingHandler(logging.FileHandler):
#     def __init__(self, mode: str = "a", delay: bool = False, errors: Optional[str] = None):
#         filename = "discord.log"
#         encoding = "utf-8"
#         super().__init__(filename=filename, mode=mode, delay=delay, encoding=encoding, errors=errors)


# # okay here's the logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # https://docs.python.org/3/howto/logging.html#optimization
# logging.logThreads = False
# logging.logProcesses = False
# logging.logMultiprocessing = False

# # don't know why but here's a handler
# ch = CustomLoggingHandler()
# ch.setLevel(logging.DEBUG)

# # the very comprehensible formatter
# formatter = CustomLoggingFormatter()
# ch.setFormatter(formatter)

# logger.addHandler(ch)


import logging
import logging.config


logging.config.fileConfig("logging.conf")

# https://docs.python.org/3/howto/logging.html#optimization
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False

root_logger = logging.getLogger()   # root