# encoding=utf-8

"""Contains the ProviderRegistry class."""


# mkroesti
from mkroesti.errorhandling import MKRoestiError
from mkroesti.names import * #@UnusedWildImport


class ProviderRegistry:
    """Registry where provider objects must be registered.

    Provider objects are instances of classes that implement
    mkroesti.provider.ProviderInterface.

    Provider objects that want to contribute algorithms to mkroesti's operation
    must be registered by calling addProvider(). ProviderRegistry offers a
    number of useful queries that allow clients to inspect which algorithms
    exist (getAlgorithmNames()) and which algorithms are actually available
    (getAvailableAlgorithmNames()). The difference is that sometimes a provider
    knows how to provide a certain algorithm "in theory", but is unable to
    do so in the current environment because some third party modules are
    missing.

    To actually obtain an algorithm object, a client must first call
    getProviders() to retrieve a list of providers that the algorithm is known
    to. Next the client must check each provider whether the algorithm is
    actually available from it; from among these providers, the client must now
    select one and instruct it to create the algorithm object. Note: The client
    should use the interface defined by AlgorithmInterface to interact with the
    algorithm object.

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
            ProviderRegistry()
        return ProviderRegistry._instance

    def __init__(self):
        """Create the singleton."""
        if None != ProviderRegistry._instance:
            raise MKRoestiError("Only one instance of ProviderRegistry is allowed!")
        ProviderRegistry._instance = self
        self.providers = list()

    def addProvider(self, provider):
        """Adds a provider object to this registry."""
        if provider in self.providers:
            raise MKRoestiError("Providers can be registered only once!")
        self.providers.append(provider)

    def getProviders(self, algorithmName):
        """Returns a list of providers that the named algorithm is known to."""
        providers = list()
        for provider in self.providers:
            if provider.isAlgorithmKnown(algorithmName):
                providers.append(provider)
        return providers

    def getAlgorithmNames(self):
        """Returns a list of all names of algorithms known to registered providers."""
        # TODO The following block appears several times in this class, the
        # only difference being the method that is called on providers and its
        # parameters. Is it possible to make a function from the block and specify
        # as function parameters the method name and the method parameters?
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
        """Returns True if the named algorithm is known to any registered provider."""
        return (algorithmName in self.getAlgorithmNames())

    def isAlgorithmAvailable(self, algorithmName):
        """Returns True if the named algorithm is available from any registered provider."""
        return (algorithmName in self.getAvailableAlgorithmNames())

    def getAliasNames(self):
        """Returns a list of all names of aliases known to registered providers."""
        unifyingDict = { ALIAS_ALL : None }
        for provider in self.providers:
            unifyingDict.update(dict.fromkeys(provider.getAliasNames()))
        return unifyingDict.keys()

    def resolveAlias(self, aliasName):
        """Returns a list of all names of aliases known to registered providers."""
        unifyingDict = dict()
        if aliasName == ALIAS_ALL:
            # Must treat ALIAS_ALL specially because providers do not implement
            # handling this (see class docs of
            # mkroesti.provider.ProviderInterface for details)
            for provider in self.providers:
                unifyingDict.update(dict.fromkeys(provider.getAlgorithmNames()))
        else:
            for provider in self.providers:
                if aliasName in provider.getAliasNames():
                    unifyingDict.update(dict.fromkeys(provider.resolveAlias(aliasName)))
        return unifyingDict.keys()

