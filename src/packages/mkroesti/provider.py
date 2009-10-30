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


"""Contains the ProviderInterface, AbstractProvider and AliasAbstractProvider
classes, as well as a couple of concrete provider implementations.

Algorithm provider classes *must* implement ProviderInterface (although they do
not need to inherit from it). See the class' documentation for details. In
addition, instances of algorithm provider classes *must* be registered so that
the algorithms they provide become known to the mkroesti system. Provider
instances injected into the system by third party Python modules via the
--providers command line option are automatically registered. All other
hacking attempts should use the following convenience functions for
registration:

    import mkroesti
    mkroesti.registerProvider(aProvider)
    mkroesti.registerProviders(providerList)

AbstractProvider derives from ProviderInterface. It is a base class that
concrete provider classes may inherit from. It provides useful default
implementations for most of the methods of ProviderInterface.

AliasAbstractProvider extends AbstractProvider with support for aliases.
Subclasses must provide a dictionary that maps alias to algorithm names.
For instance:

    class ConcreteProvider(AliasAbstractProvider):
        def __init__(self):
            namesDictionary = {
                None     : ["algorithm1", "algorithm2", "algorithm3"]
                "alias1" : ["algorithm4", "algorithm5", "algorithm5"]
                "alias2" : ["algorithm6"]
                }
            AliasAbstractProvider.__init__(self, namesDictionary)
        [...]
"""


# PSL
import copy

# mkroesti
from mkroesti import algorithm
from mkroesti.errorhandling import * #@UnusedWildImport
from mkroesti.names import * #@UnusedWildImport


class ProviderInterface:
    """Interface that must be implemented by algorithm provider classes.

    The main purpose of the class ProviderInterface is to document the
    interface. In the spirit of duck typing, a concrete provider class is not
    required to inherit from ProviderInterface (although it automatically does
    if it inherits from AbstractProvider or AliasAbstractProvider).

    An algorithm provider knows about 1-n algorithms. Algorithms are identified
    by their name. getAlgorithmNames() returns a list of names of those
    algorithms that the provider knows about. The names in the list must be
    unique, i.e. a provider cannot know two different algorithms under the same
    name (duh!).
    
    isAlgorithmKnown() can be used to query the provider whether it knows about
    an algorithm with a certain name. isAlgorithmAvailable() can be used to
    query the provider if an algorithm that it knows about is actually
    available (and the reason if it is not). The difference between "known" and
    "available" is that sometimes a provider knows how to provide a certain
    algorithm "in theory", but is unable to do so in the current environment
    because some third party modules are missing. Finally, the convenience
    method getAvailableAlgorithmNames() returns a list of known algorithms that
    are actually available.

    getAlgorithmSource() returns a string description of the implementation
    source that the provider uses for the named algorithm (e.g. "Python
    Standard Library module hashlib").

    An algorithm provider may place the algorithms it knows about into
    categories, also known as "aliases". getAliasNames() returns a list of
    aliases or categories that the provider knows about. resolveAlias()
    resolves a given alias name to the real algorithm names. Alias resolution
    ignores algorithms that are not available. Please note that providers must
    not handle the special alias ALIAS_ALL in any way.

    In the same way as there are known and available algorithms (see above),
    there are also known and available aliases. The methods isAliasKnown(),
    isAliasAvailable() and getAvailableAliasNames() support this distinction.
    An alias is available if one or more algorithms that it resolves to is
    available.

    Provider implementations may refer to constants in mkroesti.names for
    a set of predefined algorithm and alias names.

    To make the algorithms it provides known to the system, concrete algorithm
    provider classes must be instantiated and the instance must be registered.
    Provider instances injected into the system by third party Python modules
    via the --providers command line option are automatically registered. All
    other hacking attempts should use the following convenience functions for
    registration:

        import mkroesti
        mkroesti.registerProvider(aProvider)
        mkroesti.registerProviders(providerList)
    """

    def getAlgorithmNames(self):
        """Returns a list of algorithm names that this provider knows about."""
        raise NotImplementedError

    def isAlgorithmKnown(self, algorithmName):
        """Returns True if the given algorithm is known to this provider."""
        raise NotImplementedError

    def getAvailableAlgorithmNames(self):
        """Returns a list of algorithm names that are available from this provider."""
        raise NotImplementedError

    def isAlgorithmAvailable(self, algorithmName):
        """Returns tuple of (boolean, string).

        The boolean part of the tuple indicates whether the given algorithm is
        available. If the algorithm is not available, the string part of the
        tuple should contain a reason why it is not available.

        If this provider does not know about the given algorithm in the first
        place, it raises an UnknownAlgorithmError.
        """
        raise NotImplementedError

    def getAlgorithmSource(self, algorithmName):
        """Returns description of the implementation source of the given algorithm.

        If this provider does not know about the given algorithm, it raises an
        UnknownAlgorithmError.
        """
        raise NotImplementedError

    def createAlgorithm(self, algorithmName):
        """Returns algorithm object that implements the given algorithm.

        The algorithm object must implement
        mkroesti.algorithm.AlgorithmInterface.

        If this provider does not know about the given algorithm, it raises an
        UnknownAlgorithmError. If the algorithm is not available, this provider
        raises an UnavailableAlgorithmError.
        """
        raise NotImplementedError

    def getAliasNames(self):
        """Returns a list of alias names that this provider knows about.

        If this provider does not know any aliases, it returns an empty list.

        The list must not include the special alias ALIAS_ALL.
        """
        raise NotImplementedError

    def isAliasKnown(self, aliasName):
        """Returns True if the given alias is known to this provider."""
        raise NotImplementedError

    def getAvailableAliasNames(self):
        """Returns a list of alias names that are available from this provider."""
        raise NotImplementedError

    def isAliasAvailable(self, aliasName):
        """Returns True if the given alias is available from this provider.

        If this provider does not know about the given alias in the first
        place, it raises an UnknownAliasError.
        """
        raise NotImplementedError

    def resolveAlias(self, aliasName):
        """Returns a list of available algorithm names that the given alias
        resolves to.

        If this provider does not know about the given alias, it raises an
        UnknownAliasError. If the alias is not available, this provider raises
        an UnavailableAliasError.

        The mkroesti system will never pass the alias ALIAS_ALL to this
        method, so this special alias does not need to (and in fact *must* not)
        be resolved. Since providers are forbidden to use ALIAS_ALL, this
        implies that passing ALIAS_ALL to this method will always result in
        UnknownAliasError being raised.  
        """
        raise NotImplementedError


