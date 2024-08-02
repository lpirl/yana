"""
Plugins that allow to listing notes and to address them during the next
run by their list index or by pattern-matching their paths.
"""

import logging
from fnmatch import filter as fnmatch_filter
from os import sep as pathsep, linesep, remove
from os.path import split as path_split, join as path_join, isfile
from json import dump, load
import abc

from lib import CACHE_DIR
from lib.printing import (print_colored, print_colored_2, print_default,
                          print_highlighted, print_path)
from plugins import Registry, AbstractBaseSubCommand, AbstractBaseFinder

LIST_CACHE_FILE = path_join(CACHE_DIR, "list_cache.json")


class BaseLastListingFinder(AbstractBaseFinder):
    """
    A common base class for finders that operate on last listed notes.

    This mainly deals with loading cached paths.
    """

    # disable check for not overridden abstract methods:
    #pylint: disable=W0223
    # since pylint does not detect this class being abstract itself correctly
    # (see http://stackoverflow.com/questions/22186843/
    #  pylint-w0223-method-is-abstract-in-class-but-is-not-overridden
    #  #comment33806701_22224042)
    __metaclass__ = abc.ABCMeta

    def set_up(self, *_):
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
        logging.debug("loaded %u paths from last listing", len(paths))
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
            try:
                index = int(query)
            except ValueError:
                return

            # abs() to allow use of negative indexing
            abs_index = abs(index)
            print(abs_index, len(self.last_listed_paths))
            if abs_index > 0 and abs_index <= len(self.last_listed_paths):

                # for positive numbers, make indexing start at 1
                if index > 0:
                    index -= 1

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
    """
    Lists notes found.
    Saves listed items to disk to be able to refer to them by indexes
    or by matching their paths (with separate finders, respectively).
    """

    sub_command = "list"
    sub_command_help = "lists notes"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-t', '--tags', action='store_true',
                                help='list tags as well', default=False)

        self.listed_paths = []
        self.invoked = False

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

        try:
            super(ListSubCommand, self).invoke(*args, **kwargs)
        except KeyboardInterrupt as exception:
            raise exception
        finally:
            self.save_listed_paths()

    def invoke_on_note(self, args, note):
        self.listed_paths.append(note.abspath)

        print_colored("%u " % len(self.listed_paths), True)
        print_path(note.path + linesep)

        if args.tags:
            tags = note.tags
            if tags:
                print_default("\n")
                for tag in tags:
                    print_colored_2("\t#%s\n" % tag)
                print_default("\n")
