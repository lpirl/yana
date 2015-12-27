import logging
from inspect import getmembers, isclass

import plugins as plugins_module

class Yana(object):

    def __init__(self, args_parser):
        self.args_parser = args_parser
        self.load_plugins()

    def load_plugins(self):
        """
        Acquires and initializes all plugins (classes) in the module
        ``plugins``.
        """
        plugin_classes = [t[1] for t in
                            getmembers(plugins_module, isclass)
                            if not t[0].startswith("Abstract") ]
        logging.debug("found plugins: %s" % str(
            [s.__name__ for s in plugin_classes]
        ))
        self.plugins = {P.sub_command: P(self.args_parser)
                        for P in plugin_classes}

    def run(self, args):
        """
        TODO docsting
        """
        try:
            sub_command = args.sub_command
            plugin = self.plugins[sub_command]
            logging.debug("running plugin: '%s'" % plugin.__class__.__name__)
            plugin.run(args)
        except KeyError:
            logging.error(
                "Could not find plugin '%s', available plugins are: %s" %
                (sub_command, '; '.join(self.plugins.keys()))
            )
