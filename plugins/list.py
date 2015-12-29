import logging
from os import sep as pathsep, linesep
from os.path import split as path_split

from plugins import AbstractBasePlugin
from lib.printing import print_colored, print_default, print_highlighted

class List(AbstractBasePlugin):

    sub_command = "list"
    sub_command_help = "lists notes"

    def post_init(self):
        self.list_count = 0

    def run_on_path(self, args, notes_path):
        self.list_count += 1
        print_colored("%u " % self.list_count, True)

        pathname, filename = path_split(notes_path)
        print_default("%s%s" % (pathname, pathsep))
        print_highlighted("%s%s" % (filename, linesep))
