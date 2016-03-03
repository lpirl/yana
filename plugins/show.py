"""
Implements plugins to show (think: cat) plugins.
"""

from shutil import copyfileobj
from sys import stdout
from os import linesep

from plugins import Registry, AbstractBaseSubCommand
from lib.printing import print_colored

@Registry.register_sub_command
class ShowSubCommand(AbstractBaseSubCommand):
    """
    A simple plugin that prints the contents of notes found to stdout.
    """

    sub_command = "show"
    sub_command_help = "show notes"

    def invoke_on_note(self, args, note):
        print_colored("%s%s" % (note.path, linesep), interactive_only=True)
        with open(note.path, "r") as note_file:
            copyfileobj(note_file, stdout)
