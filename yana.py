# encoding: UTF-8

from sys import argv
import argparse
import logging

from lib import Yana

# TODO: use https://pypi.python.org/pypi/ConfigArgParse

if __name__ != '__main__':
    raise NotImplementedError(
        "This is a command line tool, nothing to import. :)"
    )

# set up logger
logging.getLogger().name = "yana"
if '-d' in argv:
    logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(
    description="This is Yet Another Notes App.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help='Turn on debug messages?')

# TODO: make proper sub command
parser.add_argument('sub_command', type=str,
                    help='Sub command to use.')

yana = Yana(parser)

# make the path argument should always the last one
parser.add_argument('path', type=str, nargs="?", default=".",
                    help='Directory or file to operate on.')

args = parser.parse_args()
yana.run(args)
