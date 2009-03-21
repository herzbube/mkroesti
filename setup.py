#!/usr/bin/env python
# encoding=utf-8

# Copyright 2009 Patrick Näf
# 
# This file is part of mkroesti
#
# mkroesti is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mkroesti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mkroesti. If not, see <http://www.gnu.org/licenses/>.


# PSL
from distutils.core import setup
from distutils.cmd import Command
import unittest
import sys


# Extend search path for packages and modules. This is required for finding the
# "tests" package and its modules.
PACKAGES_BASEDIR = "src/packages"
sys.path.append(PACKAGES_BASEDIR)


class test(Command):
    """Implements a distutils command to execute unit tests.

    The class name is the same as the command name string used in the 'cmdclass'
    dictionary passed to the setup() function further down. The reason for this
    is that, unfortunately, 'python setup.py test --help' will print out the
    class name instead of the name used in the dictionary (or the 'command_name'
    attribute defined in this class).
    """

    # This must be a class attribute; it is used by
    # "python setup.py --help-commands"
    description = "execute unit tests"

    # Options must be defined in a class attribute. The attribute value is a
    # list of tuples. Each tuple defines an option and must contain 3 values:
    # long option name, short option name, and a description to print with
    # --help. An option that should have an argument must have the suffix "=".
    # Each option defined in user_options must have a data attribute with a
    # name that corresponds to the long name of the option. For instance, an
    # option "--foo-bar" requires an attribute "foo_bar". If the user has
    # specified the option, a value is set to the data attribute. If the
    # option has no argument, the attribute value is set to 1. If the option
    # has an argument, the attribute value is set to the argument value.
    user_options = [("suite=", "s", "run test suite for a specific module [default: run all tests]")]

    def __init__(self, dist):
        # This data attribute is returned by Command.get_command_name()
        self.command_name = "test"
        Command.__init__(self, dist)

    def initialize_options(self):
        # The default value is a callable defined in tests.__init__.py. The user
        # must specify something like this: "--suite tests.test_algorithm"
        self.suite = "tests.allTests"   

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest.defaultTestLoader.loadTestsFromName(self.suite)
        testRunner = unittest.TextTestRunner(verbosity = 1)
        testRunner.run(tests)


setup(
      # Add a command named "test". The name string in the dict is also used by
      # "python setup.py --help-commands", but not by "python setup.py test -h"
      cmdclass = { "test" : test },
      # Meta-data
      name="mkroesti",
      version="0.1",
      url="http://www.herzbube.ch/mkroesti",
      author="Patrick Näf",
      author_email="mkroesti@herzbube.ch",
      description="Extensible hash generator",
      long_description=
"""
mkroesti is an extensible hash generator written in Python.

mkroesti can be used both as a command line utility and as a web tool. It takes
an input (e.g. a file, or a password) and generates different kinds of hashes
from that input. The hashes to generate are selected by naming them on the
command line.

The vanilla mkroesti package provides no hash algorithm implementations of its
own, it is merely a front-end to hash algorithms available through modules in
the Python Standard Library, or through third-party modules. The README file
gives details about the dependencies of mkroesti.

mkroesti can be extended with new hash algorithms, or new implementations of
hash algorithms that are already known to mkroesti. See the README file for
details.
""",
      # Listing packages/modules
      package_dir = {"": PACKAGES_BASEDIR},
      packages = ["mkroesti"],
      # Listing scripts
      scripts = ["src/scripts/mkroesti"]
     )
