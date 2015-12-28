import abc
from pkgutil import walk_packages
from inspect import getmembers, isclass
from lib import QUEUE_END_SYMBOL

class AbstractBasePlugin(object):
    """
    All plugins must inherit from this base class.
    """

    __metaclass__ = abc.ABCMeta

    sub_command = None
    """
    Sub command this plugin will be assigned to.
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
        """hook for subclasses"""

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """

    def run(self, args, notes_paths_q):
        """
        Runs the plugin if the user-provided sub command matches the
        sub command of this class.
        """
        for path in iter(notes_paths_q.get, None):
            self.run_on_path(args, path)

    @abc.abstractmethod
    def run_on_path(self, args, note_path):
        """
        Runs the plugin if the user-provided sub command matches the
        sub command of this class.
        """

"""
Import all plugins dynamically
"""
for module_loader, module_name, _ in walk_packages(__path__):
    module = module_loader.find_module(module_name).load_module(module_name)
    for cls_name, cls in getmembers(module):
        if not isclass(cls):
            continue
        if not issubclass(cls, AbstractBasePlugin):
            continue
        if cls_name.startswith("Abstract"):
            continue
        exec('from %s import %s' % (module_name, cls_name))
