# encoding=utf-8

# Copyright 2008 Patrick Näf
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


"""Unit tests for mkroesti.provider.py"""

# PSL
import unittest

# mkroesti
from mkroesti.names import ALIAS_ALL
from mkroesti.provider import AbstractProvider, AliasAbstractProvider
from mkroesti.errorhandling import (MKRoestiError, UnknownAlgorithmError,
                                    DuplicateAlgorithmError, UnknownAliasError)


class AbstractProviderTest(unittest.TestCase):
    """Exercise mkroesti.provider.AbstractProvider"""

    def setUp(self):
        self.notProvidedAlgorithmName = "not-provided-algorithm"
        self.providedAlgorithmNames = ["algorithm1", "algorithm2", "algorithm3"]
        self.provider = AbstractProvider(algorithmNames = self.providedAlgorithmNames)

    def testGetAlgorithmNames(self):
        self.assertEqual(self.provider.getAlgorithmNames(), self.providedAlgorithmNames)

    def testIsAlgorithmKnown(self):
        for name in self.providedAlgorithmNames:
            self.assertTrue(self.provider.isAlgorithmKnown(name))
        self.assertFalse(self.provider.isAlgorithmKnown(self.notProvidedAlgorithmName))
        self.assertFalse(self.provider.isAlgorithmKnown(None))

    def testGetAvailableAlgorithmNames(self):
        self.assertEqual(self.provider.getAvailableAlgorithmNames(), self.providedAlgorithmNames)

    def testIsAlgorithmAvailable(self):
        for name in self.providedAlgorithmNames:
            (isAvailable, reason) = self.provider.isAlgorithmAvailable(name) #@UnusedVariable
            self.assertTrue(isAvailable)
        self.assertRaises(UnknownAlgorithmError, self.provider.isAlgorithmAvailable, self.notProvidedAlgorithmName)
        self.assertRaises(UnknownAlgorithmError, self.provider.isAlgorithmAvailable, None)

    def testGetAlgorithmSource(self):
        for name in self.providedAlgorithmNames:
            self.assertRaises(NotImplementedError, self.provider.getAlgorithmSource, name)
        self.assertRaises(NotImplementedError, self.provider.getAlgorithmSource, self.notProvidedAlgorithmName)
        self.assertRaises(NotImplementedError, self.provider.getAlgorithmSource, None)

    def testCreateAlgorithm(self):
        for name in self.providedAlgorithmNames:
            self.assertRaises(NotImplementedError, self.provider.createAlgorithm, name)
        self.assertRaises(NotImplementedError, self.provider.createAlgorithm, self.notProvidedAlgorithmName)
        self.assertRaises(NotImplementedError, self.provider.createAlgorithm, None)

    def testGetAliasNames(self):
        self.assertRaises(NotImplementedError, self.provider.getAliasNames)

    def testResolveAlias(self):
        self.assertRaises(NotImplementedError, self.provider.resolveAlias, "dummy-alias")

    def testProvideZeroAlgorithms(self):
        self.assertRaises(MKRoestiError, AbstractProvider)
        self.assertRaises(MKRoestiError, AbstractProvider, list())

    def testProvideDuplicateAlgorithms(self):
        duplicateNames = list()
        duplicateNames.extend(self.providedAlgorithmNames)
        duplicateNames.extend(self.providedAlgorithmNames)
        self.assertRaises(DuplicateAlgorithmError, AbstractProvider, duplicateNames)


class AliasAbstractProviderTest(unittest.TestCase):
    """Exercise mkroesti.provider.AliasAbstractProvider"""

    def setUp(self):
        self.notProvidedAlias = "not-provided-alias"
        self.namesDictionary = {
            None : ["algorithm1", "algorithm2", "algorithm3"],
            "alias1" : ["algorithm4", "algorithm5", "algorithm6"],
            "alias2" : ["algorithm7", "algorithm8", "algorithm9"]
            }
        self.provider = AliasAbstractProvider(self.namesDictionary)
        # Create flat list of algorithm names
        self.providedAlgorithmNames = list()
        for algorithmList in self.namesDictionary.values():
            self.providedAlgorithmNames.extend(algorithmList)
        # Create flat list of alias names
        self.providedAliasNames = self.namesDictionary.keys()
        self.providedAliasNames.remove(None)
        # Bring lists to a defined order so that they can be used in assertions
        # that compare for equality
        self.providedAlgorithmNames.sort()
        self.providedAliasNames.sort()

    def testGetAlgorithmNames(self):
        names = self.provider.getAlgorithmNames()
        names.sort()   # bring to defined order before comparing
        self.assertEqual(names, self.providedAlgorithmNames)

    def testGetAliasNames(self):
        names = self.provider.getAliasNames()
        names.sort()   # bring to defined order before comparing
        self.assertEqual(names, self.providedAliasNames)

    def testResolveAlias(self):
        for name in self.providedAliasNames:
            expectedNames = self.namesDictionary[name]
            actualNames = self.provider.resolveAlias(name)
            # bring to defined order before comparing
            expectedNames.sort()
            actualNames.sort()
            self.assertEqual(expectedNames, actualNames)
        self.assertRaises(UnknownAliasError, self.provider.resolveAlias, self.notProvidedAlias)

    def testProvideZeroAliases(self):
        # It's ok to provide no aliases, therefore we expect no error
        provider = AliasAbstractProvider({ None : ["algorithm1"] })
        self.assertEqual(provider.getAliasNames(), list())

    def testProvideDuplicateAliases(self):
        # Can't provoke this error because 1) we must specify a dictionary to
        # AliasAbstractProvider, but 2) dictionaries may contain only unique
        # keys
        pass

    def testAliasAll(self):
        # Test behaviour when the special alias ALIAS_ALL is used
        self.assertRaises(MKRoestiError, AliasAbstractProvider, { ALIAS_ALL : ["algorithm1"] })
        self.assertTrue(ALIAS_ALL not in self.provider.getAliasNames())
        self.assertRaises(UnknownAliasError, self.provider.resolveAlias, ALIAS_ALL)


if __name__ == "__main__":
    unittest.main()
