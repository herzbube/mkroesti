"""Contains the AlgorithmFactory class."""


# mkroesti
from mkroesti.registry import ProviderRegistry
from mkroesti.errorhandling import MKRoestiError


class AlgorithmFactory:
    """Factory that creates algorithm objects.

    Algorithm objects are instances of classes that implement
    mkroesti.algorithm.AlgorithmInterface.

    AlgorithmFactory is mostly a convenience class that acts as a friendly
    front-end to the mkroesti.registry.ProviderRegistry singleton. Clients
    who simply want to go straight ahead and do some hashing can call
    createAlgorithms(), which will return a list of algorithm objects. The
    list can then be iterated and one hash for each of the algorithm objects
    can be created.

    If a client specifies an alias instead of a real algorithm name,
    createAlgorithms() transparently resolves the alias to its real
    algorithm names. This is the main reason why the function returns a
    list instead of just a single algorithm object.

    If several providers exist for the same algorithm name, createAlgorithms()
    by default selects the first provider and creates only one algorithm
    object. Clients may specify to createAlgorithms() that they want all
    algorithm objects. This is the second reason why createAlgorithms() returns
    a list instead of just a single algorithm object.
    """

    @staticmethod
    def createAlgorithms(name, duplicateHashes = False):
        """Creates and returns a list of mkroesti.algorithm.AlgorithmInterface objects."""

        # Resolve alias (if it is one) or create the list with algorithm names
        # with a single entry
        algorithmNames = list()
        if name in ProviderRegistry.getInstance().getAliasNames():
            algorithmNames.extend(ProviderRegistry.getInstance().resolveAlias(name))
        else:
            algorithmNames.append(name)
        algorithmNames.sort()

        # Create algorithm objects
        algorithms = list()
        for algorithmName in algorithmNames:
            providers = ProviderRegistry.getInstance().getProviders(algorithmName)
            algorithmsCreated = 0
            for provider in providers:
                (isAvailable, reason) = provider.isAlgorithmAvailable(algorithmName)
                if not isAvailable:
                    continue
                if algorithmsCreated > 0 and not duplicateHashes:
                    continue
                algorithms.append(provider.createAlgorithm(algorithmName))
                algorithmsCreated += 1
        return algorithms

