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


"""Contains the AlgorithmFactory class."""


# mkroesti
from mkroesti.registry import ProviderRegistry
from mkroesti.errorhandling import UnknownAlgorithmError, UnavailableAlgorithmError


class AlgorithmFactory:
    """Factory that creates algorithm objects.

    Algorithm objects are instances of classes that implement
    mkroesti.algorithm.AlgorithmInterface (they do not necessarily inherit
    from that class).

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
    by default selects one of them (there is no guarantee which one) and creates
    only one algorithm object, using the selected provider. Clients, however,
    may override this behaviour and request that they want all algorithm
    objects. This is the second reason why createAlgorithms() returns a list
    instead of just a single algorithm object.
    """

    @staticmethod
    def createAlgorithms(name = None, duplicateHashes = False):
        """Creates and returns a list of algorithm objects for the given name.

        If the given name refers to a known alias, the alias is resolved to
        its real algorithm names. Of these, algorithm objects are created only
        for those algorithms that are actually available.
        
        If the given name refers to a known algorithm, but the algorithm is
        not available, an UnavailableAlgorithmError is raised.

        If the given name neither refers to a known alias, nor to a known 
        algorithm, an UnknownAlgorithmError is raised.
        """

        # Resolve alias (if it is one) or create the list with algorithm names
        # with a single entry
        algorithmNames = list()
        if name in ProviderRegistry.getInstance().getAliasNames():
            algorithmNames.extend(ProviderRegistry.getInstance().resolveAlias(name))
        elif ProviderRegistry.getInstance().isAlgorithmKnown(name):
            if ProviderRegistry.getInstance().isAlgorithmAvailable(name):
                algorithmNames.append(name)
            else:
                raise UnavailableAlgorithmError(name)
        else:
            raise UnknownAlgorithmError(name)

        # Create algorithm objects
        algorithms = list()
        for algorithmName in algorithmNames:
            providers = ProviderRegistry.getInstance().getProviders(algorithmName)
            algorithmsCreated = 0
            for provider in providers:
                # Must check for availability in case the original name was an
                # alias, in which case alias resolution has given us all known
                # algorithms, even if they are unavailable
                (isAvailable, reason) = provider.isAlgorithmAvailable(algorithmName) #@UnusedVariable
                if not isAvailable:
                    continue
                if algorithmsCreated > 0 and not duplicateHashes:
                    break
                algorithms.append(provider.createAlgorithm(algorithmName))
                algorithmsCreated += 1
        return algorithms

