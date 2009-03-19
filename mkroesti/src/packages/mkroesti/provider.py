# encoding=utf-8

"""Contains the ProviderInterface and AbstractProvider classes, as well as
a couple of concrete provider implementations.

Algorithm provider classes *must* implement ProviderInterface. See that class'
documentation for details. In addition, to make the algorithms they provide
known to the system, instances of algorithm provider classes *must* be
registered with mkroesti.registry.ProviderRegistry.

AbstractProvider derives from ProviderInterface. It is a base class that
concrete provider classes may inherit from. Besides default-implementing a few
methods of ProviderInterface, its main feature is that it registers the
provider class instance automatically with mkroesti.registry.ProviderRegistry.

It is recommended that concrete provider classes subclass AbstractProvider
and create an instance as illustrated in the following example:

  # Class declaration
  class ConcreteProvider(AbstractProvider):
    [...]
  # Create an instance right after class declaration has finished
  ConcreteProvider()
"""


# mkroesti
from mkroesti.registry import ProviderRegistry
from mkroesti import algorithm
from mkroesti.errorhandling import MKRoestiError
from mkroesti.names import *


class ProviderInterface:
    """Interface that must be implemented by algorithm provider classes.

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
    because some third party modules are missing.

    getAlgorithmSource() returns a string description of the implementation
    source that the provider uses for the named algorithm (e.g. "Python
    Standard Library module hashlib").

    An algorithm provider may place the algorithms it knows about into
    categories, also known as "aliases". getAliasNames() returns a list of
    aliases or categories that the provider knows about. resolveAlias()
    resolves a given alias name to the real algorithm names. Please note that
    providers do not need to (and in fact must not) handle the special alias
    ALIAS_ALL.

    Provider implementations may refer to constants in mkroesti.names for
    a set of predefined algorithm and alias names.

    To make the algorithms it provides known to the system, concrete algorithm
    provider classes must be instantiated and the instance must be added to
    mkroesti.registry.ProviderRegistry. The recommended approach is to subclass
    AbstractProvider (which automatically adds the provider instance to the
    registry) and create an instance like this:

      # Class declaration
      class ConcreteProvider(AbstractProvider):
        [...]
      # Create an instance right after class declaration has finished
      ConcreteProvider()
    """

    def getAlgorithmNames(self):
        """Returns a list of algorithm names that this provider knows about."""
        raise NotImplementedError

    def isAlgorithmKnown(self, algorithmName):
        """Returns True if the named algorithm is known to this provider."""
        raise NotImplementedError

    def getAvailableAlgorithmNames(self):
        """Returns a list of algorithm names that are available from this provider."""
        raise NotImplementedError

    def isAlgorithmAvailable(self, algorithmName):
        """Returns tuple of (boolean, string).

        The boolean part of the tuple indicates whether the named algorithm is
        available from this provider. If the algorithm is not available, the
        string part of the tuple should contain a reason why it is not
        available.
	"""
        raise NotImplementedError

    def getAlgorithmSource(self, algorithmName):
        """Returns description of the implementation source of the named algorithm."""
        raise NotImplementedError

    def createAlgorithm(self, algorithmName):
        """Returns algorithm object that implements the named algorithm.

        The algorithm object implements mkroesti.algorithm.AlgorithmInterface.
        """
        raise NotImplementedError

    def getAliasNames(self):
        """Returns a list of alias names that this provider knows about.

        The list must not include the special alias ALIAS_ALL.
        """
        raise NotImplementedError

    def resolveAlias(self, aliasName):
        """Returns a list of algorithm names that the named alias resolves to.

	The mkroesti system will never pass the alias ALIAS_ALL to this
	method, so this special alias does not need to be resolved.
        """
        raise NotImplementedError


class AbstractProvider(ProviderInterface):
    """Abstract base class that implements common features of provider classes.

    The main feature of this class is that it automatically registers the
    provider class instance automatically (i.e. during construction) with
    mkroesti.registry.ProviderRegistry.

    The default implementations of methods in AbstractProvider are based on
    the assumption that on construction subclasses specify a list of known
    algorithm names, and optionally a list of known alias names.
    """

    def __init__(self, algorithmNames):
        """Initializes this provider with a list of names of known algorithms and no known aliases."""
        self.__init__(algorithmNames, list())

    def __init__(self, algorithmNames, aliasNames):
        """Initialize with a list of names of known algorithms, and a list of names of known aliases."""
	if algorithmNames is not None:
            self.algorithmNames = algorithmNames
        else:
            self.algorithmNames = list()
	if aliasNames is not None:
            self.aliasNames = aliasNames
        else:
            self.aliasNames = list()
        ProviderRegistry.getInstance().addProvider(self)

    def getAlgorithmNames(self):
        """Returns the list of known algorithms specified on construction."""
        return self.algorithmNames

    def isAlgorithmKnown(self, algorithmName):
        """This default implementation uses the primitive getAlgorithmNames()."""
        algorithmNames = self.getAlgorithmNames()
        if algorithmName in algorithmNames:
            return True
        else:
            return False

    def getAvailableAlgorithmNames(self):
        """This default implementation combines the primitives
        getAlgorithmNames() and isAlgorithmAvailable().
        """
        availableAlgorithmNames = list()
        for algorithmName in self.getAlgorithmNames():
            (isAvailable, reason) = self.isAlgorithmAvailable(algorithmName)
            if isAvailable:
                availableAlgorithmNames.append(algorithmName)
        return availableAlgorithmNames

    def isAlgorithmAvailable(self, algorithmName):
        """This default implementation returns (True, None) if the given
        algorithm name is part of the list that the primitive
        getAlgorithmNames() returns. Otherwise this default implementation
        returns (False, "Unknown algorithm").
        """
        if algorithmName in self.getAlgorithmNames():
            return (True, None)
        else:
            return (False, "Unknown algorithm")

    def getAliasNames(self):
        """Returns the list of known aliases specified on construction."""
        return self.aliasNames


