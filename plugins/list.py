"""
Plugins that allow to listing notes and to address them during the next
run by their list index or by pattern-matching their paths.
"""

import logging
from fnmatch import filter as fnmatch_filter
from os import sep as pathsep, linesep, remove
from os.path import split as path_split, join as path_join, isfile
from json import dump, load

from lib import CACHE_DIR
from plugins import Registry, AbstractBaseSubCommand, AbstractBaseFinder
from lib.printing import print_colored, print_default, print_highlighted

LIST_CACHE_FILE = path_join(CACHE_DIR, "list_cache.json")

class BaseLastListingFinder(AbstractBaseFinder):
    """
    A common base class for finders that operate on last listed notes.

    This mainly deals with loading cached paths.
    """

    def set_up(self, *args):
        self.load_last_listed_paths()

    def load_last_listed_paths(self):
        """
        Loads paths that were found last time using the list sub command.
        """
        file_name = LIST_CACHE_FILE
        paths = []
        if isfile(file_name):
            with open(file_name, "r") as cache_file:
                try:
                    paths = load(cache_file) or []
                except ValueError:
                    remove(file_name)
                else:
                    paths = [p for p in paths if isfile(p)]
        logging.debug("loaded %u oaths from last listing" % len(paths))
        self.last_listed_paths = paths

@Registry.register_finder
class LastListingIndexFinder(BaseLastListingFinder):
    """
    A finder that tries to return paths from the last listing addressed
    by possibly user-provided indexes.
    """
    finds = "last listed by index"

    def find(self, args, queries, found_path_callback):
        """
        Returns all paths that were listed last time and that are
        specified as index in ``queries``.
        """

        for query in queries:
            if query.isdigit():
                index = int(query) - 1
                if -1 < index and index < len(self.last_listed_paths):
                    path = self.last_listed_paths[index]
                    logging.info("found by index in cache: %s", path)
                    found_path_callback(path)

@Registry.register_finder
class LastListingRunMatchFinder(BaseLastListingFinder):
    """
    A finder that tries to return paths from the last listing matching
    possibly user-provided patterns.
    """

    finds = "last listed by pattern-matching paths"

    def find(self, args, queries, found_path_callback):
        """
        Returns all paths that were listed last time and that match
        patterns specified in ``queries``.
        """

        for query in queries:
            for matched_path in fnmatch_filter(self.last_listed_paths, query):
                logging.info("found by match in cache: %s", matched_path)
                found_path_callback(matched_path)

@Registry.register_sub_command
class ListSubCommand(AbstractBaseSubCommand):

    sub_command = "list"
    sub_command_help = "lists notes"

    def set_up(self, _):
        self.listed_paths = []
        self.invoked = False

    def tear_down(self):
        self.save_listed_paths()

    def save_listed_paths(self):
        """
        Saves listed paths.
        """
        if not self.invoked:
            return
        with open(LIST_CACHE_FILE, "w") as cache_file:
            dump(self.listed_paths, cache_file)

    def invoke(self, *args, **kwargs):
        """
        Sets a flag that this sub command was invoked.
        That way, ``save_listed_paths`` can decide if it should operate.
        """
        self.invoked = True
        super(ListSubCommand, self).invoke(*args, **kwargs)

    def invoke_on_note(self, args, note):
        self.listed_paths.append(note.abspath)
        print_colored("%u " % len(self.listed_paths), True)
        pathname, filename = path_split(note.path)
        print_default("%s%s" % (pathname, pathsep))
        print_highlighted("%s%s" % (filename, linesep))
