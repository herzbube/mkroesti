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


"""Unit tests for mkroesti.factory.py"""

# PSL
import unittest

# mkroesti
from mkroesti.factory import AlgorithmFactory
from mkroesti.registry import ProviderRegistry
from mkroesti.errorhandling import UnknownAlgorithmError, UnavailableAlgorithmError
from mkroesti.names import ALIAS_ALL
from tests.stubs import (TestProvider, ALGORITHM_NAME_1, ALGORITHM_NAME_2,
                         ALGORITHM_NAME_3, ALGORITHM_NAME_UNAVAILABLE,
                         ALGORITHM_NAME_UNKNOWN, ALIAS_NAME_1, ALIAS_NAME_2,
                         ALIAS_NAME_3, ALIAS_NAME_UNKNOWN)


class AlgorithmFactoryTest(unittest.TestCase):
    """Exercise mkroesti.factory.AlgorithmFactory"""

    def setUp(self):
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
        self.algorithm2CountDict = dict()
        self.alias2AlgorithmDict = dict()
        for provider in self.registeredProviders:
            for algorithmName in provider.getAlgorithmNames():
                if algorithmName in self.algorithm2CountDict:
                    self.algorithm2CountDict[algorithmName] += 1
                else:
                    self.algorithm2CountDict[algorithmName] = 1
            for aliasName in provider.getAliasNames():
                newAlgorithmNames = provider.getAlgorithmNames()
                if aliasName not in self.alias2AlgorithmDict:
                    self.alias2AlgorithmDict[aliasName] = newAlgorithmNames
                else:
                    seenAlgorithmNames = self.alias2ProviderDict[aliasName]
                    seenAlgorithmNames.extend(newAlgorithmNames)
                    self.alias2ProviderDict[aliasName] = set(seenAlgorithmNames)
        self.alias2AlgorithmDict[ALIAS_ALL] = self.algorithm2CountDict.keys()
        # Bring lists to a defined order so that they can be used in assertions
        # that compare for equality
        self.noAliasProviders.sort()
        self.aliasProviders.sort()
        self.registeredProviders.sort()
        for aliasName in self.alias2AlgorithmDict:
            self.alias2AlgorithmDict[aliasName].sort()
        pass

    def tearDown(self):
        ProviderRegistry.deleteInstance()

    def testCreateAlgorithm(self):
        for algorithmName in self.algorithm2CountDict:
            if ALGORITHM_NAME_UNAVAILABLE == algorithmName:
                continue
            algorithmObjects = AlgorithmFactory.createAlgorithms(name = algorithmName)
            self.assertEqual(len(algorithmObjects), 1)
            algorithmObject = algorithmObjects[0]
            self.assertNotEqual(algorithmObject, None)
            # Exercise the algorithm object a little bit, using what we would
            # expect from a real AlgorithmInterface
            self.assertEqual(algorithmObject.getName(), algorithmName)
            self.assertNotEqual(algorithmObject.getProvider(), None)
            self.assertNotEqual(algorithmObject.getHash("dummy-input"), None)

    def testCreateAlgorithmWithDuplicateHashes(self):
        for algorithmName in self.algorithm2CountDict:
            if ALGORITHM_NAME_UNAVAILABLE == algorithmName:
                continue
            algorithmObjects = AlgorithmFactory.createAlgorithms(name = algorithmName, duplicateHashes = True)
            self.assertEqual(len(algorithmObjects), self.algorithm2CountDict[algorithmName])
            providers = list()
            hash = None
            for algorithmObject in algorithmObjects:
                self.assertNotEqual(algorithmObject, None)
                # Exercise the algorithm object a little bit, using what we would
                # expect from a real AlgorithmInterface
                self.assertEqual(algorithmObject.getName(), algorithmName)
                provider = algorithmObject.getProvider()
                self.assertNotEqual(provider, None)
                # Same provider does not provide an algorithm multiple times
                self.assertFalse(provider in providers)
                providers.append(provider)
                # All algorithm objects produce the same hash
                newHash = algorithmObject.getHash("dummy-input")
                self.assertNotEqual(newHash, None)
                if hash == None:
                    hash = newHash
                else:
                    self.assertEqual(newHash, hash)

    def testCreateUnknownAlgorithm(self):
        self.assertRaises(UnknownAlgorithmError, AlgorithmFactory.createAlgorithms, ALGORITHM_NAME_UNKNOWN)
        self.assertRaises(UnknownAlgorithmError, AlgorithmFactory.createAlgorithms, None)

    def testCreateUnavailableAlgorithm(self):
        self.assertRaises(UnavailableAlgorithmError, AlgorithmFactory.createAlgorithms, ALGORITHM_NAME_UNAVAILABLE)

    def testCreateAlgorithmWithAlias(self):
        # Make sure that the test data contains ALIAS_ALL
        self.assertTrue(ALIAS_ALL in self.alias2AlgorithmDict)
        for aliasName in self.alias2AlgorithmDict:
            expectedAlgorithmNames = self.alias2AlgorithmDict[aliasName]
            if ALGORITHM_NAME_UNAVAILABLE in expectedAlgorithmNames:
                expectedAlgorithmNames.remove(ALGORITHM_NAME_UNAVAILABLE)
            algorithmObjects = AlgorithmFactory.createAlgorithms(name = aliasName)
            actualAlgorithmNames = list()
            for algorithmObject in algorithmObjects:
                algorithmName = algorithmObject.getName()
                self.assertFalse(algorithmName in actualAlgorithmNames)
                actualAlgorithmNames.append(algorithmName)
                # Don't exercise the algorithm object any further
            self.assertEqual(sorted(actualAlgorithmNames), expectedAlgorithmNames)

    def testCreateAlgorithmWithAliasAllWithDuplicateHashes(self):
        algorithmObjects = AlgorithmFactory.createAlgorithms(name = ALIAS_ALL, duplicateHashes = True)
        actualAlgorithm2CountDict = dict()
        for algorithmObject in algorithmObjects:
            algorithmName = algorithmObject.getName()
            if algorithmName not in actualAlgorithm2CountDict:
                actualAlgorithm2CountDict[algorithmName] = 1
            else:
                actualAlgorithm2CountDict[algorithmName] += 1
        expectedAlgorithm2CountDict = self.algorithm2CountDict.copy()
        del expectedAlgorithm2CountDict[ALGORITHM_NAME_UNAVAILABLE]
        self.assertEqual(actualAlgorithm2CountDict, expectedAlgorithm2CountDict)
        expectedAlgorithmNames = self.algorithm2CountDict.keys()
        expectedAlgorithmNames.remove(ALGORITHM_NAME_UNAVAILABLE)
        actualAlgorithmNames = actualAlgorithm2CountDict.keys() 
        self.assertEqual(sorted(actualAlgorithmNames), sorted(expectedAlgorithmNames))

    def testCreateAlgorithmWithUnknownAlias(self):
        # The factory cannot distinguish between unknown algorithms and
        # unknown aliases, therefore it reports any unknown name as an unknown
        # algorithm
        self.assertRaises(UnknownAlgorithmError, AlgorithmFactory.createAlgorithms, ALIAS_NAME_UNKNOWN)

  
if __name__ == "__main__":
    unittest.main()
