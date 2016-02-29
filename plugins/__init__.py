# encoding: utf8

"""
This module contains the base implementations for all kinds of plugins.

Sub modules contain the plugins itself.

Why things are the way they are:

Plugins have to register explicitly because it is less import magic
(and remember Zen 2 of Python: explicit is better than implicit).

Different kinds of plugins share a common top module so the can have
shared code more easily (e.g. w/i one sub module).

The superclass for all kinds of plugins is not unified so we do not have
to call all plugins on all extension points.
Also the shared state within one respective object of such a class might
turn out to be an illusion when different kinds of plugins are distributed
across processes. This would probably be confusion to program.
"""

import abc
from pkgutil import walk_packages
import logging

from lib import QUEUE_END_SYMBOL


class Registry(object):

    sub_commands = set()
    finders = set()

    def __init__(self):
        """
        Class can not be instantiated.
        Please use it's classmethods.
        """
        raise RuntimeError(self.__init__.__doc__)

    @classmethod
    def register(cls, registry, plugin_cls):
        registry.add(plugin_cls)
        return plugin_cls

    @classmethod
    def register_sub_command(cls, plugin_cls):
        return cls.register(cls.sub_commands, plugin_cls)

    @classmethod
    def register_finder(cls, plugin_cls):
        return cls.register(cls.finders, plugin_cls)


class AbstractBasePlugin(object):
    """
    Provides common functionality for plugins.
    """

    __metaclass__ = abc.ABCMeta

    def set_up(self, arg_parser):
        """
        Called after initialization (plugins must not override __init__).
        """
        pass

    def tear_down(self):
        """
        Called on program exit.
        """
        pass


class AbstractBaseSubCommand(AbstractBasePlugin):
    """
    All sub commands should from this base class.
    """

    sub_command = None
    """
    CLI sub command this plugin will be assigned to.
    """

    sub_command_help = None
    """
    Short description of sub command.
    """

    def __init__(self, *args, **kwargs):

        assert self.sub_command is not None
        assert self.sub_command_help is not None

        super(AbstractBaseSubCommand, self).__init__(*args, **kwargs)

    def invoke(self, args, note_q_get):
        """
        Called if the user-provided sub command matches the this class'
        sub command.
        """
        for note in iter(note_q_get, QUEUE_END_SYMBOL):
            self.invoke_on_note(args, note)

    def invoke_on_note(self, args, note):
        """
        Called by ``invoke(…)`` per path.
        Usually, plugins can overwide this function and do not have to
        implement ``invoke(…)`` themselves.
        """
        pass


class AbstractBaseFinder(AbstractBasePlugin):
    """
    All finders should from this base class.
    """

    finds = None
    """
    A very short and descriptive text saying what this finder can find.
    It must fit into "This finder finds notes <YXZ>"
    """

    def __init__(self, *args, **kwargs):

        assert self.finds is not None

        super(AbstractBaseFinder, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    def find(self, args, queries, found_path_callback):
        """
        This is where the implementation goes.
        Finders are required to submit found paths to notes via
        ``found_path_callback``.
        To do so, they most likely want to use the information provided
        through ``queries``.
        """
        pass


# load sub modules so they can register at the corresponding registry
for module_loader, module_name, _ in walk_packages(__path__):
    logging.debug("loading plugin module %s", module_name)
    module_loader.find_module(module_name).load_module(module_name)
