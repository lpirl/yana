# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from multiprocessing import Process, Queue
from os import remove
from os.path import isfile, join as path_join
from json import dump, load

from lib import QUEUE_END_SYMBOL, CACHE_DIR
from sub_commands import SUB_COMMAND_CLASSES
from finders import FINDER_CLASSES

# TODO: use https://pypi.python.org/pypi/ConfigArgParse

class Cli(object):

    def __init__(self):

        self._init_arg_parser()
        self._init_logging()
        self._init_finders()
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
        Initializes all sub command classes from the corresponding module.
        """
        sub_parsers = self.arg_parser.add_subparsers(help="sub command",
                                                    dest='subcommand')


        self.sub_commands = {}
        for cls in SUB_COMMAND_CLASSES:
            logging.debug("initializing sub command: %s" % cls.__name__)

            sub_parser = sub_parsers.add_parser(cls.sub_command,
                                                help=cls.sub_command_help)
            self.sub_commands[cls.sub_command] = cls(sub_parser)

            # add the path argument per default after all other arguments
            sub_parser.add_argument('note', type=str, nargs="*", default=".",
                                    help="target note (lookup order: " +
                                        "index from last run's notes, " +
                                        "glob match in last run's paths, " +
                                        "directory or file.")

    def _init_finders(self):
        """
        Initializes all finder classes from the corresponding module.
        """
        self.finders = []
        for cls in FINDER_CLASSES:
            logging.debug("initializing finder: %s" % cls.__name__)
            self.finders.append(cls(self.arg_parser))

    def find_notes(self, target_notes, notes_paths_q):
        """
        Finds all notes using all available lookups and puts them into
        the ``notes_paths_q``.
        """
        LIST_CACHE_FILE = path_join(CACHE_DIR, "list_cache.json")

        old_cache = []
        if isfile(LIST_CACHE_FILE):
            with open(LIST_CACHE_FILE, "r") as f:
                try:
                    old_cache = load(f)
                except ValueError:
                    remove(LIST_CACHE_FILE)
            # TODO: cleanup cache

        new_cache = list()

        def deduping_and_caching_q_put(path):
            if path not in new_cache:
                new_cache.append(path)
                notes_paths_q.put(path)

        for finder in self.finders:
            logging.debug("running finder: %s" % finder.__class__.__name__)
            finder.find(target_notes, old_cache, deduping_and_caching_q_put)

        notes_paths_q.put(QUEUE_END_SYMBOL)

        if not new_cache:
            logging.error("Could not find any note. Maybe try 'list' again.")

        with open(LIST_CACHE_FILE, "w") as f:
            dump(new_cache, f)

    def _run(self):
        """
        TODO
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
