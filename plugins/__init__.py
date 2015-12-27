import abc
from pkgutil import walk_packages
from inspect import getmembers, isclass

class AbstractBasePlugin(metaclass=abc.ABCMeta):
    """
    All plugins must inherit from this base class.
    """

    __metaclass__ = abc.ABCMeta

    sub_command = None
    """
    Sub command this plugin will be assigned to.
    """

    def __init__(self, args_parser):

        assert self.sub_command is not None

        self.args_parser = args_parser

        self.post_init()
        """hook for subclasses"""

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """

    @abc.abstractmethod
    def run(self, args):
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
