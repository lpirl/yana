"""
A few helpers to have a unified printing facility (similar to logging).

Information that are only for interactive shells will go to stderr.
"""

import sys

from blessings import Terminal

reload(sys)
sys.setdefaultencoding('utf8')

terminal = Terminal()

def colored_print(color, text, interactive_only=False):
    stream = sys.stderr if interactive_only else sys.stdout
    stream.write("%s\n" % getattr(terminal, color)(text))

def print_headline(text, interactive_only=False):
    colored_print("yellow", text, interactive_only)
