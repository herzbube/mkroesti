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


"""Unit tests for mkroesti.algorithm.py"""

# PSL
import unittest

# mkroesti
from mkroesti.algorithm import AbstractAlgorithm


class AbstractAlgorithmTest(unittest.TestCase):
    """Exercise mkroesti.algorithm.AbstractAlgorithm"""

    def testGetName(self):
        name = "dummy-name"
        algorithm = AbstractAlgorithm(name = name)
        self.assertEqual(algorithm.getName(), name)
        pass

    def testGetProvider(self):
        provider = "dummy-provider"
        algorithm = AbstractAlgorithm(provider = provider)
        self.assertEqual(algorithm.getProvider(), provider)
        pass

    def testNeedBytesInput(self):
        algorithm = AbstractAlgorithm()
        self.assertRaises(NotImplementedError, algorithm.needBytesInput)
        pass

    def testGetHash(self):
        input = "dummy-input"
        algorithm = AbstractAlgorithm()
        self.assertRaises(NotImplementedError, algorithm.getHash, input)
        pass


#class FooAlgorithmTest(unittest.TestCase):
#    """Exercise bla bla"""
#
#    def testGetName(self):
#        """Exercise hahaha."""
#        algorithmName = ALGORITHM_NAME_1
#        stubAlgorithm = AlgorithmStub()
#        methodName = "getName"
#        stubAlgorithm.setReturnValue(methodName, algorithmName)
#        self.assertEqual(stubAlgorithm.getName(), ALGORITHM_NAME_1)
#        pass
#
#    def testGetProvider(self):
#        """Exercise dooda."""
##        stubAlgorithm = AlgorithmStub(algorithmName = ALGORITHM_NAME_1)
##        self.assertEqual(stubAlgorithm.getName(), ALGORITHM_NAME_1)
#        pass
#
#    def testGetHash(self):
#        """Exercise yodel."""
#        pass


if __name__ == "__main__":
    unittest.main()
