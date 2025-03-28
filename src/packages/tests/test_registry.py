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


"""Unit tests for mkroesti.registry.py"""

# PSL
import unittest

# mkroesti
from mkroesti.registry import ProviderRegistry
from mkroesti.errorhandling import (MKRoestiError, DuplicateProviderError,
                                    UnknownAlgorithmError, UnknownAliasError,
                                    UnavailableAliasError)
from mkroesti.names import ALIAS_ALL
import mkroesti
from tests.helpers import * #@UnusedWildImport


class ProviderRegistryTest(unittest.TestCase):
    """Exercise mkroesti.registry.ProviderRegistry"""

    def setUp(self):
        # The registry
        self.registry = ProviderRegistry.getInstance()
        # Setup providers with no alias
        self.noAliasProviders = list()
        self.noAliasProviders.append(TestProvider({None : [ALGORITHM_NAME_1]}))
        # Setup providers with aliases
        self.aliasProviders = list()
        self.aliasProviders.append(TestProvider({ALIAS_NAME_1 : [ALGORITHM_NAME_1, ALGORITHM_NAME_2]}))
        self.aliasProviders.append(TestProvider({ALIAS_NAME_2 : [ALGORITHM_NAME_1, ALGORITHM_NAME_3, ALGORITHM_NAME_UNAVAILABLE]}))
        self.aliasProviders.append(TestProvider({ALIAS_NAME_3 : [ALGORITHM_NAME_1, ALGORITHM_NAME_2, ALGORITHM_NAME_3]}))
        self.aliasProviders.append(TestProvider({ALIAS_NAME_UNAVAILABLE : [ALGORITHM_NAME_UNAVAILABLE]}))
        # Setup list with all providers
        self.registeredProviders = list()
        self.registeredProviders.extend(self.noAliasProviders)
        self.registeredProviders.extend(self.aliasProviders)
        # Register providers
        mkroesti.registerProviders(self.registeredProviders)
        # Setup various dictionaries that help certain test method
        self.algorithm2ProviderDict = dict()   # provided but not necessarily available
        self.alias2ProviderDict = dict()       # provided but not necessarily available
        self.alias2AlgorithmDict = dict()      # only available algorithms
        for provider in self.registeredProviders:
            for algorithmName in provider.getAlgorithmNames():
                if algorithmName in self.algorithm2ProviderDict:
                    self.algorithm2ProviderDict[algorithmName].append(provider)
                else:
                    self.algorithm2ProviderDict[algorithmName] = [provider]
            for aliasName in provider.getAliasNames():
                if aliasName in self.alias2ProviderDict:
                    self.alias2ProviderDict[aliasName].append(provider)
                else:
                    self.alias2ProviderDict[aliasName] = [provider]
                newAlgorithmNames = provider.getAlgorithmNames()
                if aliasName not in self.alias2AlgorithmDict:
                    self.alias2AlgorithmDict[aliasName] = newAlgorithmNames
                else:
                    seenAlgorithmNames = self.alias2AlgorithmDict[aliasName]
                    seenAlgorithmNames.extend(newAlgorithmNames)
                    # Remove duplicates
                    self.alias2AlgorithmDict[aliasName] = list(set(seenAlgorithmNames))
        # Remove unavailable algorithms from alias resolution; also gather
        # algorithm names for special "all" alias
        self.allAvailableAlgorithmNames = list()
        for aliasName in self.alias2AlgorithmDict:
            algorithmNames = self.alias2AlgorithmDict[aliasName]
            if ALGORITHM_NAME_UNAVAILABLE in algorithmNames:
                algorithmNames.remove(ALGORITHM_NAME_UNAVAILABLE)
            self.allAvailableAlgorithmNames.extend(algorithmNames)
        # Remove duplicates
        self.allAvailableAlgorithmNames = list(set(self.allAvailableAlgorithmNames))
        # Bring lists to a defined order so that they can be used in assertions
        # that compare for equality
        # Note: Algorithm provider instances are not intrinsically sortable, so
        # we just sort them by their id()
        self.noAliasProviders.sort(key=id)
        self.aliasProviders.sort(key=id)
        self.registeredProviders.sort(key=id)
        for algorithmName in self.algorithm2ProviderDict:
            self.algorithm2ProviderDict[algorithmName].sort(key=id)
        for aliasName in self.alias2ProviderDict:
            self.alias2ProviderDict[aliasName].sort()
        for aliasName in self.alias2AlgorithmDict:
            self.alias2AlgorithmDict[aliasName].sort()

    def tearDown(self):
        ProviderRegistry.deleteInstance()

    def testSingleton(self):
        self.assertNotEqual(self.registry, None)
        self.assertEqual(self.registry, ProviderRegistry.getInstance())
        # Deleting the singleton instance will cause a new instance to be
        # created the next time that getInstance() is called
        ProviderRegistry.deleteInstance()
        self.assertNotEqual(self.registry, ProviderRegistry.getInstance())
        self.registry = ProviderRegistry.getInstance()
        # Manually creating an instance is not allowed
        self.assertRaises(MKRoestiError, ProviderRegistry)

    def testAddProvider(self):
        # Providers can be of any type; since in this test case we don't do
        # anything with the provider besides adding it to the registry, it
        # can even be a string
        provider = "this-is-not-a-real-provider" 
        self.registry.addProvider(provider)
        self.assertRaises(DuplicateProviderError, self.registry.addProvider, provider)

    def testGetProviders(self):
        for algorithmName in self.algorithm2ProviderDict:
            providers = self.registry.getProviders(algorithmName)
            # bring to defined order before comparing
            providers.sort(key=id)
            self.assertEqual(providers, self.algorithm2ProviderDict[algorithmName])

    def testGetProvidersUnknownAlgorithm(self):
        self.assertRaises(UnknownAlgorithmError, self.registry.getProviders, ALGORITHM_NAME_UNKNOWN)
        self.assertRaises(UnknownAlgorithmError, self.registry.getProviders, None)

    def testGetAlgorithmNames(self):
        expectedAlgorithmNames = sorted(self.algorithm2ProviderDict.keys())
        actualAlgorithmNames = sorted(self.registry.getAlgorithmNames())
        self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testGetAvailableAlgorithmNames(self):
        expectedAlgorithmNames = sorted(self.algorithm2ProviderDict.keys())
        expectedAlgorithmNames.remove(ALGORITHM_NAME_UNAVAILABLE)
        actualAlgorithmNames = sorted(self.registry.getAvailableAlgorithmNames())
        self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testIsAlgorithmKnown(self):
        for algorithmName in self.algorithm2ProviderDict:
            self.assertTrue(self.registry.isAlgorithmKnown(algorithmName))
        self.assertFalse(self.registry.isAlgorithmKnown(ALGORITHM_NAME_UNKNOWN))
        self.assertFalse(self.registry.isAlgorithmKnown(None))

    def testIsAlgorithmAvailable(self):
        for algorithmName in self.algorithm2ProviderDict:
            isAvailable = self.registry.isAlgorithmAvailable(algorithmName)
            if ALGORITHM_NAME_UNAVAILABLE == algorithmName:
                self.assertFalse(isAvailable)
            else:
                self.assertTrue(isAvailable)
        self.assertRaises(UnknownAlgorithmError, self.registry.isAlgorithmAvailable, ALGORITHM_NAME_UNKNOWN)
        self.assertRaises(UnknownAlgorithmError, self.registry.isAlgorithmAvailable, None)

    def testGetAliasNames(self):
        expectedAliasNames = list(self.alias2ProviderDict.keys())
        expectedAliasNames.append(ALIAS_ALL)
        expectedAliasNames.sort()
        actualAliasNames = self.registry.getAliasNames()
        actualAliasNames.sort()
        self.assertEqual(actualAliasNames, expectedAliasNames)

    def testIsAliasKnown(self):
        for aliasName in self.alias2ProviderDict:
            self.assertEqual(self.registry.isAliasKnown(aliasName), True)
        self.assertEqual(self.registry.isAliasKnown(ALIAS_NAME_UNKNOWN), False)
        self.assertEqual(self.registry.isAliasKnown(None), False)

    def testGetAvailableAliasNames(self):
        expectedAliasNames = list(self.alias2ProviderDict.keys())
        expectedAliasNames.append(ALIAS_ALL)
        expectedAliasNames.remove(ALIAS_NAME_UNAVAILABLE)
        expectedAliasNames.sort()
        actualAliasNames = self.registry.getAvailableAliasNames()
        actualAliasNames.sort()
        self.assertEqual(actualAliasNames, expectedAliasNames)

    def testIsAliasAvailable(self):
        for aliasName in self.alias2ProviderDict:
            expectedResult = (aliasName is not ALIAS_NAME_UNAVAILABLE)
            actualResult = self.registry.isAliasAvailable(aliasName)
            self.assertEqual(actualResult, expectedResult)
        self.assertRaises(UnknownAliasError, self.registry.isAliasAvailable, ALIAS_NAME_UNKNOWN)
        self.assertRaises(UnknownAliasError, self.registry.isAliasAvailable, None)

    def testResolveAlias(self):
        for aliasName in self.alias2ProviderDict:
            if aliasName is not ALIAS_NAME_UNAVAILABLE:
                expectedAlgorithmNames = self.alias2AlgorithmDict[aliasName]
                actualAlgorithmNames = self.registry.resolveAlias(aliasName)
                actualAlgorithmNames.sort()
                self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)
            else:
                self.assertRaises(UnavailableAliasError, self.registry.resolveAlias, aliasName)

    def testResolveAliasAll(self):
        expectedAlgorithmNames = sorted(self.allAvailableAlgorithmNames)
        actualAlgorithmNames = sorted(self.registry.resolveAlias(ALIAS_ALL))
        self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testResolveUnknownAlias(self):
        self.assertRaises(UnknownAliasError, self.registry.resolveAlias, ALIAS_NAME_UNKNOWN)
        self.assertRaises(UnknownAliasError, self.registry.resolveAlias, None)

    def testResolveUnavailableAlias(self):
        self.assertRaises(UnavailableAliasError, self.registry.resolveAlias, ALIAS_NAME_UNAVAILABLE)

    def testNoProviders(self):
        # Destroy the registry from setUp(), then create a new and empty one
        ProviderRegistry.deleteInstance()
        self.registry = ProviderRegistry.getInstance()
        # Repeat all tests, but with no registered providers. The point is to
        # test if all registry methods correctly handle the border case
        # "no providers" 
        self.assertRaises(UnknownAlgorithmError, self.registry.getProviders, ALGORITHM_NAME_1)
        self.assertEqual(self.registry.getAlgorithmNames(), list())
        self.assertEqual(self.registry.getAvailableAlgorithmNames(), list())
        self.assertFalse(self.registry.isAlgorithmKnown(ALGORITHM_NAME_1))
        self.assertRaises(UnknownAlgorithmError, self.registry.isAlgorithmAvailable, ALGORITHM_NAME_1)
        self.assertEqual(self.registry.getAliasNames(), [ALIAS_ALL])
        self.assertRaises(UnknownAliasError, self.registry.resolveAlias, ALIAS_NAME_1)
        self.assertEqual(self.registry.resolveAlias(ALIAS_ALL), list())


if __name__ == "__main__":
    unittest.main()
