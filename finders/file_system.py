import re
from os.path import isfile, isdir
import logging

from finders import AbstractBaseFinder

class FileSystemFinder(AbstractBaseFinder):
    """
    A finder that searches within the file system.
    """

    def find(self, target_notes, _, notes_paths_q_put):
                # TODO: spawn new process if crossing fs boundaries?

        # TODO: make this configurable:
        match = re.compile('.*\.note$').match

        dir_paths = []
        for path in target_notes:
            if isdir(path):
              dir_paths.append(path)
            elif isfile(path) and match(path):
                notes_paths_q_put(path)

        try:
            # cPython >= 3.5
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
                    logging.debug("found in file system: %s" % entry_path)
                    notes_paths_q_put(entry_path)
        except ImportError:
            # cPython < 3.5
            from os import walk
            from os.path import join as path_join
            for dir_path in target_notes:
                for root, _, files in walk(dir_path):
                    for file_path in files:
                        if match(file_path):
                            full_path = path_join(root, file_path)
                            logging.debug("found in file system: %s" % full_path)
                            notes_paths_q_put(full_path)
