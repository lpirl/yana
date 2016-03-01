YANA
====

**Y**\ et **A**\ nother **N**\ otes **A**\ pp wants ease the management
of knowledge using
only a few mental concepts,
tools you know (e.g. your terminal and editor of choice)
and building on technology that will persist (i.e. human-readable files in
the file system).

However, it is rather a **personal prototype** than a product with batteries included.

Features
========

See table of contents of the `document describing the usage <USAGE.rst>`_.

To-Do's
=======

In loose order:

conceptual
----------

* connections between notes

  * directed
  * labeled

  * but how to represent them?

    * using links in markup language?
    * using symlinks?
    * using IDs?
    * …?

  * can they be tagged?


* mappable to mind maps and vice versa

  * again: how?

technical
---------

* use `ConfigArgParse <https://pypi.python.org/pypi/ConfigArgParse>`_

* tests

  * probably behavioral testing especially for CLI applications?

* provide a ``setup.py``

* limit by tags

  * e.g. ``yana -t [<pattern> [<pattern …]]``

* replace tags

  * e.g. ``yana tag-replace [old] [new] …``

* collect all notes into a specified directory

  * e.g. to assemble all notes for archiving
  * flat xor maintaining the directory hierarchy

* compile notes

  * using markup compiler of preference
  * might be useful in connection with notes collection (see above)

* caching of notes found?

  * e.g. for really slow network connections
  * but: OS caches usually quite good


* more clever searching of notes with respect to lately found ones

  * e.g. travel file system up from known notes instead top-down every time
  * but: complexity-benefit ratio probably very bad

Useless Trivia [1]_
===================

*YANA* emerged because of the dissatisfaction of the available personal
knowledge management tools.
For example,
bookmarking and re-reading Web sites is too verbose and
inefficient,
placing text files everywhere is too unstructured,
hosted solutions introduce dependencies and so on.

It is still an experiment and it remains unclear if the aspired concepts
are representable using the employed low-tech foundations…

.. [1] Thanks to the great project
   `sshuttle <https://github.com/apenwarr/sshuttle>`_ for this great headline.
