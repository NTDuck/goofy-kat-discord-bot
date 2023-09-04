
import logging
import logging.config
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue


# https://docs.python.org/3/howto/logging.html#optimization
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False

log_queue = Queue(maxsize=-1)   # no queue size limit
queue_handler = QueueHandler(log_queue)

# handlers - logging level set immediately after instantiation
terminal_handler = logging.StreamHandler()
terminal_handler.setLevel(logging.INFO)

# logs/ should not exceed 1GB
file_handler = RotatingFileHandler(
    filename="logs/app.log",
    mode="a",
    encoding="utf-8",
    maxBytes=1e8,
    backupCount=10,
)
file_handler.setLevel(logging.DEBUG)

# discord_file_handler = logging.FileHandler(
#     filename="logs/dump.log",
#     mode="a",
#     encoding="utf-8",
# )
# discord_file_handler.setLevel(logging.DEBUG)

# listener - can accept multiple QueueHandler instances
queue_listener = QueueListener(log_queue, terminal_handler, file_handler)

# base logger - not root to avoid default discord.py dumps
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(queue_handler)

formatter = logging.Formatter(
    fmt="[%(asctime)s] - %(levelname)s (%(name)s) - %(message)s",   # https://docs.python.org/3/library/logging.html#logrecord-attributes
    datefmt="%Y/%m/%d %H:%M:%S",   # https://docs.python.org/3/library/time.html#time.strftime
)
terminal_handler.setFormatter(formatter)

debug_formatter = logging.Formatter(
    fmt='[%(asctime)s] - %(levelname)s (%(name)s) - "%(pathname)s", line %(lineno)d, in <%(module)s> - %(message)s',
    datefmt="%Y/%m/%d %H:%M:%S",
)
file_handler.setFormatter(debug_formatter)