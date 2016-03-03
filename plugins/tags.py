"""
Implements plugins to view tags of notes.
"""

from plugins import Registry, AbstractBaseSubCommand

from lib import QUEUE_END_SYMBOL
from lib.printing import print_colored_2, print_default

@Registry.register_sub_command
class TagsSubCommand(AbstractBaseSubCommand):
    """
    A sub command that displays tags and optionally the notes where they
    can be found in.
    """

    sub_command = "tags"
    sub_command_help = "show used tags for notes"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-s', '--sort', action='store_true',
                                default=False, help='sort output')
        arg_parser.add_argument('-n', '--notes', action='store_true',
                                default=False, help='show notes ' +
                                'containing the corresponding tag')

    def invoke(self, args, note_q_get):
        """
        If neither sorting, nor the notes are requested, this method
        hands off the work to ``invoke_on_note``.

        All other cases are handled within this method.
        """

        # we cover the easiest "default" approach with this guard clause:
        if not args.notes and not args.sort:
            self._printed_tags = set()
            super(TagsSubCommand, self).invoke(args, note_q_get)
            return

        # collect all tags and if required all corresponding notes
        tags_and_notes = {}
        for note in set(iter(note_q_get, QUEUE_END_SYMBOL)):
            for tag in note.tags:
                notes = tags_and_notes.setdefault(tag, set())
                if args.notes:
                    notes.add(note)

        # sort the tags if need be
        tags = tags_and_notes.keys()
        if args.sort:
            tags.sort(key=lambda s: s.lower())

        # output
        for tag in tags:
            print_colored_2("#%s\n" % tag)
            if args.notes:
                for note in tags_and_notes[tag]:
                    print_default("\t%s\n" % note)

    def invoke_on_note(self, args, note):
        """
        Prints tags w/o sorting them and w/o displaying corresponding
        notes.
        """
        for tag in set(note.tags) - self._printed_tags:
            print_colored_2("#%s\n" % tag)
            self._printed_tags.add(tag)
