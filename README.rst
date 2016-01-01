
yana --help
===========

usage: yana.py [-h] [-d] {list,show} ...

Even though this builds on what will persist (plaint text files and a file
system) it is still only Yet Another Notes App.

positional arguments:
  {list,show}  sub command
    list       lists notes
    show       show notes

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  turn on debug messages (default: False)

Now you know.


yana list --help
================

usage: yana.py list [-h] [note [note ...]]

positional arguments:
  note        target note (lookup order: index from last run's notes, glob
              match in last run's paths, directory or file.

optional arguments:
  -h, --help  show this help message and exit


yana show --help
================

usage: yana.py show [-h] [note [note ...]]

positional arguments:
  note        target note (lookup order: index from last run's notes, glob
              match in last run's paths, directory or file.

optional arguments:
  -h, --help  show this help message and exit

