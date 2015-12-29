import logging
from shutil import copyfileobj
from sys import stdout

from plugins import AbstractBasePlugin
from lib.printing import print_headline

class Show(AbstractBasePlugin):

    sub_command = "show"
    sub_command_help = "show notes"

    def run_on_path(self, args, notes_path):
        print_headline("%s" % notes_path, interactive_only=True)
        with open(notes_path, "r") as f:
            copyfileobj(f, stdout)
