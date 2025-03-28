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
import unittest

# mkroesti
from tests import test_algorithm
from tests import test_provider
from tests import test_registry
from tests import test_factory
from tests import test_main


def allTests():
    """This function is used by the test command in setup.py.

    This function is a callable that can be used from anywhere by
    unittest.TestLoader.loadTestsFromName().
    """

    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_algorithm))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_provider))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_registry))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_factory))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_main))
    return suite
