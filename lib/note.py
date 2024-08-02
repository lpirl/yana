"""
This module implements the in-code representation of on-disk notes.
"""

from contextlib import contextmanager
from os.path import abspath, relpath, normpath, isfile
from re import compile as re_compile

# TODO: more laziness for instance variables
#   https://pypi.python.org/pypi/cached-property

class Note(object):
    """
    Programmatic representation ("model") of a note (i.e. a file in the
    file system).

    It provides some helpers for comparing notes and working with tags.
    """

    _tag_pattern = None
    """ compiled regular expression object """

    @classmethod
    def set_parser(cls, arg_parser):
        """
        Used to add command line arguments to configure the behavior
        implemented in this class.
        """
        arg_parser.add_argument('--tag-regex', help='regular expression ' +
                                'used to identify tags in notes',
                                default=r"(?m)(?<!\[)(?:#)([\w_]+)")

    @classmethod
    def set_args(cls, args):
        """
        Used to receive user-specified options.
        See also method ``set_parser``.
        """
        cls._tag_pattern = re_compile(args.tag_regex)

    def __init__(self, path):

        assert self._tag_pattern is not None

        self.path = path
        normalized_path = normpath(path)
        self.relpath = relpath(normalized_path)
        self.abspath = abspath(normalized_path)

    def __hash__(self):
        return hash(self.abspath)

    def __eq__(self, other):
        return isinstance(other, Note) and self.abspath == other.abspath

    def __str__(self):
        return self.path

    def open(self, *args, **kwags):
        """
        Returns the contents of the note.
        """
        if not isfile(self.abspath):
            return
        return open(self.abspath, *args, **kwags)

    @property
    def content(self):
        """
        Returns the contents of the note.
        """
        out = ""
        with self.open() as note_file:
            out = note_file.read()
        return out

    @property
    def lines(self):
        """
        Yields the lines of the note.
        """
        with self.open() as note_file:
            for line in note_file:
                yield line

    @property
    def tags(self):
        """
        Returns all tags that can be found w/i a note.
        """
        return set(self._tag_pattern.findall(self.content))
