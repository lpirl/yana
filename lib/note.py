from os.path import abspath, relpath, normpath, isfile

class Note(object):
    """
    Programmatic representation ("model") of a note (i.e. a file in the
    file system).

    It provides some helpers for comparing notes and working with tags.
    """

    def __init__(self, path):
        assert isfile(path)
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
