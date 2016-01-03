from os import sep as pathsep, linesep
from os.path import split as path_split

from plugins import Registry, AbstractBaseSubCommand
from lib.printing import print_colored, print_default, print_highlighted

@Registry.register_sub_command
class ListSubCommand(AbstractBaseSubCommand):

    sub_command = "list"
    sub_command_help = "lists notes"

    def post_init(self):
        self.list_count = 0

    def invoke_on_path(self, args, note_path):
        self.list_count += 1
        print_colored("%u " % self.list_count, True)

        pathname, filename = path_split(note_path)
        print_default("%s%s" % (pathname, pathsep))
        print_highlighted("%s%s" % (filename, linesep))
