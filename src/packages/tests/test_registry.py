# encoding=utf-8

# $Id: test_registry.py 40 2008-12-02 00:04:32Z patrick $

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


"""Unit tests for mkroesti.registry.py"""

# PSL
import unittest

# mkroesti
from mkroesti.registry import ProviderRegistry
from mkroesti.errorhandling import (MKRoestiError, DuplicateProviderError,
                                    UnknownAlgorithmError, UnknownAliasError)
from mkroesti.names import ALIAS_ALL
from tests.stubs import (TestProvider, ALGORITHM_NAME_1, ALGORITHM_NAME_2,
                         ALGORITHM_NAME_3, ALGORITHM_NAME_UNAVAILABLE,
                         ALGORITHM_NAME_UNKNOWN, ALIAS_NAME_1, ALIAS_NAME_2,
                         ALIAS_NAME_3, ALIAS_NAME_UNKNOWN)


class ProviderRegistryTest(unittest.TestCase):
    """Exercise mkroesti.registry.ProviderRegistry"""

    def setUp(self):
        # The registry
        self.registry = ProviderRegistry.getInstance()
        # Setup providers with no alias
        # Note: Don't need to register providers, they do so automatically
        self.noAliasProviders = list()
        self.noAliasProviders.append(TestProvider({None : [ALGORITHM_NAME_1]}))
        # Setup providers with aliases
        # Note: Don't need to register providers, they do so automatically
        self.aliasProviders = list()
        self.noAliasProviders.append(TestProvider({ALIAS_NAME_1 : [ALGORITHM_NAME_1, ALGORITHM_NAME_2]}))
        self.noAliasProviders.append(TestProvider({ALIAS_NAME_2 : [ALGORITHM_NAME_1, ALGORITHM_NAME_3, ALGORITHM_NAME_UNAVAILABLE]}))
        self.noAliasProviders.append(TestProvider({ALIAS_NAME_3 : [ALGORITHM_NAME_1, ALGORITHM_NAME_2, ALGORITHM_NAME_3]}))
        # Setup list with all providers
        self.registeredProviders = list()
        self.registeredProviders.extend(self.noAliasProviders)
        self.registeredProviders.extend(self.aliasProviders)
        # Setup various dictionaries that help certain test method
        self.algorithm2ProviderDict = dict()
        self.alias2ProviderDict = dict()
        self.alias2AlgorithmDict = dict()
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
                    seenAlgorithmNames = self.alias2ProviderDict[aliasName]
                    seenAlgorithmNames.extend(newAlgorithmNames)
                    self.alias2ProviderDict[aliasName] = set(seenAlgorithmNames)
        # Bring lists to a defined order so that they can be used in assertions
        # that compare for equality
        self.noAliasProviders.sort()
        self.aliasProviders.sort()
        self.registeredProviders.sort()
        for algorithmName in self.algorithm2ProviderDict:
            self.algorithm2ProviderDict[algorithmName].sort()
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
            providers.sort()
            self.assertEqual(providers, self.algorithm2ProviderDict[algorithmName])

    def testGetProvidersUnknownAlgorithm(self):
        self.assertRaises(UnknownAlgorithmError, self.registry.getProviders, ALGORITHM_NAME_UNKNOWN)
        self.assertRaises(UnknownAlgorithmError, self.registry.getProviders, None)

    def testGetAlgorithmNames(self):
        expectedAlgorithmNames = self.algorithm2ProviderDict.keys()
        expectedAlgorithmNames.sort()
        actualAlgorithmNames = self.registry.getAlgorithmNames()
        actualAlgorithmNames.sort()
        self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testGetAvailableAlgorithmNames(self):
        expectedAlgorithmNames = self.algorithm2ProviderDict.keys()
        expectedAlgorithmNames.remove(ALGORITHM_NAME_UNAVAILABLE)
        expectedAlgorithmNames.sort()
        actualAlgorithmNames = self.registry.getAvailableAlgorithmNames()
        actualAlgorithmNames.sort()
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
        expectedAliasNames = self.alias2ProviderDict.keys()
        expectedAliasNames.append(ALIAS_ALL)
        expectedAliasNames.sort()
        actualAliasNames = self.registry.getAliasNames()
        actualAliasNames.sort()
        self.assertEqual(actualAliasNames, expectedAliasNames)

    def testResolveAlias(self):
        for aliasName in self.alias2ProviderDict:
            expectedAlgorithmNames = self.alias2AlgorithmDict[aliasName]
            actualAlgorithmNames = self.registry.resolveAlias(aliasName)
            actualAlgorithmNames.sort()
            self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testResolveAliasAll(self):
        expectedAlgorithmNames = self.algorithm2ProviderDict.keys()
        expectedAlgorithmNames.sort()
        actualAlgorithmNames = self.registry.resolveAlias(ALIAS_ALL)
        actualAlgorithmNames.sort()
        self.assertEqual(actualAlgorithmNames, expectedAlgorithmNames)

    def testResolveUnknownAlias(self):
        self.assertRaises(UnknownAliasError, self.registry.resolveAlias, ALIAS_NAME_UNKNOWN)

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
