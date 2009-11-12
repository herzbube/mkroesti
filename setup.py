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
    """Implements a distutils command to execute automated tests.

    To run the command, a user must type one of the following:
      ./setup.py test                                # run all tests
      ./setup.py test --suite=tests.test_algorithm   # run tests from only one module

    The class name is the same as the command name string used in the 'cmdclass'
    dictionary passed to the setup() function further down. The reason for this
    is that, unfortunately, 'python setup.py test --help' will print out the
    class name instead of the name used in the dictionary (or the 'command_name'
    attribute defined in this class).
    """

    # This must be a class attribute; it is used by
    # "python setup.py --help-commands"
    description = "execute automated tests"

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
        testResult = testRunner.run(tests)
        if not testResult.wasSuccessful():
            sys.exit(1)


setup(
      # Add a command named "test". The name string in the dict is also used by
      # "python setup.py --help-commands", but not by "python setup.py test -h"
      cmdclass = { "test" : test },
      # Meta-data
      name="mkroesti",
      version="0.4",
      url="http://www.herzbube.ch/mkroesti",
      author="Patrick Naef",
      author_email="herzbube@herzbube.ch",
      description="A hash generator",
      long_description=
"""
mkroesti is a hash generator written in Python.

mkroesti can be used both as a command line utility and as a web tool. It takes
an input (e.g. a file, or a password) and generates different kinds of hashes
from that input. The hashes to generate are selected by naming them on the
command line, or ticking the corresponding checkboxes in the web GUI.

mkroesti provides no hash algorithm implementations of its own. Instead it
consists of a collection of front-ends to hash algorithms available in the
Python Standard Library, and from a number of third-party modules. The README
file gives details about the dependencies of mkroesti.

mkroesti also defines a couple of interfaces that allow third parties to inject
new front-ends to previously unavailable hash algorithms. The README file has
more information on how this extension mechanism works.
""",
      # Listing packages/modules
      package_dir = {"": PACKAGES_BASEDIR},
      packages = ["mkroesti"],
      # Listing scripts
      scripts = ["src/scripts/mkroesti"]
     )
