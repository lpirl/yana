"""
Contains the main CLI application.
It contains also the most top-level coordination of the program.
"""

# encoding: UTF-8
from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from multiprocessing import Process, Queue
from os import remove
from os.path import isfile, join as path_join
from json import dump, load
from signal import signal, SIGTERM

from lib import QUEUE_END_SYMBOL, CACHE_DIR
from plugins import Registry
from lib.printing import print_default

class Cli(object):

    LIST_CACHE_FILE = path_join(CACHE_DIR, "list_cache.json")


    def __init__(self):
        """
        Finds/loads/initializes everything needed for operation.
        """

        self._init_arg_parser()
        self._init_logging()
        self._init_finders()
        self._init_sub_commands()
        self.args = None
        self.old_cache = None
        self.new_cache = None

    def handle_args(self):
        """
        This kicks off the actual operation (i.e. use the users' args,
        options and sub commands to server the request).
        """
        self._parse_args()
        args = self.args

        notes_paths_q = Queue(False)

        find_process = Process(target=self._find_notes,
                               args=(args.note, notes_paths_q.put))
        find_process.start()

        sub_command = self.sub_commands[args.subcommand]
        logging.debug("running sub command: '%s'", sub_command.__class__.__name__)

        try:
            sub_command.invoke(args, notes_paths_q.get)
        except KeyboardInterrupt:
            find_process.terminate()
            print_default("\n")
        finally:
            find_process.join()

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description="Yet Another Notes App - but this one builds " +
            "on what will persist (plaint text files and a file system).",
            epilog="Now you know.",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )

    def _parse_args(self):

        # display help per default:
        if len(argv) == 1:
            argv.append("-h")

        args = self.arg_parser.parse_args()
        self.args = args

        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)

    def _init_logging(self):
        logging.getLogger().name = "yana"
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                                     default=False, help='turn on debug messages')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     default=False, help='turn on verbose messages')
        if '-d' in argv:
            logging.getLogger().setLevel(logging.DEBUG)

    def _init_sub_commands(self):
        """
        Initializes all sub command classes from the corresponding module.
        """
        sub_parsers = self.arg_parser.add_subparsers(help="sub command",
                                                     dest='subcommand')

        assert self.finders, "finders must be initialized first"
        finding_help = ', '.join((f.finds for f in self.finders))

        self.sub_commands = {}
        for cls in Registry.sub_commands:
            logging.debug("initializing sub command: %s", cls.__name__)

            sub_parser = sub_parsers.add_parser(cls.sub_command,
                                                help=cls.sub_command_help)
            self.sub_commands[cls.sub_command] = cls(sub_parser)

            # add the path argument per default after all other arguments
            sub_parser.add_argument('note', type=str, nargs="*", default=".",
                                    help="target note (strategies: %s)." %
                                    finding_help)

    def _init_finders(self):
        """
        Initializes all finder classes from the corresponding module.
        """
        self.finders = []
        for cls in Registry.finders:
            logging.debug("initializing finder: %s", cls.__name__)
            self.finders.append(cls(self.arg_parser))

    def load_cached_paths(self):
        """
        Loads cached paths.
        """
        file_name = self.LIST_CACHE_FILE
        paths = []
        if isfile(file_name):
            with open(file_name, "r") as cache_file:
                try:
                    paths = load(cache_file) or []
                except ValueError:
                    remove(file_name)
                else:
                    paths = [p for p in paths if isfile(p)]
        self.old_cache = paths
        self.new_cache = []

    def save_cached_paths(self, *args):
        """
        Saves cached paths.

        This method is required to function as a ``os.signal`` handler.
        """
        with open(self.LIST_CACHE_FILE, "w") as cache_file:
            dump(self.new_cache, cache_file)
        self.new_cache = None

    def _find_notes(self, target_notes, notes_paths_q_put):
        """
        Finds all notes using all available lookups and puts them into
        the ``notes_paths_q``.
        """

        def deduping_and_caching_q_put(path):
            if path not in self.new_cache:
                self.new_cache.append(path)
                notes_paths_q_put(path)

        # make cache to be saved when (probably) interrupt by user occurs
        signal(SIGTERM, self.save_cached_paths)

        self.load_cached_paths()

        try:
            for finder in self.finders:
                logging.debug("running finder: %s", finder.__class__.__name__)
                finder.find(self.args, target_notes, self.old_cache,
                            deduping_and_caching_q_put)
        except KeyboardInterrupt:
            pass
        else:
            if not self.new_cache:
                logging.error(
                    "Could not find any note. Maybe try 'list' again."
                )
            self.save_cached_paths()
        notes_paths_q_put(QUEUE_END_SYMBOL)
