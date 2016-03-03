"""
Contains the main CLI application.
It contains also the most top-level coordination of the program.
"""

# encoding: UTF-8
from sys import argv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from multiprocessing import Process, Queue

from plugins import Registry
from lib import QUEUE_END_SYMBOL
from lib.printing import print_default
from lib.note import Note

class Cli(object):
    """
    Implements most top-level coordination and interaction as CLI.

    After initialization, all you need is ``handle_args()``.
    """

    def __init__(self):
        """
        Finds/loads/initializes everything needed for operation.
        """

        self._init_arg_parser()
        self._init_logging()
        self._init_note_class()
        self._init_and_set_up_finders()
        self._init_and_set_up_sub_commands()
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

        Note.set_args(args)

        notes_q = Queue(False)

        find_process = Process(target=self._find_notes,
                               args=(args.query, notes_q.put))
        find_process.start()

        sub_command = self.sub_commands[args.subcommand]
        logging.debug("running sub command: '%s'", sub_command.__class__.__name__)

        try:
            sub_command.invoke(args, notes_q.get)
        except KeyboardInterrupt:
            find_process.terminate()
            print_default("\n")
        finally:
            find_process.join()

    def _init_arg_parser(self):
        self.arg_parser = ArgumentParser(
            description="Yet Another Notes App - this one builds " +
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

    def _init_note_class(self):
        Note.set_parser(self.arg_parser)

    def _init_and_set_up_sub_commands(self):
        """
        Initializes and sets up all sub command classes from the
        corresponding module.
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
            sub_command = cls()
            sub_command.set_up(sub_parser)
            self.sub_commands[cls.sub_command] = sub_command

            # add the path argument per default after all other arguments
            sub_parser.add_argument('query', type=str, nargs="*", default=".",
                                    help="a query for notes (searches: %s)." %
                                    finding_help)

    def _init_and_set_up_finders(self):
        """
        Initializes and sets up all finder classes from the
        corresponding module.
        """
        self.finders = []
        for cls in Registry.finders:
            logging.debug("initializing and setting up finder: %s", cls.__name__)
            finder = cls()
            finder.set_up(self.arg_parser)
            self.finders.append(finder)

    def _find_notes(self, queries, notes_q_put):
        """
        Collects paths to notes from finders and submits them as
        ``Note``s via ``notes_q_put`` to the corresponding sub command.
        """

        def found_path_callback(path):
            """
            Initializes ``Note` `from found ``path`` and puts it
            into the notes queue.

            This function can easily feature deduplication (and actually
            did) but I am not quite sure if this is actually desired.
            """
            notes_q_put(Note(path))

        try:
            for finder in self.finders:
                logging.debug("running finder: %s", finder.__class__.__name__)
                finder.find(self.args, queries, found_path_callback)
        except KeyboardInterrupt:
            pass

        notes_q_put(QUEUE_END_SYMBOL)
