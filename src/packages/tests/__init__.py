# encoding=utf-8

# PSL
import unittest

# mkroesti
import test_algorithm
import test_provider
import test_registry
import test_factory
import test_main


def allTests():
    """Callable that can be used by unittest.TestLoader.loadTestsFromName()."""

    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_algorithm))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_provider))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_registry))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_factory))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_main))
    return suite
