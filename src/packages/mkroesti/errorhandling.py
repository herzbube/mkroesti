# encoding=utf-8

"""Error handling stuff."""


class MKRoestiError(Exception):
    """General runtime error triggered by mkroesti."""

    def __init__(self, message):
        self.message = message


class UnknownAlgorithmError(Exception):
    """Is raised if a given algorithm is not known."""

    def __init__(self, algorithmName):
        self.message = "unknown algorithm: " + str(algorithmName)


class UnavailableAlgorithmError(Exception):
    """Is raised if a given algorithm is not available."""

    def __init__(self, algorithmName):
        self.message = "algorithm is not available: " + str(algorithmName)


class DuplicateAlgorithmError(Exception):
    """Is raised if a provider tries to provide the same algorithm multiple times."""

    def __init__(self, message):
        self.message = message


class UnknownAliasError(Exception):
    """Is raised if a given alias is not known."""

    def __init__(self, aliasName):
        self.message = "unknown alias: " + str(aliasName)


class DuplicateAliasError(Exception):
    """Is raised if a provider tries to provide the same alias multiple times."""

    def __init__(self, message):
        self.message = message


class DuplicateProviderError(Exception):
    """Is raised if the same provider is added to the registry multiple times."""

    def __init__(self, message):
        self.message = message


