# encoding=utf-8

# mkroesti
from mkroesti import algorithm
from mkroesti import provider

# Define constants
ALIAS_NAME = "alias"
ALGORITHM_NAME_1 = "algorithm-name-1"
ALGORITHM_NAME_2 = "algorithm-name-2"
ALGORITHM_RESULT_1 = "algorithm-result-1"
ALGORITHM_RESULT_2 = "algorithm-result-2"
ALGORITHM_SOURCE_1 = "algorithm-source-1"
ALGORITHM_SOURCE_2 = "algorithm-source-2"


class AlgorithmStub(algorithm.AbstractAlgorithm):
    def __init__(self, algorithmName, provider):
        algorithm.AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_NAME_1 == algorithmName:
            ALGORITHM_RESULT_1
        elif ALGORITHM_NAME_2 == algorithmName:
            ALGORITHM_RESULT_2
        else:
            return algorithm.AbstractAlgorithm.getHash(self, input)


class ProviderStub(provider.DictAbstractProvider):
    def __init__(self):
        namesDictionary = {
            ALIAS_NAME : [ALGORITHM_NAME_1, ALGORITHM_NAME_2]
            }
        provider.DictAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        if ALGORITHM_NAME_1 == algorithmName:
            ALGORITHM_SOURCE_1
        elif ALGORITHM_NAME_2 == algorithmName:
            ALGORITHM_SOURCE_2
        else:
            return provider.DictAbstractProvider.getAlgorithmSource(self, algorithmName)

    def createAlgorithm(self, algorithmName):
        return AlgorithmStub(algorithmName, self)
