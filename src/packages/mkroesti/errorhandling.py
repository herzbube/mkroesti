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


class ConversionError(Exception):
    """Is raised if conversion from str to bytes, or vice versa, fails."""

    def __init__(self, message):
        self.message = message
