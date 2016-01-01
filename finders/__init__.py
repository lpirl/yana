import abc

from lib.plugin_utils import load_classes

class AbstractBaseFinder(object):
    """
    All finders must inherit from this base class.
    """

    def __init__(self, args_parser):

        self.args_parser = args_parser

        # TODO

        self.post_init()

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """

    @abc.abstractmethod
    def find(self, target_notes, cached_paths, notes_paths_q_put):
        # TODO
        pass

"""
Import all plugins
"""
FINDER_CLASSES = load_classes(__path__, AbstractBaseFinder)
