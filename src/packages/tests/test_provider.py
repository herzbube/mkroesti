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


"""Unit tests for mkroesti.provider.py"""

# PSL
import unittest

# mkroesti
from mkroesti.names import ALIAS_ALL
from mkroesti.provider import AbstractProvider, AliasAbstractProvider
from mkroesti.errorhandling import (MKRoestiError, UnknownAlgorithmError,
                                    DuplicateAlgorithmError, UnknownAliasError,
                                    UnavailableAliasError)
from tests.helpers import TestAliasProvider


class AbstractProviderTest(unittest.TestCase):
    """Exercise mkroesti.provider.AbstractProvider"""

    def setUp(self):
        self.notProvidedAlgorithmName = "not-provided-algorithm"
        self.notProvidedAliasName = "not-provided-alias"
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
        self.assertEquals(self.provider.getAliasNames(), list())

    def testIsAliasKnown(self):
        self.assertEquals(self.provider.isAliasKnown(self.notProvidedAliasName), False)
        self.assertEquals(self.provider.isAliasKnown(None), False)

    def testGetAvailableAliasNames(self):
        self.assertRaises(NotImplementedError, self.provider.getAvailableAliasNames)

    def testIsAliasAvailable(self):
        self.assertRaises(NotImplementedError, self.provider.isAliasAvailable, self.notProvidedAliasName)

    def testResolveAlias(self):
        self.assertRaises(NotImplementedError, self.provider.resolveAlias, self.notProvidedAliasName)

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
        self.notProvidedAliasName = "not-provided-alias"
        self.fullyAvailableAliasName = "fully-available-alias" 
        self.partiallyAvailableAliasName = "partially-available-alias" 
        self.notAvailableAliasName = "not-available-alias" 
        self.namesDictionary = {
            None : ["algorithm1", "algorithm2", "algorithm3"],
            self.fullyAvailableAliasName : ["algorithm4", "algorithm5"],
            self.partiallyAvailableAliasName : ["algorithm6", "algorithm7"],
            self.notAvailableAliasName : ["algorithm8", "algorithm9"]
            }
        # Create flat list of algorithm names
        self.providedAlgorithmNames = list()
        for algorithmList in self.namesDictionary.values():
            self.providedAlgorithmNames.extend(algorithmList)
        # Create flat list of alias names
        self.providedAliasNames = list(self.namesDictionary.keys())
        self.providedAliasNames.remove(None)
        # Only one alias is not available
        self.notAvailableAliasNames = list()
        self.notAvailableAliasNames.append(self.notAvailableAliasName)
        # All remaining aliases are available
        self.availableAliasNames = self.providedAliasNames[:]   # make a copy
        for aliasName in self.notAvailableAliasNames:
            self.availableAliasNames.remove(aliasName) 
        self.partiallyAvailableAlgorithmNames = self.namesDictionary[self.partiallyAvailableAliasName][1:]
        self.partiallyNotAvailableAlgorithmNames = self.namesDictionary[self.partiallyAvailableAliasName][0:1]
        # Algorithms that are not available are
        # - all those that self.notAvailableAliasName resolves to
        # - some of those that self.partiallyAvailableAliasName resolves to (the
        #   point being that some but not all of the alias' algorithms are
        #   available)
        self.notAvailableAlgorithmNames = self.namesDictionary[self.notAvailableAliasName][:]   # make a copy
        self.notAvailableAlgorithmNames.extend(self.partiallyNotAvailableAlgorithmNames)
        # All remaining algorithms are available
        self.availableAlgorithmNames = self.providedAlgorithmNames[:]   # make a copy
        for algorithmName in self.notAvailableAlgorithmNames:
            self.availableAlgorithmNames.remove(algorithmName) 
        # Bring lists to a defined order so that they can be used in assertions
        # that compare for equality
        self.providedAlgorithmNames.sort()
        self.availableAlgorithmNames.sort()
        self.notAvailableAlgorithmNames.sort()
        self.partiallyAvailableAlgorithmNames.sort()
        self.partiallyNotAvailableAlgorithmNames.sort()
        self.providedAliasNames.sort()
        self.availableAliasNames.sort()
        self.notAvailableAliasNames.sort()
        # Now set up the provider object
        self.provider = TestAliasProvider(self.namesDictionary, self.availableAlgorithmNames)

    def testGetAlgorithmNames(self):
        names = self.provider.getAlgorithmNames()
        names.sort()   # bring to defined order before comparing
        self.assertEqual(names, self.providedAlgorithmNames)

    def testGetAliasNames(self):
        names = self.provider.getAliasNames()
        names.sort()   # bring to defined order before comparing
        self.assertEqual(names, self.providedAliasNames)

    def testIsAliasKnown(self):
        for name in self.providedAliasNames:
            self.assertEquals(self.provider.isAliasKnown(name), True)
        self.assertEquals(self.provider.isAliasKnown(self.notProvidedAliasName), False)
        self.assertEquals(self.provider.isAliasKnown(None), False)

    def testGetAvailableAliasNames(self):
        self.assertEqual(self.provider.getAvailableAliasNames(), self.availableAliasNames)

    def testIsAliasAvailable(self):
        for aliasName in self.availableAliasNames:
            expectedResult = True
            actualResult = self.provider.isAliasAvailable(aliasName)
            self.assertEqual(expectedResult, actualResult)
        for aliasName in self.notAvailableAliasNames:
            expectedResult = False
            actualResult = self.provider.isAliasAvailable(aliasName)
            self.assertEqual(expectedResult, actualResult)
        self.assertRaises(UnknownAliasError, self.provider.isAliasAvailable, self.notProvidedAliasName)
        self.assertRaises(UnknownAliasError, self.provider.isAliasAvailable, None)

    def testResolveAlias(self):
        for aliasName in self.providedAliasNames:
            if aliasName in self.notAvailableAliasNames:
                self.assertRaises(UnavailableAliasError, self.provider.resolveAlias, aliasName)
                continue
            elif aliasName is self.partiallyAvailableAliasName:
                expectedNames = self.partiallyAvailableAlgorithmNames
            else:
                expectedNames = self.namesDictionary[aliasName]
            actualNames = self.provider.resolveAlias(aliasName)
            # bring to defined order before comparing
            expectedNames.sort()
            actualNames.sort()
            self.assertEqual(expectedNames, actualNames)
        self.assertRaises(UnknownAliasError, self.provider.resolveAlias, self.notProvidedAliasName)
        self.assertRaises(UnknownAliasError, self.provider.resolveAlias, None)

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
        # -> is handled by the registry, not providers
        self.assertRaises(MKRoestiError, AliasAbstractProvider, { ALIAS_ALL : ["algorithm1"] })
        self.assertTrue(ALIAS_ALL not in self.provider.getAliasNames())
        self.assertRaises(UnknownAliasError, self.provider.resolveAlias, ALIAS_ALL)


if __name__ == "__main__":
    unittest.main()
