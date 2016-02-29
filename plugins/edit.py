import logging
from plugins import Registry, AbstractBaseSubCommand
from subprocess import Popen
from shlex import split as split_command

from lib import QUEUE_END_SYMBOL

@Registry.register_sub_command
class ShowSubCommand(AbstractBaseSubCommand):

    sub_command = "edit"
    sub_command_help = "edit notes"

    def set_up(self, arg_parser):
        arg_parser.add_argument('-s', '--separate', action='store_true',
                                help='run editor for every note separately',
                                default=False)
        arg_parser.add_argument('-t', '--terminal', action='store_true',
                                help='use a terminal editor', default=False)
        arg_parser.add_argument('-w', '--wait', action='store_true',
                                help='wait for the editor to finish',
                                default=False)
        arg_parser.add_argument('--editor', default="geany -i",
                                help='default editor to use')
        arg_parser.add_argument('--terminal-editor', default="nano",
                                help='default editor on terminal to use')

    def invoke(self, args, notes_q_get):
        notes = list(iter(notes_q_get, QUEUE_END_SYMBOL))
        notes_paths = [n.path for n in notes]
        if args.separate:
            for note_path in notes_paths:
                self.edit_notes(args, (note_path,))
        else:
            self.edit_notes(args, notes_paths)

    def edit_notes(self, args, notes_paths):
        if args.terminal:
            cmd = split_command(args.terminal_editor)
        else:
            cmd = split_command(args.editor)

        popen_kwargs = {
            "stdin": None,
            "stdout": None,
            "stderr": None,
            "close_fds": True
        }

        cmd += list(notes_paths)
        logging.debug("executing '%s'", ' '.join(cmd))
        sub_process = Popen(cmd, **popen_kwargs)

        if args.terminal or args.wait:
            sub_process.wait()
