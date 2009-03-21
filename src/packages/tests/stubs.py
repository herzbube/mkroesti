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


"""Stub classes that can be used by mkroesti unit tests."""

# mkroesti
from mkroesti.provider import AliasAbstractProvider


# Define constants used by the stubs in this module
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


class Stub():
    def __init__(self):
        self.parameterValues = dict()
        self.returnValues = dict()
        self.numberOfCalls = dict()

    def setParameterValue(self, methodName, parameterName, parameterValue):
        """Remembers which value was specified for the given parameter when the given method was called the last time."""
        self.parameterValues[(methodName, parameterName)] = parameterValue
    def getParameterValue(self, methodName, parameterName):
        """Returns which value was specified for the given parameter when the given method was called the last time."""
        return self.parameterValues[(methodName, parameterName)]
    def setReturnValue(self, methodName, returnValue):
        """Defines the value that the given method should return from now on."""
        self.returnValues[methodName] = returnValue
    def getReturnValue(self, methodName):
        """Returns the canned return value for the given method (None if none was defined)."""
        if methodName in self.returnValues:
            return self.returnValues[methodName]
        else:
            return None
    def incrementNumberOfCalls(self, methodName):
        """Increments how many times the given method was called by 1."""
        if methodName in self.numberOfCalls:
            self.numberOfCalls[methodName] += 1   # is there really no ++ operator in Python?
        else:
            self.numberOfCalls[methodName] = 1
    def getNumberOfCalls(self, methodName):
        """Returns how many times the given method was called so far."""
        if methodName in methodName:
            return self.numberOfCalls[methodName]
        else:
            return 0


class AlgorithmStub(Stub):
    def getName(self):
        methodName = "getName"
        self.incrementNumberOfCalls(methodName)
        return self.getReturnValue(methodName)
    def getProvider(self):
        methodName = "getProvider"
        self.incrementNumberOfCalls(methodName)
        return self.getReturnValue(methodName)
    def getHash(self, input):
        methodName = "getHash"
        self.incrementNumberOfCalls(methodName)
        parameterName = "input"
        self.setParameterValue(methodName, parameterName, input)
        return self.getReturnValue(methodName)
        

class ProviderStub(Stub):
    def getAlgorithmNames(self):
        methodName = "getAlgorithmNames"
        self.incrementNumberOfCalls(methodName)
        return self.getReturnValue(methodName)
    def isAlgorithmKnown(self, algorithmName):
        methodName = "isAlgorithmKnown"
        self.incrementNumberOfCalls(methodName)
        parameterName = "algorithmName"
        self.setParameterValue(methodName, parameterName, algorithmName)
        return self.getReturnValue(methodName)
    def getAvailableAlgorithmNames(self):
        methodName = "getAvailableAlgorithmNames"
        self.incrementNumberOfCalls(methodName)
        return self.getReturnValue(methodName)
    def isAlgorithmAvailable(self, algorithmName):
        methodName = "isAlgorithmAvailable"
        self.incrementNumberOfCalls(methodName)
        parameterName = "algorithmName"
        self.setParameterValue(methodName, parameterName, algorithmName)
        return self.getReturnValue(methodName)
    def getAlgorithmSource(self, algorithmName):
        methodName = "getAlgorithmSource"
        self.incrementNumberOfCalls(methodName)
        parameterName = "algorithmName"
        self.setParameterValue(methodName, parameterName, algorithmName)
        return self.getReturnValue(methodName)
    def createAlgorithm(self, algorithmName):
        methodName = "createAlgorithm"
        self.incrementNumberOfCalls(methodName)
        parameterName = "algorithmName"
        self.setParameterValue(methodName, parameterName, algorithmName)
        return self.getReturnValue(methodName)
    def getAliasNames(self):
        methodName = "getAliasNames"
        self.incrementNumberOfCalls(methodName)
        return self.getReturnValue(methodName)
    def resolveAlias(self, aliasName):
        methodName = "resolveAlias"
        self.incrementNumberOfCalls(methodName)
        parameterName = "aliasName"
        self.setParameterValue(methodName, parameterName, aliasName)
        return self.getReturnValue(methodName)



class TestAlgorithm():
    """Implements an algorithm with pre-determined test data."""

    def __init__(self, algorithmName = None, provider = None):
        self.name = algorithmName
        self.provider = provider
    def getName(self):
        return self.name
    def getProvider(self):
        return self.provider
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


def setUpProviderStub(algorithmNames = list(), aliasName = None):
    """Creates a ProviderStub instance and sets it up with pre-defined values.

    These are the initial characteristics of the provider:
    - The provider knows the algorithms specified to this function
    - All algorithms known by the provider are available
    - The source returned for each algorithm is the same string
    - When requested to create an algorithm object, the provider always returns
      None
    - The provider knows either no, or exactly one alias which must be specified
      to this function
    - If there is an alias, it resolves to all the algorithms known by the
      provider
    """
    stub = ProviderStub()
    methodName = "getAlgorithmNames"
    returnValue = algorithmNames
    stub.setReturnValue(methodName, returnValue)
    methodName = "isAlgorithmKnown"
    returnValue = True
    stub.setReturnValue(methodName, returnValue)
    methodName = "getAvailableAlgorithmNames"
    returnValue = True
    stub.setReturnValue(methodName, returnValue)
    methodName = "isAlgorithmAvailable"
    returnValue = (True, None)
    stub.setReturnValue(methodName, returnValue)
    methodName = "getAlgorithmSource"
    returnValue = "the rabbit hole"
    stub.setReturnValue(methodName, returnValue)
    methodName = "createAlgorithm"
    returnValue = None
    stub.setReturnValue(methodName, returnValue)
    if aliasName is None:
        methodName = "getAliasNames"
        returnValue = list()
        stub.setReturnValue(methodName, returnValue)
        methodName = "resolveAlias"
        returnValue = list()
        stub.setReturnValue(methodName, returnValue)
    else:
        methodName = "getAliasNames"
        returnValue = [aliasName]
        stub.setReturnValue(methodName, returnValue)
        methodName = "resolveAlias"
        returnValue = algorithmNames
        stub.setReturnValue(methodName, returnValue)
    return stub


# Example code for using setUpProviderStub()
#
#    def setUp(self):
#        # Setup providers with no alias
#        self.noAliasProviders = list()
#        self.noAliasProviders.append(setUpProviderStub(algorithmNames = [ALGORITHM_NAME_1],
#                                                          aliasName = None))
#        # Setup providers with aliases
#        self.aliasProviders = list()
#        self.aliasProviders.append(setUpProviderStub(algorithmNames = [ALGORITHM_NAME_1, ALGORITHM_NAME_2],
#                                                          aliasName = ALIAS_NAME_1))
#        self.aliasProviders.append(setUpProviderStub(algorithmNames = [ALGORITHM_NAME_1, ALGORITHM_NAME_3],
#                                                          aliasName = ALIAS_NAME_2))
#        self.aliasProviders.append(setUpProviderStub(algorithmNames = [ALGORITHM_NAME_1, ALGORITHM_NAME_2, ALGORITHM_NAME_3],
#                                                          aliasName = ALIAS_NAME_3))
#        # Setup list with all providers and add them to the registry
#        self.registeredProviders = list()
#        self.registeredProviders.extend(self.noAliasProviders)
#        self.registeredProviders.extend(self.aliasProviders)
#        for provider in self.registeredProviders:
#            self.registry.addProvider(provider)
