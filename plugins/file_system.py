import re
from os.path import isfile, isdir
import logging

from plugins import Registry, AbstractBaseFinder

@Registry.register_finder
class FileSystemFinder(AbstractBaseFinder):
    """
    A finder that searches within the file system.
    """

    finds = "recursively in the file system"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-n', '--new', action='store_true',
                                default=False, help='ignore non-existing ' +
                                'notes / allow new notes to be created')
        arg_parser.add_argument('-m', '--match', default=r'.*\.note$',
                                help='regular expression used to identify ' +
                                'notes paths')

    def _find_scandir(self, args, dir_paths, match, notes_paths_q_put):
        """
        Search for matching files using the new and fast ``os.scandir``.
        Matching files will be submitted via ``notes_paths_q_put``.
        """
        from os import scandir
        logging.debug("using scandir")
        exclude = ('.', '..')
        for dir_path in dir_paths:
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

    def _find_walk(self, args, dir_paths, match, notes_paths_q_put):
        """
        Search for matching files w/o new (and fast ``os.scandir``).
        Matching files will be submitted via ``notes_paths_q_put``.
        """
        logging.debug("using walk")
        from os import walk
        from os.path import join as path_join
        for dir_path in dir_paths:
            for root, _, files in walk(dir_path):
                for file_path in files:
                    if match(file_path):
                        full_path = path_join(root, file_path)
                        logging.info("found in file system: %s", full_path)
                        notes_paths_q_put(full_path)


    def find(self, args, queries, notes_paths_q_put):
        """
        Search for matching files in the file system.
        """
        # IDEA: spawn new process/thread if crossing fs boundaries?

        match = re.compile(args.match).match

        dir_paths = []
        for query in queries:
            if isdir(query):
                dir_paths.append(query)
            elif (isfile(query) or args.new) and match(query):
                notes_paths_q_put(query)

        try:
            # cPython >= 3.5
            self._find_scandir(args, dir_paths, match, notes_paths_q_put)
        except ImportError:
            # cPython < 3.5
            self._find_walk(args, dir_paths, match, notes_paths_q_put)
