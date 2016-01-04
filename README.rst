
yana --help
===========

usage: yana.py [-h] [-d] [-v] {edit,list,cache,show} ...

Even though this builds on what will persist (plaint text files and a file
system) it is still only Yet Another Notes App.

positional arguments:
  {edit,list,cache,show}
                        sub command
    edit                edit notes
    list                lists notes
    cache               persistently cache found paths
    show                show notes

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           turn on debug messages (default: False)
  -v, --verbose         turn on verbose messages (default: False)

Now you know.


yana edit --help
================

usage: yana.py edit [-h] [-s] [-t] [-w] [note [note ...]]

positional arguments:
  note            target note (strategies: recursively in the file system,
                  listed during last run by their index, listed during last
                  run by matching paths, in persistent cache by matching
                  paths).

optional arguments:
  -h, --help      show this help message and exit
  -s, --separate  run editor for every note separately
  -t, --terminal  use a terminal editor
  -w, --wait      wait for the editor to finish


yana list --help
================

usage: yana.py list [-h] [note [note ...]]

positional arguments:
  note        target note (strategies: recursively in the file system, listed
              during last run by their index, listed during last run by
              matching paths, in persistent cache by matching paths).

optional arguments:
  -h, --help  show this help message and exit


yana cache --help
=================

usage: yana.py cache [-h] [note [note ...]]

positional arguments:
  note        target note (strategies: recursively in the file system, listed
              during last run by their index, listed during last run by
              matching paths, in persistent cache by matching paths).

optional arguments:
  -h, --help  show this help message and exit


yana show --help
================

usage: yana.py show [-h] [note [note ...]]

positional arguments:
  note        target note (strategies: recursively in the file system, listed
              during last run by their index, listed during last run by
              matching paths, in persistent cache by matching paths).

optional arguments:
  -h, --help  show this help message and exit

