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
    def set_parser(_, arg_parser):
        arg_parser.add_argument('--tag-regex', help='regular expression ' +
                                 'used to identify tags in notes',
                                default=r"(?m)(?<!\[)(?:#)([\w-]+)")

    @classmethod
    def set_args(cls, args):
        cls._tag_pattern = re_compile(args.tag_regex)

    def __init__(self, path):

        assert isfile(path)
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

    @property
    def tags(self):
        with open(self.abspath) as note_file:
            note_content = note_file.read()
            return self.__class__._tag_pattern.findall(note_content)