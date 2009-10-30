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


"""Helper classes that can be used by mkroesti unit tests"""

# mkroesti
from mkroesti.provider import AliasAbstractProvider


# Define constants used by the helper classes in this module
ALIAS_NAME_1 = "alias-name-1"
ALIAS_NAME_2 = "alias-name-2"
ALIAS_NAME_3 = "alias-name-3"
ALGORITHM_NAME_1 = "algorithm-name-1"
ALGORITHM_NAME_2 = "algorithm-name-2"
ALGORITHM_NAME_3 = "algorithm-name-3"
ALGORITHM_RESULT_1 = "algorithm-result-1"
ALGORITHM_RESULT_2 = "algorithm-result-2"
ALGORITHM_RESULT_3 = "algorithm-result-3"
ALGORITHM_SOURCE_1 = "algorithm-source-1"
ALGORITHM_SOURCE_2 = "algorithm-source-2"
ALGORITHM_SOURCE_3 = "algorithm-source-3"
ALGORITHM_NAME_UNAVAILABLE = "algorithm-name-unavailable"
ALGORITHM_REASON_UNAVAILABLE = "algorithm-reason-unavailable"
ALGORITHM_SOURCE_UNAVAILABLE = "algorithm-source-unavailable"
ALGORITHM_NAME_UNKNOWN = "algorithm-name-unknown"
ALIAS_NAME_UNKNOWN = "alias-name-unknown"
ALIAS_NAME_UNAVAILABLE = "alias-name-unavailable"


class TestAlgorithm():
    """Implements an algorithm with pre-determined test data."""

    def __init__(self, algorithmName = None, provider = None):
        self.name = algorithmName
        self.provider = provider
    def getName(self):
        return self.name
    def getProvider(self):
        return self.provider
    def needBytesInput(self):
        return False
    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_NAME_1 == algorithmName:
            return ALGORITHM_RESULT_1
        elif ALGORITHM_NAME_2 == algorithmName:
            return ALGORITHM_RESULT_2
        elif ALGORITHM_NAME_3 == algorithmName:
            return ALGORITHM_RESULT_3
        else:
            raise ValueError("Unsupported algorithm name " + algorithmName)


class TestProvider(AliasAbstractProvider):
    """Implements an algorithm provider with pre-determined test data."""

    def __init__(self, namesDictionary):
        AliasAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        if ALGORITHM_NAME_1 == algorithmName:
            ALGORITHM_SOURCE_1
        elif ALGORITHM_NAME_2 == algorithmName:
            ALGORITHM_SOURCE_2
        elif ALGORITHM_NAME_3 == algorithmName:
            ALGORITHM_SOURCE_3
        elif ALGORITHM_NAME_UNAVAILABLE == algorithmName:
            ALGORITHM_SOURCE_UNAVAILABLE
        else:
            raise ValueError("Unsupported algorithm name " + algorithmName)

    def isAlgorithmAvailable(self, algorithmName):
        if ALGORITHM_NAME_UNAVAILABLE == algorithmName:
            return (False, ALGORITHM_REASON_UNAVAILABLE)
        else:
            return AliasAbstractProvider.isAlgorithmAvailable(self, algorithmName)

    def createAlgorithm(self, algorithmName):
        return TestAlgorithm(algorithmName, self)


class TestAliasProvider(AliasAbstractProvider):
    """Implements a configurable alias provider that is incapa."""

    def __init__(self, namesDictionary, availableAlgorithmNames):
        AliasAbstractProvider.__init__(self, namesDictionary)
        self.availableAlgorithmNames = availableAlgorithmNames

    def isAlgorithmAvailable(self, algorithmName):
        if (algorithmName in self.availableAlgorithmNames):
            return (True, None)
        else:
            return (False, ALGORITHM_REASON_UNAVAILABLE)
