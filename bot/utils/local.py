
import os
import random


def random_local_asset(*dirs, basedir=["bot", "assets"]):   # might raise OSError if path fails
    dir = os.path.join(*basedir, *dirs)
    return os.path.join(*basedir, *dirs, random.choice(os.listdir(dir)))