class AbstractProvider(ProviderInterface):
    """Abstract base class that implements common features of provider classes.

    The default implementations of methods in AbstractProvider are based on
    the assumption that on construction subclasses specify a list of known
    algorithm names.
    """

    def __init__(self, algorithmNames = list()):
        """Initialize with a list of names of known algorithms."""
        if len(algorithmNames) == 0:
            raise MKRoestiError("Must provide at least 1 algorithm")
        if len(algorithmNames) != len(set(algorithmNames)):
            raise DuplicateAlgorithmError("Algorithm names must be unique")
        self.algorithmNames = algorithmNames[:]   # make a copy

    def getAlgorithmNames(self):
        """Returns the list of known algorithms specified on construction."""
        return self.algorithmNames[:]   # make a copy

    def isAlgorithmKnown(self, algorithmName):
        """This default implementation uses the primitive getAlgorithmNames()."""
        return (algorithmName in self.getAlgorithmNames())

    def getAvailableAlgorithmNames(self):
        """This default implementation combines the primitives
        getAlgorithmNames() and isAlgorithmAvailable().
        """
        availableAlgorithmNames = list()
        for algorithmName in self.getAlgorithmNames():
            (isAvailable, reason) = self.isAlgorithmAvailable(algorithmName) #@UnusedVariable
            if isAvailable:
                availableAlgorithmNames.append(algorithmName)
        return availableAlgorithmNames

    def isAlgorithmAvailable(self, algorithmName):
        """This default implementation returns (True, None) if the given
        algorithm name is part of the list that the primitive
        getAlgorithmNames() returns. Otherwise this default implementation
        raises UnknownAlgorithmError.
        """
        if algorithmName in self.getAlgorithmNames():
            return (True, None)
        else:
            raise UnknownAlgorithmError(algorithmName)

    def getAliasNames(self):
        """This default implementation returns an empty list, assuming that
        this provider knows no aliases.
        """
        return list()

    def isAliasKnown(self, aliasName):
        """This default implementation returns False, assuming that this
        provider knows no aliases.
        """
        return False


