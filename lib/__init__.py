from os import mkdir
from os.path import isdir, join as path_join

from appdirs import user_cache_dir

QUEUE_END_SYMBOL = None

CACHE_DIR = path_join(user_cache_dir(), "yana")
if not isdir(CACHE_DIR):
    mkdir(CACHE_DIR)
