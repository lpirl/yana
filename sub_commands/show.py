import logging
from shutil import copyfileobj
from sys import stdout
from os import linesep

from sub_commands import AbstractBaseSubCommand
from lib.printing import print_colored

class Show(AbstractBaseSubCommand):

    sub_command = "show"
    sub_command_help = "show notes"

    def run_on_path(self, args, notes_path):
        print_colored("%s%s" % (notes_path, linesep), interactive_only=True)
        with open(notes_path, "r") as f:
            copyfileobj(f, stdout)
