#!/usr/bin/env python
# encoding=utf-8

from distutils.core import setup

setup(
      # Meta-data
      name="mkroesti",
      version="0.1",
      url="http://www.herzbube.ch/mkroesti",
      author="Patrick Näf",
      author_email="herzbube@herzbube.ch",
      description="Extensible hash generator",
      long_description=
"""
mkroesti is an extensible hash generator written in Python.

mkroesti can be used both as a command line utility and as a Web tool. It takes
an input (e.g. a file, a password) and generates different kinds of hashes from
that input. The hashes to generate are selected by naming them on the command
line.

The vanilla mkroesti package provides no hash algorithm implementations of its
own, it is merely a front-end to hash algorithms available through modules in
the Python Standard Library, or through third-party modules. The README file
gives details about the dependencies of mkroesti.

mkroesti can be extended with new hash algorithms, or new implementations of
hash algorithms that are already known to mkroesti. See the README file for
details.
""",
      # Listing packages/modules
      package_dir = {"": "src/packages"},
      packages = ["mkroesti"],
      # Listing scripts
      scripts = ["src/scripts/mkroesti"],
      # Listing other stuff
#      data_files = [("man page directory, ["man page file"])]
     )
