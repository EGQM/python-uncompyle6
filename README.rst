|buildstatus|

uncompyle6
==========

A native Python cross-version Decompiler and Fragment Decompiler.
Follows in the tradition of decompyle, uncompyle, and uncompyle2.


Introduction
------------

*uncompyle6* translates Python bytecode back into equivalent Python
source code. It accepts bytecodes from Python version 2.1 to 3.6 or
so, including PyPy bytecode and Dropbox's Python 2.5 bytecode.

Why this?
---------

There were a number of decompyle, uncompile, uncompyle2, uncompyle3
forks around. All of them came basically from the same code base, and
almost all of them no were no longer actively maintained. Only one
handled Python 3, and even there, only 3.2. This code pulls these
together and moves forward. It also addresses a number of open issues
in the previous forks.

What makes this different from other CPython bytecode decompilers?: its
ability to deparse just fragments and give source-code information
around a given bytecode offset.

I use this to deparse fragments of code inside my trepan_
debuggers_. For that, I need to record text fragments for all
bytecode offsets (of interest). This purpose although largely
compatible with the original intention is yet a little bit different.
See this_ for more information.

The idea of Python fragment deparsing given an instruction offset can
be used in showing stack traces or any program that wants to show a
location in more detail than just a line number.  It can be also used
when source-code information does not exist and there is just bytecode
information.

Requirements
------------

This project requires Python 2.6 or later, PyPy 3-2.4, or PyPy-5.0.1.
The bytecode files it can read has been tested on Python bytecodes from
versions 2.1-2.7, and 3.2-3.6 and the above-mentioned PyPy versions.

Installation
------------

This uses setup.py, so it follows the standard Python routine:

::

    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    python setup.py install # may need sudo
    # or if you have pyenv:
    python setup.py develop

A GNU makefile is also provided so :code:`make install` (possibly as root or
sudo) will do the steps above.

Testing
-------

::

   make check

A GNU makefile has been added to smooth over setting running the right
command, and running tests from fastest to slowest.

If you have remake_ installed, you can see the list of all tasks
including tests via :code:`remake --tasks`


Usage
-----

Run

::

$ uncompyle6 *compiled-python-file-pyc-or-pyo*

For usage help:

::

   $ uncompyle6 -h


Known Bugs/Restrictions
-----------------------

About 90% of the decompilation verifies from Python 2.3.7 to Python
3.4.2 on the standard library packages I have on my system.

(Verification is the process of decompiling bytecode, compiling with a
Python for that byecode version, and then comparing the byetcode
produced by the decompiled/compiled program. Some allowance is made
for inessential differences, but other semantically equivalent
differences are not caught.)

Later distributions average about 200 files. At this point, 2.7
decompilation is definitely better than uncompyle2. A number of bugs
have been fixed. We now handle more Python bytecodes than the old
decompyle program that handled Python bytecodes ranging from 1.5 to
2.4.  There is some work do do on the lower end which is more
difficult for us since we don't have a Python interpreter for versions
1.5, 1.6 or 2.0.

Python 3.5 largely works, but still has some bugs in it.
Python 3.6 changes things drastically by using word codes rather than
byte codes, and that needs to be addressed.

Currently not all Python magic numbers are supported. Specifically in
some versions of Python, notably Python 3.6, the magic number has
changes several times within a version. We support only the released
magic. There are also customized Python interpreters, notably Dropbox,
which use their own magic and encrypt bytcode. With the exception of
the Dropbox's old Python 2.5 interpreter this kind of thing is not
handled.

There is lots to do, so please dig in and help.

See Also
--------

* https://github.com/zrax/pycdc : supports all versions of Python and is written in C++
* https://code.google.com/archive/p/unpyc3/ : supports Python 3.2 only. The above projects use a different decompiling technique what is used here.
* The HISTORY_ file.

.. |downloads| image:: https://img.shields.io/pypi/dd/uncompyle6.svg
.. _trepan: https://pypi.python.org/pypi/trepan
.. _HISTORY: https://github.com/rocky/python-uncompyle6/blob/master/HISTORY.md
.. _debuggers: https://pypi.python.org/pypi/trepan3k
.. _remake: https://bashdb.sf.net/remake
.. _pycdc: https://github.com/zrax/pycdc
.. _this: https://github.com/rocky/python-uncompyle6/wiki/Deparsing-technology-and-its-use-in-exact-location-reporting
.. |buildstatus| image:: https://travis-ci.org/rocky/python-uncompyle6.svg
		 :target: https://travis-ci.org/rocky/python-uncompyle6
