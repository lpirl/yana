"""
A module for finders that use cached paths and (possibly) provided cache
indexes.
"""

import logging

from finders import AbstractBaseFinder

class CacheIndexFinder(AbstractBaseFinder):
    """
    A finder that returns items from the cache, addressed by their index.
    """

    def find(self, target_notes, cached_paths, notes_paths_q_put):
        """
        Returns the all (existing) ``cached_paths`` that are possibly
        specified in ``target_notes``.
        """
        cache_size = len(cached_paths)
        for target_note in target_notes:
            if target_note.isdigit():
                index = int(target_note) - 1
                if -1 < index and index < cache_size:
                    path = cached_paths[index]
                    logging.debug("found by index in cache: %s", path)
                    notes_paths_q_put(path)
