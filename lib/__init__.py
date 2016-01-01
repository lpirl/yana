"""
This module provides the core functionalities.

It provides interfaces to the user (i.e. CLI at the moment), glues
everything together and orchestrates execution.
"""

from os import mkdir
from os.path import isdir, join as path_join

from appdirs import user_cache_dir

QUEUE_END_SYMBOL = None

CACHE_DIR = path_join(user_cache_dir(), "yana")
if not isdir(CACHE_DIR):
    mkdir(CACHE_DIR)
