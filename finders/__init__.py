import abc
from pkgutil import walk_packages
from inspect import getmembers, isclass

class AbstractBaseFinder(object):
    """
    All finders must inherit from this base class.
    """

    def __init__(self):

        # TODO

        self.post_init()

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """

    @abc.abstractmethod
    def run(self):
        # TODO
        pass

"""
Import all plugins dynamically
"""
FINDER_CLASSES = set()
for module_loader, module_name, _ in walk_packages(__path__):
    module = module_loader.find_module(module_name).load_module(module_name)
    for cls_name, cls in getmembers(module):
        if not isclass(cls):
            continue
        if not issubclass(cls, AbstractBaseFinder):
            continue
        if cls_name.startswith("Abstract"):
            continue
        exec('from %s import %s' % (module_name, cls_name))
        exec('FINDER_CLASSES.add(%s)' % (module_name, cls_name))