class AliasAbstractProvider(AbstractProvider):
    """Extends AbstractProvider with alias support.

    Allows subclasses to specify a dictionary on construction that maps
    known alias names to algorithm names.

    The dictionary expected by AliasAbstractProvider.__init__() contains
    alias names as keys, and lists of algorithm names as values.

    If the null object (None) is one of the keys, AliasAbstractProvider assumes
    that the associated algorithm names are not part of an alias.
    """

    def __init__(self, namesDictionary):
        """Initialize with a dictionary that maps alias to algorithm names."""
        
        # Make a deep copy a) because we possibly modify the dict by removing
        # key None, and b) because we want to become independent from what
        # our clients do with their own reference to the dictionary
        self.namesDictionary = copy.deepcopy(namesDictionary)
        # Extract algorithm names
        algorithmNames = list()
        for algorithmNameList in self.namesDictionary.values():
            algorithmNames.extend(algorithmNameList)
        # Remove null object key from dictionary ***BEFORE*** extracting alias
        # names, but ***AFTER*** extracting algorithm names
        if None in self.namesDictionary:
            del self.namesDictionary[None]
        # Extract alias names
        self.aliasNames = self.namesDictionary.keys()
        if ALIAS_ALL in self.aliasNames:
            raise MKRoestiError("Aliases must not include the special alias name '" + ALIAS_ALL + "'")
        # Submit to base class initializer
        AbstractProvider.__init__(self, algorithmNames)

    def getAliasNames(self):
        # In Python 3, self.aliasNames is a "view" object because it was
        # created by dict.keys(), but our interface says we must return a list
        # object. Use list() to explicitly return a list object.
        return list(self.aliasNames)   # make a copy

    def isAliasKnown(self, aliasName):
        """This default implementation uses the primitive getAliasNames()."""
        return (aliasName in self.getAliasNames())

    def getAvailableAliasNames(self):
        """This default implementation combines the primitives getAliasNames()
        and isAliasAvailable().
        """
        availableAliasNames = list()
        for aliasName in self.getAliasNames():
            if self.isAliasAvailable(aliasName):
                availableAliasNames.append(aliasName)
        return availableAliasNames

    def isAliasAvailable(self, aliasName):
        """This default implementation combines the primitives resolveAlias()
        and isAlgorithmAvailable().
        """
        isAvailable = True
        try:
            self.resolveAlias(aliasName)
        except UnavailableAliasError:
            isAvailable = False
        return isAvailable

    def resolveAlias(self, aliasName):
        if aliasName in self.namesDictionary:
            availableAlgorithmNames = list()
            for algorithmName in self.namesDictionary[aliasName]:
                # Only include algorithms that are available
                (isAvailable, reason) = self.isAlgorithmAvailable(algorithmName) #@UnusedVariable
                if isAvailable:
                    availableAlgorithmNames.append(algorithmName)
            if len(availableAlgorithmNames) is 0:
                raise UnavailableAliasError(aliasName)
            return availableAlgorithmNames
        # Do not handle ALIAS_ALL
        raise UnknownAliasError(aliasName)


class HashlibProvider(AliasAbstractProvider):
    """Provides hashes available from the Python Standard Library module hashlib."""

    def __init__(self):
        namesDictionary = {
            None : [ALGORITHM_MD2, ALGORITHM_MD4, ALGORITHM_MD5],
            ALIAS_SHA : [ALGORITHM_SHA_0, ALGORITHM_SHA_1, ALGORITHM_SHA_224,
                         ALGORITHM_SHA_256, ALGORITHM_SHA_384, ALGORITHM_SHA_512],
            ALIAS_RIPEMD : [ALGORITHM_RIPEMD_160]
            }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        isAvailable = algorithm.HashlibAlgorithms.isAvailable(algorithmName)
        if not isAvailable:
            return (False, "not supported by this sytem's OpenSSL library")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "hashlib"

    def createAlgorithm(self, algorithmName):
        return algorithm.HashlibAlgorithms(algorithmName, self)


class Base64Provider(AliasAbstractProvider):
    """Provides hashes/encodings available from the Python Standard Library module base64."""

    def __init__(self):
        namesDictionary = {
            ALIAS_ENCODING : [ALGORITHM_BASE16, ALGORITHM_BASE32, ALGORITHM_BASE64]
            }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        return "base64"

    def createAlgorithm(self, algorithmName):
        return algorithm.Base64Algorithms(algorithmName, self)


class ZlibProvider(AliasAbstractProvider):
    """Provides hashes/checksums available from the Python Standard Library module zlib."""

    def __init__(self):
        namesDictionary = { ALIAS_CHKSUM : [ALGORITHM_ADLER32, ALGORITHM_CRC32B] }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        return "zlib"

    def createAlgorithm(self, algorithmName):
        return algorithm.ZlibAlgorithms(algorithmName, self)


