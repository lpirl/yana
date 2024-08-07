"""
Implements plugins to find notes in the file system.
"""


import re
from os import walk
from os.path import isfile, isdir, join as path_join
import logging

from plugins import Registry, AbstractBaseFinder

@Registry.register_finder
class FileSystemFinder(AbstractBaseFinder):
    """
    A finder that searches recursively within the file system.
    """

    finds = "recursively in the file system"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-n', '--new', action='store_true',
                                default=False, help='ignore non-existing ' +
                                'notes / allow new notes to be created')
        arg_parser.add_argument('--note-regex', default=r'(.*\.)?notes?$',
                                help='regular expression used to identify ' +
                                'notes paths')

    @staticmethod
    def _find_scandir(dir_paths, match, found_path_callback):
        """
        Search for matching files using the new and fast ``os.scandir``.
        Matching files will be submitted via ``found_path_callback``.
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
                found_path_callback(dir_entry.path)

    @staticmethod
    def _find_walk(dir_paths, match, found_path_callback):
        """
        Search for matching files w/o new (and fast ``os.scandir``).
        Matching files will be submitted via ``found_path_callback``.
        """



    def find(self, args, queries, found_path_callback):
        """
        Search for matching files in the file system.
        """
        # IDEA: spawn new process/thread if crossing fs boundaries?

        match = re.compile(args.note_regex).match

        dir_paths = []
        for query in queries:
            if isdir(query):
                dir_paths.append(query)
            elif (isfile(query) or args.new) and match(query):
                found_path_callback(query)

        logging.debug("walking file system")
        for dir_path in dir_paths:
            for root, _, files in walk(dir_path):
                for file_path in files:
                    if match(file_path):
                        full_path = path_join(root, file_path)
                        logging.info("found in file system: %s", full_path)
                        found_path_callback(full_path)
