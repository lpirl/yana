import re
from os.path import isfile, isdir
import logging

from finders import AbstractBaseFinder

class FileSystemFinder(AbstractBaseFinder):
    """
    A finder that searches within the file system.
    """

    def _find_scandir(self, target_notes, match, notes_paths_q_put):
        """
        Search for matching files using the new and fast ``os.scandir``.
        Matching files will be submitted via ``notes_paths_q_put``.
        """
        from os import scandir
        logging.debug("using scandir")
        exclude = ('.', '..')
        for dir_path in target_notes:
            for dir_entry in scandir(dir_path):
                entry_name = dir_entry.name
                if not dir_entry.is_file():
                    continue
                if entry_name in exclude:
                    continue
                if not match(entry_name):
                    continue
                logging.info("found in file system: %s", dir_entry.path)
                notes_paths_q_put(dir_entry.path)

    def _find_walk(self, target_notes, match, notes_paths_q_put):
        """
        Search for matching files w/o new (and fast ``os.scandir``).
        Matching files will be submitted via ``notes_paths_q_put``.
        """
        logging.debug("using walk")
        from os import walk
        from os.path import join as path_join
        for dir_path in target_notes:
            for root, _, files in walk(dir_path):
                for file_path in files:
                    if match(file_path):
                        full_path = path_join(root, file_path)
                        logging.info("found in file system: %s", full_path)
                        notes_paths_q_put(full_path)


    def find(self, target_notes, _, notes_paths_q_put):
        """
        Search for matching files in the file system.
        """
        # TODO: spawn new process if crossing fs boundaries?

        # TODO: make this configurable:
        match = re.compile(r'.*\.note$').match

        dir_paths = []
        for path in target_notes:
            if isdir(path):
                dir_paths.append(path)
            elif isfile(path) and match(path):
                notes_paths_q_put(path)

        try:
            # cPython >= 3.5
            self._find_scandir(target_notes, match, notes_paths_q_put)
        except ImportError:
            # cPython < 3.5
            self._find_walk(target_notes, match, notes_paths_q_put)
