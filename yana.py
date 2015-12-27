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

parser = argparse.ArgumentParser(
    description="Yet another notes app.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help='Turn on debug messages?')

# TODO: make proper sub command
parser.add_argument('sub_command', type=str,
                    help='Sub command to use.')

parser.add_argument('path', type=str, nargs="?", default=".",
                    help='Path to operate on (directory or a file).')

# set up logger
logging.getLogger().name = "yana"
if '-d' in argv:
	logging.getLogger().setLevel(logging.DEBUG)

yana = Yana(parser)
args = parser.parse_args()
yana.run(args)
