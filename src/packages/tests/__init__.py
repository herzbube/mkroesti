# encoding=utf-8

# PSL
import unittest

# mkroesti
import test_algorithm

def allTests():
    """Callable that can be used by unittest.TestLoader.loadTestsFromName()."""

    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_algorithm))
    return suite
