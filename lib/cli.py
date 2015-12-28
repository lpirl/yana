# encoding: UTF-8

from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from inspect import getmembers, isclass
from multiprocessing import Process, Queue
import re

from lib import QUEUE_END_SYMBOL

# TODO: use https://pypi.python.org/pypi/ConfigArgParse

class Cli(object):

    def __init__(self):

        self._init_arg_parser()
        self._init_logging()
        self._init_plugins()

        self._parse_args()
        self._run()

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description="This is Yet Another Notes App.",
            formatter_class=ArgumentDefaultsHelpFormatter
        )

    def _parse_args(self):

        # display help per default:
        if len(argv) == 1:
            argv.append("-h")

        self.args = self.arg_parser.parse_args()

    def _init_logging(self):
        logging.getLogger().name = "yana"
        self.arg_parser.add_argument('-d', '--debug', action='store_true',
                            default=False, help='Turn on debug messages?')
        if '-d' in argv:
            logging.getLogger().setLevel(logging.DEBUG)

    def _init_plugins(self):
        """
        Acquires and initializes all plugins (classes) in the module
        ``plugins``.
        """

        # we scope this import into this function so that plugins can
        # import this module
        import plugins as plugins_module

        sub_parsers = self.arg_parser.add_subparsers(help="sub command",
                                                    dest='subcommand')

        plugin_classes = [t[1] for t in
                            getmembers(plugins_module, isclass)
                            if not t[0].startswith("Abstract")]
        logging.debug("found plugins: %s" % str(
            [s.__name__ for s in plugin_classes]
        ))

        self.plugins = {}
        for cls in plugin_classes:
            sub_parser = sub_parsers.add_parser(cls.sub_command,
                                                help=cls.sub_command_help)
            self.plugins[cls.sub_command] = cls(sub_parser)

            # add the path argument per default after all other arguments
            sub_parser.add_argument('path', type=str, nargs="*", default=".",
                                    help='Directory or file to operate on.')

    @classmethod
    def find_notes(cls, paths, notes_paths_q):
        """
        Finds all notes under ``path`` and puts them into the
        ``notes_paths_q``.
        """
        # TODO: spawn new process if crossing fs boundaries?

        put = notes_paths_q.put

        # TODO: make this configurable:
        match = re.compile('.*\.note$').match

        try:
            # cPython >= 3.5
            from os import scandir
            exclude = ('.', '..')
            for path in paths:
                for dir_entry in scandir(path):
                    entry_name = dir_entry.name
                    if not dir_entry.is_file():
                        continue
                    if entry_name in exclude:
                        continue
                    if not match(entry_name):
                        continue
                    put(entry_path)
        except ImportError:
            # cPython < 3.5
            from os import walk
            from os.path import join as path_join
            for path in paths:
                for root, _, files in walk(path):
                    for file_path in files:
                        if match(file_path):
                            put(path_join(root, file_path))
        finally:
            put(QUEUE_END_SYMBOL)

    def _run(self):
        """
        TODO docsting
        """
        args = self.args
        notes_paths_q = Queue(False)
        find_process = Process(target=self.find_notes,
                                args=(args.path, notes_paths_q))
        find_process.start()

        plugin = self.plugins[args.subcommand]
        logging.debug("running plugin: '%s'" % plugin.__class__.__name__)
        plugin.run(args, notes_paths_q)

        find_process.join()
