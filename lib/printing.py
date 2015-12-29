"""
A few helpers to have a unified printing facility (similar to logging).
"""

import sys
from os import linesep

from blessings import Terminal

reload(sys)
sys.setdefaultencoding('utf8')

terminal = Terminal()

def styled_print(style, text, interactive_only=False):
    stream = sys.stderr if interactive_only else sys.stdout
    if stream.isatty():

        # excluding newlines from styling since resetting right after a
        # newline seems not to work
        if text.endswith(linesep):
            text = text[:-len(linesep)]
            append = linesep
        else:
            append = ""

        stream.write("".join((
            getattr(terminal, style),
            text,
            terminal.normal,
            append
        )))
    else:
        stream.write(text)

def print_default(text, interactive_only=False):
    styled_print("normal", text, interactive_only)

def print_colored(text, interactive_only=False):
    styled_print("green", text, interactive_only)

def print_highlighted(text, interactive_only=False):
    styled_print("bold", text, interactive_only)
