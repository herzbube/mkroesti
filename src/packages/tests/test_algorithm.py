# encoding=utf-8

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
