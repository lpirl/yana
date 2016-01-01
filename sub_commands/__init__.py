import abc

from lib import QUEUE_END_SYMBOL
from lib.plugin_utils import load_classes

class AbstractBaseSubCommand(object):
    """
    All sub commands must inherit from this base class.
    """

    __metaclass__ = abc.ABCMeta

    sub_command = None
    """
    CLI sub command this plugin will be assigned to.
    """

    sub_command_help = None
    """
    Short description of sub command.
    """

    def __init__(self, args_parser):

        assert self.sub_command is not None
        assert self.sub_command_help is not None

        self.args_parser = args_parser

        self.post_init()

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """

    def run(self, args, notes_paths_q):
        """
        Called if the user-provided sub command matches the this class'
        sub command.
        """
        for target_note in iter(notes_paths_q.get, None):
            self.run_on_path(args, target_note)

    @abc.abstractmethod
    def run_on_path(self, args, note_path):
        """
        Called by ``run(…)`` per path.
        Usually, plugins can overwide this function and do not have to
        implement ``run(…)`` themselves.
        """

"""
Import all plugin classes dynamically
"""
SUB_COMMAND_CLASSES = load_classes(__path__, AbstractBaseSubCommand)