class CryptProvider(AliasAbstractProvider):
    """Provides crypt(3) based hashes."""

    def __init__(self):
        namesDictionary = {
            ALIAS_CRYPT : [ALGORITHM_CRYPT_DES, ALGORITHM_CRYPT_MD5,
                           ALGORITHM_CRYPT_SHA_256, ALGORITHM_CRYPT_SHA_512,
                           ALGORITHM_CRYPT_BLOWFISH]
            }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        if algorithmName in (ALGORITHM_CRYPT_DES, ALGORITHM_CRYPT_MD5,
                             ALGORITHM_CRYPT_SHA_256, ALGORITHM_CRYPT_SHA_512):
            isAvailable = algorithm.CryptAlgorithm.isAvailable(algorithmName)
            if not isAvailable:
                return (False, "not supported by this sytem's crypt(3)")
            return (True, None)
        elif ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            (isAvailable, moduleName) = algorithm.CryptBlowfishAlgorithm.isAvailable()
            if not isAvailable:
                return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        if algorithmName in (ALGORITHM_CRYPT_DES, ALGORITHM_CRYPT_MD5,
                             ALGORITHM_CRYPT_SHA_256, ALGORITHM_CRYPT_SHA_512):
            return "crypt"
        elif ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            return "bcrypt"
        else:
            raise MKRoestiError("Unknown algorithm " + algorithmName)

    def createAlgorithm(self, algorithmName):
        if algorithmName in (ALGORITHM_CRYPT_DES, ALGORITHM_CRYPT_MD5,
                             ALGORITHM_CRYPT_SHA_256, ALGORITHM_CRYPT_SHA_512):
            return algorithm.CryptAlgorithm(algorithmName, self)
        elif ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            return algorithm.CryptBlowfishAlgorithm(algorithmName, self)
        else:
            raise MKRoestiError("Unknown algorithm " + algorithmName)


class WindowsHashProvider(AliasAbstractProvider):
    """Provides windows-lm and windows-nt hashes."""

    def __init__(self):
        namesDictionary = { ALIAS_CHKSUM : [ALGORITHM_WINDOWS_LM, ALGORITHM_WINDOWS_NT] }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        (isAvailable, moduleName) = algorithm.WindowsHashAlgorithms.isAvailable()
        if not isAvailable:
            return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "smbpasswd"

    def createAlgorithm(self, algorithmName):
        return algorithm.WindowsHashAlgorithms(algorithmName, self)


class MHashProvider(AliasAbstractProvider):
    """Provides hashes available from the third party module mhash."""

    def __init__(self):
        namesDictionary = {
            None : [ALGORITHM_MD2, ALGORITHM_MD4, ALGORITHM_MD5,
                    ALGORITHM_WHIRLPOOL, ALGORITHM_GOST],
            ALIAS_CHKSUM : [ALGORITHM_ADLER32, ALGORITHM_CRC32, ALGORITHM_CRC32B],
            ALIAS_SHA : [ALGORITHM_SHA_1, ALGORITHM_SHA_224, ALGORITHM_SHA_256,
                         ALGORITHM_SHA_384, ALGORITHM_SHA_512],
            ALIAS_RIPEMD : [ALGORITHM_RIPEMD_128, ALGORITHM_RIPEMD_160,
                            ALGORITHM_RIPEMD_256, ALGORITHM_RIPEMD_320],
            ALIAS_HAVAL : [ALGORITHM_HAVAL_128_3, ALGORITHM_HAVAL_160_3,
                           ALGORITHM_HAVAL_192_3, ALGORITHM_HAVAL_224_3,
                           ALGORITHM_HAVAL_256_3],
            ALIAS_SNEFRU : [ALGORITHM_SNEFRU_128, ALGORITHM_SNEFRU_256],
            ALIAS_TIGER : [ALGORITHM_TIGER_128_3, ALGORITHM_TIGER_160_3,
                           ALGORITHM_TIGER_192_3]
            }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        (isAvailable, moduleName) = algorithm.MHashAlgorithms.isAvailable()
        if not isAvailable:
            return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "mhash"

    def createAlgorithm(self, algorithmName):
        return algorithm.MHashAlgorithms(algorithmName, self)


class AprMD5Provider(AliasAbstractProvider):
    """Provides hashes available from the third party module aprmd5."""

    def __init__(self):
        namesDictionary = {
            None : [ALGORITHM_MD5],
            ALIAS_CRYPT : [ALGORITHM_CRYPT_APR1]
            }
        AliasAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        (isAvailable, moduleName) = algorithm.AprMD5Algorithms.isAvailable()
        if not isAvailable:
            return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "aprmd5"

    def createAlgorithm(self, algorithmName):
        return algorithm.AprMD5Algorithms(algorithmName, self)


def getProviders():
    providers = HashlibProvider(), Base64Provider(), ZlibProvider(), \
        CryptProvider(), WindowsHashProvider(), MHashProvider(), \
        AprMD5Provider()
    return providers
