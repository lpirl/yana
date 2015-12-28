import logging

from plugins import AbstractBasePlugin

class List(AbstractBasePlugin):

    sub_command = "list"
    sub_command_help = "lists notes"

    def run_on_path(self, args, notes_path):
        print("%s" % notes_path)
