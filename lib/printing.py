"""
A few helpers to have a unified printing facility (similar to logging).
"""

import sys
from os import linesep

from blessings import Terminal

PYTHON_MAJOR_VERSION = sys.version_info[0]

if PYTHON_MAJOR_VERSION == 2:
    # enable utf8 compatibility
    reload(sys)
    sys.setdefaultencoding('utf8')

TERMINAL = Terminal()

def styled_print(style, text, interactive_only=False):
    """
    Unifies all printing facilities (i.e. does actual printing).

    If ``interactive_only``, ``text`` is printed to ``stderr``, so that
    e.g. programs connected via a pipe do not see it.
    """
    stream = sys.stderr if interactive_only else sys.stdout
    if stream.isatty():

        # excluding newlines from styling since resetting right after a
        # newline seems not to work
        if text.endswith(linesep):
            text = text[:-len(linesep)]
            append = linesep
        else:
            append = ""

        text = "".join((
            getattr(TERMINAL, style),
            text,
            TERMINAL.normal,
            append
        ))

    stream.write(text)

    # make unbuffered writes in Python 3
    if PYTHON_MAJOR_VERSION == 3:
        stream.flush()

def print_default(text, interactive_only=False):
    """
    Shortcut to print w/o formating.
    """
    styled_print("normal", text, interactive_only)

def print_colored(text, interactive_only=False):
    """
    Shortcut to print colored.
    """
    styled_print("green", text, interactive_only)

def print_highlighted(text, interactive_only=False):
    """
    Shortcut to print highlighted (w/o color).
    """
    styled_print("bold", text, interactive_only)
