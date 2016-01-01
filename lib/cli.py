# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from inspect import getmembers, isclass
from multiprocessing import Process, Queue
import re
from os import remove
from os.path import isfile, isdir, join as path_join
from json import dump, load
from fnmatch import filter as fnmatch_filter

from lib import QUEUE_END_SYMBOL, CACHE_DIR
from sub_commands import SUB_COMMAND_CLASSES
from finders import FINDER_CLASSES

# TODO: use https://pypi.python.org/pypi/ConfigArgParse

class Cli(object):

    LIST_CACHE_FILE = path_join(CACHE_DIR, "list_cache.json")

    def __init__(self):

        self._init_arg_parser()
        self._init_logging()
        self._init_sub_commands()

        self._parse_args()
        self._run()

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description="Even though this builds on what will persist " +
                        "(plaint text files and a file system) " +
                        "it is still only Yet Another Notes App.",
            epilog="Now you know.",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )

    def _parse_args(self):

        # display help per default:
        if len(argv) == 1:
            argv.append("-h")

        self.args = self.arg_parser.parse_args()

    def _init_logging(self):
        logging.getLogger().name = "yana"
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                            default=False, help='turn on debug messages')
        if '-d' in argv:
            logging.getLogger().setLevel(logging.DEBUG)

    def _init_sub_commands(self):
        """
        Initializes all sub commands (classes) from the module
        ``sub_commands``.
        """
        sub_parsers = self.arg_parser.add_subparsers(help="sub command",
                                                    dest='subcommand')

        logging.debug("found sub_commands: %s" % str(
            [s.__name__ for s in SUB_COMMAND_CLASSES]
        ))

        self.sub_commands = {}
        for cls in SUB_COMMAND_CLASSES:
            sub_parser = sub_parsers.add_parser(cls.sub_command,
                                                help=cls.sub_command_help)
            self.sub_commands[cls.sub_command] = cls(sub_parser)

            # add the path argument per default after all other arguments
            sub_parser.add_argument('note', type=str, nargs="*", default=".",
                                    help="target note (lookup order: " +
                                        "index from last run's notes, " +
                                        "glob match in last run's paths, " +
                                        "directory or file.")

    @classmethod
    def _find_notes_by_number_in_cache(cls, target_notes, cached_paths, q_put):
        """
        Finds recently found notes, referenced by a number.
        """
        logging.debug("finding by number in cache")
        cache_size = len(cached_paths)
        for target_note in target_notes:
            if target_note.isdigit():
                index = int(target_note) - 1
                if -1 < index and index < cache_size:
                    q_put(cached_paths[index])

    @classmethod
    def _find_notes_match_file_name_in_cache(cls, target_notes, cached_paths, q_put):
        """
        Finds recently found notes by matching the arguments with the
        cached file names.
        """
        logging.debug("finding by match in cache")
        for target_note in target_notes:
            for matched_path in fnmatch_filter(cached_paths, target_note):
                q_put(matched_path)

    @classmethod
    def _find_notes_in_file_system(cls, paths, q_put):
        """
        Finds notes in file system according to configured pattern.
        """
        # TODO: spawn new process if crossing fs boundaries?

        dir_paths = []
        for path in paths:
            if isfile(path):
                q_put(path)
            elif isdir(path):
              dir_paths.append(path)

        # TODO: make this configurable:
        match = re.compile('.*\.note$').match

        try:
            # cPython >= 3.5
            from os import scandir
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
                    q_put(entry_path)
        except ImportError:
            # cPython < 3.5
            from os import walk
            from os.path import join as path_join
            for dir_path in dir_paths:
                for root, _, files in walk(dir_path):
                    for file_path in files:
                        if match(file_path):
                            q_put(path_join(root, file_path))

    @classmethod
    def find_notes(cls, target_notes, notes_paths_q):
        """
        Finds all notes using all available lookups and puts them into
        the ``notes_paths_q``.
        """

        old_cache = []
        if isfile(cls.LIST_CACHE_FILE):
            with open(cls.LIST_CACHE_FILE, "r") as f:
                try:
                    old_cache = load(f)
                except ValueError:
                    remove(cls.LIST_CACHE_FILE)
            # TODO: cleanup cache

        new_cache = list()

        def q_deduping_and_caching_put(path):
            if path not in new_cache:
                new_cache.append(path)
                notes_paths_q.put(path)

        # TODO: parallelize?
        cls._find_notes_by_number_in_cache(target_notes, old_cache,
                                            q_deduping_and_caching_put)
        cls._find_notes_match_file_name_in_cache(target_notes, old_cache,
                                                    q_deduping_and_caching_put)
        cls._find_notes_in_file_system(target_notes, q_deduping_and_caching_put)

        notes_paths_q.put(QUEUE_END_SYMBOL)

        if not new_cache:
            logging.error("Could not find any note. Maybe try 'list' again.")

        with open(cls.LIST_CACHE_FILE, "w") as f:
            dump(new_cache, f)

    def _run(self):
        """
        TODO docsting
        """
        args = self.args
        notes_paths_q = Queue(False)
        find_process = Process(target=self.find_notes,
                                args=(args.note, notes_paths_q))
        find_process.start()

        sub_command = self.sub_commands[args.subcommand]
        logging.debug("running sub command: '%s'" % sub_command.__class__.__name__)
        sub_command.invoke(args, notes_paths_q.get)

        find_process.join()
