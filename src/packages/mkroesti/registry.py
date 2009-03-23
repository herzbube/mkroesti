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


"""Contains the ProviderRegistry class."""


# mkroesti
from mkroesti.errorhandling import MKRoestiError
from mkroesti.errorhandling import (DuplicateProviderError,
                                    UnknownAlgorithmError, UnknownAliasError)
from mkroesti.names import * #@UnusedWildImport


class ProviderRegistry:
    """Registry where provider objects must be registered.

    Provider objects are instances of classes that implement
    mkroesti.provider.ProviderInterface (they do not need to inherit from it).

    Provider objects that want to contribute algorithms to mkroesti's operation
    must be registered by calling addProvider(). ProviderRegistry offers a
    number of useful queries that allow clients to inspect which algorithms
    exist (getAlgorithmNames()) and which algorithms are actually available
    (getAvailableAlgorithmNames()). The difference is that sometimes a provider
    knows how to provide a certain algorithm "in theory", but is unable to
    do so in the current environment, e.g. because some third party modules are
    missing.

    To actually obtain an algorithm object, a client must first call
    getProviders() to retrieve a list of providers that the algorithm is known
    to. Next the client must check each provider whether the algorithm is
    actually available from it; from among these providers, the client must now
    select one and instruct it to create the algorithm object. Note: The client
    should use the interface defined by AlgorithmInterface to interact with the
    algorithm object (the algorithm object's class does not necessarily
    inherit from AlgorithmInterface).

    ProviderRegistry also supports the handling of aliases. Clients may inspect
    which aliases exist (getAliasNames()) and resolve aliases to real algorithm
    names (resolveAlias()). 

    ProviderRegistry is a singleton. The singleton accessor (and creator)
    is ProviderRegistry.getInstance().
    """

    _instance = None

    @staticmethod
    def getInstance():
        """Access the singleton."""
        if None == ProviderRegistry._instance:
            ProviderRegistry._instance = ProviderRegistry()
        return ProviderRegistry._instance

    @staticmethod
    def deleteInstance():
        """Remove the reference to the singleton instance."""
        if None != ProviderRegistry._instance:
            ProviderRegistry._instance = None

    def __init__(self):
        """Create the singleton."""
        if None != ProviderRegistry._instance:
            raise MKRoestiError("Only one instance of ProviderRegistry is allowed!")
        self.providers = list()

    def addProvider(self, provider):
        """Adds a provider object to this registry."""
        if provider in self.providers:
            raise DuplicateProviderError("Providers can be registered only once!")
        self.providers.append(provider)

    def getProviders(self, algorithmName):
        """Returns a list of providers that the given algorithm is known to.

        Raises UnknownAlgorithmError if the given algorithm is not known to any
        registered provider.
        """
        providers = list()
        for provider in self.providers:
            if provider.isAlgorithmKnown(algorithmName):
                providers.append(provider)
        if len(providers) > 0:
            return providers
        else:
            raise UnknownAlgorithmError(algorithmName)

    def getAlgorithmNames(self):
        """Returns a list of all names of algorithms known to registered providers."""
        unifyingDict = dict()
        for provider in self.providers:
            # Because keys are unique within a dictionary, an algorithm name
            # will appear only once within unifyingDict even if several
            # providers know about that algorithm
            unifyingDict.update(dict.fromkeys(provider.getAlgorithmNames()))
        return unifyingDict.keys()

    def getAvailableAlgorithmNames(self):
        """Returns a list of all names of algorithms that are available from registered providers."""
        unifyingDict = dict()
        for provider in self.providers:
            unifyingDict.update(dict.fromkeys(provider.getAvailableAlgorithmNames()))
        return unifyingDict.keys()

    def isAlgorithmKnown(self, algorithmName):
        """Returns True if the given algorithm is known to any registered provider."""
        return (algorithmName in self.getAlgorithmNames())

    def isAlgorithmAvailable(self, algorithmName):
        """Returns True if the given algorithm is available from any registered provider.

        Raises UnknownAlgorithmError if the given algorithm is not known to any
        registered provider.
        """
        if not self.isAlgorithmKnown(algorithmName):
            raise UnknownAlgorithmError(algorithmName)
        return (algorithmName in self.getAvailableAlgorithmNames())

    def getAliasNames(self):
        """Returns a list of all names of aliases known to registered providers.

        The list contains the special alias ALIAS_ALL.
        """
        unifyingDict = { ALIAS_ALL : None }
        for provider in self.providers:
            unifyingDict.update(dict.fromkeys(provider.getAliasNames()))
        return unifyingDict.keys()

    def resolveAlias(self, aliasName):
        """Returns a list of algorithm names that the given alias resolves to.

        Raises UnknownAliasError if the given alias is not known to any
        registered provider.
        """
        unifyingDict = dict()
        if aliasName == ALIAS_ALL:
            # Must treat ALIAS_ALL specially because providers do not implement
            # handling this (see class docs of
            # mkroesti.provider.ProviderInterface for details)
            for provider in self.providers:
                unifyingDict.update(dict.fromkeys(provider.getAlgorithmNames()))
        else:
            if aliasName not in self.getAliasNames():
                raise UnknownAliasError(aliasName)
            for provider in self.providers:
                if aliasName in provider.getAliasNames():
                    unifyingDict.update(dict.fromkeys(provider.resolveAlias(aliasName)))
        return unifyingDict.keys()

