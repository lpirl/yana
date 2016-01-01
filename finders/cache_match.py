"""
A module for finders that use (possibly) provided patterns to find
notes in the cache.
"""

import logging
from fnmatch import filter as fnmatch_filter

from finders import AbstractBaseFinder

class CacheIndexFinder(AbstractBaseFinder):
    """
    A finder that returns items from the cache that match the
    user-provided pattern.
    """

    def find(self, target_notes, cached_paths, notes_paths_q_put):
        for target_note in target_notes:
            for matched_path in fnmatch_filter(cached_paths, target_note):
                logging.debug("found by match in cache: %s", matched_path)
                notes_paths_q_put(matched_path)
