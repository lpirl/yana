import logging
from inspect import getmembers, isclass
from multiprocessing import Process, JoinableQueue as Queue
from subprocess import Popen, PIPE, DEVNULL
from os import linesep


QUEUE_END_SYMBOL = None

class Yana(object):

    def __init__(self, args_parser):
        self.args_parser = args_parser
        self.load_plugins()

    def load_plugins(self):
        """
        Acquires and initializes all plugins (classes) in the module
        ``plugins``.
        """

        # we scope this import into this function so that plugins can
        # import this module
        import plugins as plugins_module

        plugin_classes = [t[1] for t in
                            getmembers(plugins_module, isclass)
                            if not t[0].startswith("Abstract") ]
        logging.debug("found plugins: %s" % str(
            [s.__name__ for s in plugin_classes]
        ))
        self.plugins = {P.sub_command: P(self.args_parser)
                        for P in plugin_classes}

    @classmethod
    def find_notes(cls, path, notes_paths_q):
        """
        Finds all notes under ``path`` and puts them into the
        ``notes_paths_q``.
        """

        # TODO: make this configurable:
        cmd = ("find", path, "-name", "*.yana")

        # we do not care about stderr since providing PIPE as stderr as
        # well deadlocks easily
        inner_find_process = Popen(
            cmd,
            stdout=PIPE,
            stderr=DEVNULL,
            universal_newlines=True,
            bufsize=1
        )

        for line in inner_find_process.stdout.readlines():
            line = line.rstrip(linesep)
            notes_paths_q.put(line)
        notes_paths_q.put(QUEUE_END_SYMBOL)

    def run(self, args):
        """
        TODO docsting
        """

        notes_paths_q = Queue(False)
        find_process = Process(target=self.find_notes,
                                args=(args.path, notes_paths_q))
        find_process.start()

        try:
            sub_command = args.sub_command
            plugin = self.plugins[sub_command]
            logging.debug("running plugin: '%s'" % plugin.__class__.__name__)
            plugin.run(args, notes_paths_q)
        except KeyError:
            logging.error(
                "Could not find plugin '%s', available plugins are: %s" %
                (sub_command, '; '.join(self.plugins.keys()))
            )
            find_process.terminate()
        find_process.join()
