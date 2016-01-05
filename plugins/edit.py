import logging
from plugins import Registry, AbstractBaseSubCommand
from subprocess import Popen, call

@Registry.register_sub_command
class ShowSubCommand(AbstractBaseSubCommand):

    sub_command = "edit"
    sub_command_help = "edit notes"

    def post_init(self, arg_parser):
        arg_parser.add_argument('-s', '--separate', action='store_true',
            default=False, help='run editor for every note separately')
        arg_parser.add_argument('-t', '--terminal', action='store_true',
            default=False, help='use a terminal editor')
        arg_parser.add_argument('-w', '--wait', action='store_true',
            default=False, help='wait for the editor to finish')

    def invoke(self, args, notes_paths_q_get):
        notes_paths = list(iter(notes_paths_q_get, None))
        if args.separate:
            for note_path in notes_paths:
                self.edit_notes(args, (note_path,))
        else:
            self.edit_notes(args, notes_paths)

    def edit_notes(self, args, notes_paths):
        if args.terminal:
            # todo: make this configurable:
            cmd = "nano".split()
        else:
            # todo: make this configurable:
            cmd = "geany -i".split()

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
