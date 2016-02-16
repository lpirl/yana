"""
A module for plugins that use that last runs' paths.
"""

import logging
from fnmatch import filter as fnmatch_filter

from plugins import Registry, AbstractBaseFinder

@Registry.register_finder
class LastRunIndexFinder(AbstractBaseFinder):
    """
    A finder that returns paths from the last run addressed by their index.
    """

    finds = "listed during last run by their index"

    def find(self, args, target_notes, previous_path, notes_paths_q_put):
        """
        Returns the all (existing) ``previous_path`` that are possibly
        specified in ``target_notes``.
        """
        cache_size = len(previous_path)
        for target_note in target_notes:
            if target_note.isdigit():
                index = int(target_note) - 1
                if -1 < index and index < cache_size:
                    path = previous_path[index]
                    logging.info("found by index in cache: %s", path)
                    notes_paths_q_put(path)


@Registry.register_finder
class LastRunMatchFinder(AbstractBaseFinder):
    """
    A finder that returns paths from the last run that match a (possibly)
    user-provided pattern.
    """

    finds = "listed during last run by matching paths"

    def find(self, args, target_notes, previous_path, notes_paths_q_put):
        for target_note in target_notes:
            for matched_path in fnmatch_filter(previous_path, target_note):
                logging.info("found by match in cache: %s", matched_path)
                notes_paths_q_put(matched_path)