class DictAbstractProvider(AbstractProvider):
    """Allows subclasses to specify a dictionary on construction that maps
    known alias names to algorithm names.

    The dictionary expected by DictAbstractProvider.__init__() contains
    alias names as keys, and lists of algorithm names as values.

    If the null object (None) is one of the keys, DictAbstractProvider assumes
    that the associated algorithm names are not part of an alias.
    """

    def __init__(self, namesDictionary):
        """Initialize with a dictionary that maps known alias names to algorithm names."""
        self.namesDictionary = namesDictionary
        # Extract algorithm names
        algorithmNames = list()
        for algorithmNameList in dict.values(self.namesDictionary):
            algorithmNames.extend(algorithmNameList)
        # Remove null object key from dictionary ***BEFORE*** extracting alias
        # names, but ***AFTER*** extracting algorithm names
        if None in self.namesDictionary:
            del self.namesDictionary[None]
        # Extract alias names
        aliasNames = dict.keys(self.namesDictionary)
        # Submit to base class initializer
        AbstractProvider.__init__(self, algorithmNames, aliasNames)

    def resolveAlias(self, aliasName):
        if aliasName in self.namesDictionary:
            return self.namesDictionary[aliasName]
        raise MKRoestiError("Unknown alias " + aliasName)


class HashlibProvider(DictAbstractProvider):
    """Provides hashes available from the Python Standard Library module hashlib."""

    def __init__(self):
        namesDictionary = {
            None : [ALGORITHM_MD2, ALGORITHM_MD4, ALGORITHM_MD5],
            ALIAS_SHA : [ALGORITHM_SHA_0, ALGORITHM_SHA_1, ALGORITHM_SHA_224,
	        ALGORITHM_SHA_256, ALGORITHM_SHA_384, ALGORITHM_SHA_512],
            ALIAS_RIPEMD : [ALGORITHM_RIPEMD_160]
            }
        DictAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        return "hashlib"

    def createAlgorithm(self, algorithmName):
        return algorithm.HashlibAlgorithms(algorithmName, self)
HashlibProvider()


class Base64Provider(DictAbstractProvider):
    """Provides hashes/checksums available from the Python Standard Library module base64."""

    def __init__(self):
        namesDictionary = {
            ALIAS_CHKSUM : [ALGORITHM_BASE16, ALGORITHM_BASE32, ALGORITHM_BASE64]
            }
        DictAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        return "base64"

    def createAlgorithm(self, algorithmName):
        return algorithm.Base64Algorithms(algorithmName, self)
Base64Provider()


class ZlibProvider(DictAbstractProvider):
    """Provides hashes/checksums available from the Python Standard Library module zlib."""

    def __init__(self):
        namesDictionary = { ALIAS_CHKSUM : [ALGORITHM_ADLER32, ALGORITHM_CRC32] }
        DictAbstractProvider.__init__(self, namesDictionary)

    def getAlgorithmSource(self, algorithmName):
        return "zlib"

    def createAlgorithm(self, algorithmName):
        return algorithm.ZlibAlgorithms(algorithmName, self)
ZlibProvider()


class CryptProvider(DictAbstractProvider):
    """Provides crypt() based hashes."""

    def __init__(self):
        namesDictionary = { ALIAS_CRYPT : [ALGORITHM_CRYPT_SYSTEM, ALGORITHM_CRYPT_BLOWFISH] }
        DictAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        if ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            (isAvailable, moduleName) = algorithm.CryptBlowfishAlgorithm.isAvailable()
            if not isAvailable:
                return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        if ALGORITHM_CRYPT_SYSTEM == algorithmName:
            return "crypt"
        elif ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            return "bcrypt"
        else:
            raise MKRoestiError("Unknown algorithm " + algorithmName)

    def createAlgorithm(self, algorithmName):
        if ALGORITHM_CRYPT_SYSTEM == algorithmName:
            return algorithm.CryptAlgorithm(algorithmName, self)
        elif ALGORITHM_CRYPT_BLOWFISH == algorithmName:
            return algorithm.CryptBlowfishAlgorithm(algorithmName, self)
        else:
            raise MKRoestiError("Unknown algorithm " + algorithmName)
CryptProvider()


class WindowsHashProvider(DictAbstractProvider):
    """Provides LanManager and Windows NT password hashes."""

    def __init__(self):
        namesDictionary = { ALIAS_CHKSUM : [ALGORITHM_WINDOWS_LM, ALGORITHM_WINDOWS_NT] }
        DictAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        (isAvailable, moduleName) = algorithm.WindowsHashAlgorithms.isAvailable()
        if not isAvailable:
            return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "smbpasswd"

    def createAlgorithm(self, algorithmName):
        return algorithm.WindowsHashAlgorithms(algorithmName, self)
WindowsHashProvider()


class MHashProvider(DictAbstractProvider):
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
            ALIAS_TIGER : [ALGORITHM_TIGER_128, ALGORITHM_TIGER_160,
	        ALGORITHM_TIGER_192]
            }
        DictAbstractProvider.__init__(self, namesDictionary)

    def isAlgorithmAvailable(self, algorithmName):
        (isAvailable, moduleName) = algorithm.MHashAlgorithms.isAvailable()
        if not isAvailable:
            return (False, moduleName + " module not found")
        return (True, None)

    def getAlgorithmSource(self, algorithmName):
        return "mhash"

    def createAlgorithm(self, algorithmName):
        return algorithm.MHashAlgorithms(algorithmName, self)
MHashProvider()

