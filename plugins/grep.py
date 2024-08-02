"""
Implements plugins to search for contents in notes.
"""

import re

from plugins import Registry, AbstractBaseSubCommand

from lib import QUEUE_END_SYMBOL
from lib.printing import print_default, print_path, print_highlight

@Registry.register_sub_command
class GrepCommand(AbstractBaseSubCommand):
    """
    A sub command that searches for contents in notes.
    """

    sub_command = "grep"
    sub_command_help = "search for contents in notes"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-c', '--case', action='store_true',
                                default=False, help='case-sensitive')
        arg_parser.add_argument('-e', '--regex', action='store_true',
                                help=('treat pattern as regular '
                                      'expression'))
        arg_parser.add_argument('pattern', help='pattern to search for')

    def invoke(self, args, note_q_get):
        """
        Prints lines matching the search string in all notes.
        """
        for note in set(iter(note_q_get, QUEUE_END_SYMBOL)):
            self.invoke_on_note(args, note)

    def invoke_on_note(self, args, note):
        """
        Prints lines matching the search string.
        """

        if args.regex:
            pattern = args.pattern
        else:
            pattern = re.escape(args.pattern)

        if args.case:
            flags = re.NOFLAG
        else:
            flags = re.IGNORECASE

        reo = re.compile(pattern, flags)

        for line in note.lines:
            last_pos_printed = None
            for match in reo.finditer(line):
                if not last_pos_printed:
                    print_path(note.path + ": ")
                print_default(line[last_pos_printed:match.start()])
                print_highlight(line[match.start():match.end()])
                last_pos_printed = match.end()
            if last_pos_printed:
                print_default(line[last_pos_printed:])
