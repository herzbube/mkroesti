"""Contains algorithm related classes.

AlgorithmFactory is used to create instances of algorithm classes based on the
algorithm's name. An algorithm class must derive from AlgorithmInterface and
upon instantiation must register its instances with the AlgorithmRegistry.

AbstractAlgorithm derives from AlgorithmInterface. It is a base class that
concrete algorithm classes may inherit from. It implements some useful features
such as registering with the AlgorithmRegistry singleton. Notably, it does not
implement the getHash() function.

AlgorithmRegistry is where algorithm objects register themselves and clients
get references to these algorithm objects. AlgorithmRegistry is a singleton.

Apart from the classes mentioned so far, this module contains a number of
concrete algorithm classes. These classes are not listed here. Clients should
not need to know about these concrete algorithm classes, instead they should
refer to algorithms by name.
"""


import base64
import crypt
import hashlib
from random import randint
import string
import zlib

import smbpasswd
import mhash

from mkroesti.errorhandling import MKRoestiError


class AlgorithmRegistry:
    """Registry where algorithm objects register themselves.

    AlgorithmRegistry uses an algorithm object's name to maintain the registry.
    Clients may retrieve an algorithm object by calling getAlgorithm() and
    specifying the algorithm name. Clients should use the interface defined by
    AlgorithmInterface to interact with the algorithm object.

    AlgorithmRegistry is a singleton. The singleton accessor (and creator)
    is AlgorithmRegistry.getInstance().
    """

    _instance = None

    @staticmethod
    def getInstance():
        """Access the singleton."""
        if None == AlgorithmRegistry._instance:
            AlgorithmRegistry()
        return AlgorithmRegistry._instance

    def __init__(self):
        """Create the singleton."""
        if None != AlgorithmRegistry._instance:
            raise MKRoestiError("Only one instance of AlgorithmRegistry is allowed!")
        AlgorithmRegistry._instance = self
        self.algorithms = dict()

    def getAlgorithm(self, name):
        """Returns the algorithm object that implements the algorithm name."""
        if not name in self.algorithms:
            raise MKRoestiError("Unknown algorithm " + name)
        return self.algorithms[name]

    def addAlgorithm(self, algorithm):
        """Adds an algorithm objects to this registry."""
        if algorithm.name in self.algorithms:
            raise MKRoestiError("Algorithms can be registered only once!")
        if not isinstance(algorithm, AlgorithmInterface):
            raise MKRoestiError(str(algorithm) + " is not derived from AlgorithmInterface!")
        self.algorithms[algorithm.name] = algorithm


class AlgorithmInterface:
    """Interface that must be implemented by algorithm classes."""

    def getName(self):
        """Returns a string that is the name of the algorithm."""
        raise NotImplementedError

    def getHash(self, input):
        """Returns a string that is the result of the algorithm hashing input."""
        raise NotImplementedError


class AbstractAlgorithm(AlgorithmInterface):
    """Abstract base class that implements common features of algorithm classes."""

    def __init__(self, name):
        self.name = name
        AlgorithmRegistry.getInstance().addAlgorithm(self)

    def getName(self):
        return self.name


class Base16Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "base16")

    def getHash(self, input):
        return base64.b16encode(input)


class Base32Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "base32")

    def getHash(self, input):
        return base64.b32encode(input)


class Base64Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "base64")

    def getHash(self, input):
        return base64.b64encode(input)


class Adler32Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "adler32")

    def getHash(self, input):
        # TODO should return an unsigned hex value
        return zlib.adler32(input)


class CRC32Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "crc32")

    def getHash(self, input):
        # TODO should return an unsigned hex value
        return zlib.crc32(input)


class MD5Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "md5")

    def getHash(self, input):
        algorithm = hashlib.md5(input)
        return algorithm.hexdigest()


class SHA1Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-1")

    def getHash(self, input):
        algorithm = hashlib.sha1(input)
        return algorithm.hexdigest()


class SHA224Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-224")

    def getHash(self, input):
        algorithm = hashlib.sha224(input)
        return algorithm.hexdigest()


class SHA256Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-256")

    def getHash(self, input):
        algorithm = hashlib.sha256(input)
        return algorithm.hexdigest()


class SHA384Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-384")

    def getHash(self, input):
        algorithm = hashlib.sha384(input)
        return algorithm.hexdigest()


class SHA512Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-512")

    def getHash(self, input):
        algorithm = hashlib.sha512(input)
        return algorithm.hexdigest()


class OpenSSLAlgorithm(AbstractAlgorithm):
    """Generic class that provides access to OpenSSL algorithms by name.

    Use the supportsAlgorithm() method to check whether you can create an
    instance of OpenSSLAlgorithm using the given name.
    """
    
    def __init__(self, name):
        AbstractAlgorithm.__init__(self, name)

    def getHash(self, input):
        opensslAlgorithmName = OpenSSLAlgorithm.mapAlgorithmName(self.getName())
        algorithm = hashlib.new(opensslAlgorithmName)
        algorithm.update(input)
        return algorithm.hexdigest()

    @staticmethod
    def mapAlgorithmName(mkroestiName):
        if "ripemd-160" == mkroestiName:
           return "rmd160"
        if "sha-0" == mkroestiName:
           return "sha"
        elif "md2" == mkroestiName or \
             "md4" == mkroestiName:
           return mkroestiName
        else:
           return None

    @staticmethod
    def supportsAlgorithm(name):
       if OpenSSLAlgorithm.mapAlgorithmName(name) is not None:
           return True
       else:
          return False


class MHashAlgorithm(AbstractAlgorithm):
    """Generic class that provides access to mhash algorithms by name.

    Use the supportsAlgorithm() method to check whether you can create an
    instance of MHashAlgorithm using the given name.
    """
    
    def __init__(self, name):
        AbstractAlgorithm.__init__(self, name)

    def getHash(self, input):
        mhashAlgorithmName = MHashAlgorithm.mapAlgorithmName(self.getName())
        algorithm = mhash.MHASH(mhashAlgorithmName)
        algorithm.update(input)
        return algorithm.hexdigest()

    @staticmethod
    def mapAlgorithmName(mkroestiName):
        if "sha-1" == mkroestiName:
           return mhash.MHASH_SHA1
        elif "sha-224" == mkroestiName:
           return mhash.MHASH_SHA224
        elif "sha-256" == mkroestiName:
           return mhash.MHASH_SHA256
        elif "sha-384" == mkroestiName:
           return mhash.MHASH_SHA384
        elif "sha-512" == mkroestiName:
           return mhash.MHASH_SHA512
        elif "ripemd-128" == mkroestiName:
           return mhash.MHASH_RIPEMD128
        elif "ripemd-160" == mkroestiName:
           return mhash.MHASH_RIPEMD160
        elif "ripemd-256" == mkroestiName:
           return mhash.MHASH_RIPEMD256
        elif "ripemd-320" == mkroestiName:
           return mhash.MHASH_RIPEMD320
        elif "haval-128-3" == mkroestiName:
           return mhash.MHASH_HAVAL128
        elif "haval-160-3" == mkroestiName:
           return mhash.MHASH_HAVAL160
        elif "haval-192-3" == mkroestiName:
           return mhash.MHASH_HAVAL192
        elif "haval-224-3" == mkroestiName:
           return mhash.MHASH_HAVAL224
        elif "haval-256-3" == mkroestiName:
           return mhash.MHASH_HAVAL256
        elif "snefru-128" == mkroestiName:
           return mhash.MHASH_SNEFRU128
        elif "snefru-256" == mkroestiName:
           return mhash.MHASH_SNEFRU256
        elif "tiger-128" == mkroestiName:
           return mhash.MHASH_TIGER128
        elif "tiger-160" == mkroestiName:
           return mhash.MHASH_TIGER160
        elif "tiger-192" == mkroestiName:
           return mhash.MHASH_TIGER
        elif "whirlpool" == mkroestiName:
           return mhash.MHASH_WHIRLPOOL
        elif "gost" == mkroestiName:
           return mhash.MHASH_GOST
        elif "adler32" == mkroestiName:
           return mhash.MHASH_ADLER32
        elif "crc32" == mkroestiName:
           return mhash.MHASH_CRC32
        elif "crc32b" == mkroestiName:
           return mhash.MHASH_CRC32B
        elif "md2" == mkroestiName:
           return mhash.MHASH_MD2
        elif "md4" == mkroestiName:
           return mhash.MHASH_MD4
        elif "md5" == mkroestiName:
           return mhash.MHASH_MD5
        else:
           return None

    @staticmethod
    def supportsAlgorithm(name):
       if MHashAlgorithm.mapAlgorithmName(name) is not None:
           return True
       else:
          return False


class WindowsLMAlgorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "windows-lm")

    def getHash(self, input):
        return smbpasswd.lmhash(input)


class WindowsNTAlgorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "windows-nt")

    def getHash(self, input):
        return smbpasswd.nthash(input)


class CryptAlgorithm(AbstractAlgorithm):
    salt_chars = './' + string.ascii_letters + string.digits

    def __init__(self):
        AbstractAlgorithm.__init__(self, "crypt")

    def getHash(self, input):
        # As described in the docs of the crypt module:
	#   salt is usually a random two-character string which will be used
	#   to perturb the DES algorithm in one of 4096 ways. The characters
	#   in salt must be in the set [./a-zA-Z0-9].
        # The following implementation of generating the salt is taken verbatim
	# (with the exception of fixing a typo) from this mailing list post:
	#   http://mail.python.org/pipermail/python-list/2004-March/252058.html
	salt = CryptAlgorithm.salt_chars[randint(0, 63)] + CryptAlgorithm.salt_chars[randint(0, 63)]
        return crypt.crypt(input, salt)


class AlgorithmFactory:
    """Factory class that instantiates algorithm classes."""

    @staticmethod
    def resolveAliases(algorithmNames):
        """Resolves aliases to real algorithm names.

        algorithmNames is expected to be a list of strings. The return value is
        a list whose members correspond to those of the input list
        algorithmNames. Any members that were aliases have been replaced by the
        real algorithm names that the alias refers to.
        """

        returnList = list()
        for algorithmName in algorithmNames:
            if "all" == algorithmName:
                returnList.append("crypt")
                returnList.append("apr1")
                returnList.append("md2")
                returnList.append("md4")
                returnList.append("md5")
                returnList.append("whirlpool")
                returnList.append("windows-lm")
                returnList.append("windows-nt")
                returnList.append("mysql-password")
                returnList.extend(AlgorithmFactory.resolveAliases(["chksum"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["sha"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["ripemd"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["haval"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["tiger"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["snefru"]))
            elif "sha" == algorithmName:
                returnList.append("sha-0")
                returnList.append("sha-1")
                returnList.append("sha-224")
                returnList.append("sha-256")
                returnList.append("sha-384")
                returnList.append("sha-512")
            elif "ripemed" == algorithmName:
                returnList.append("ripemd")
                returnList.append("ripemd-128")
                returnList.append("ripemd-160")
                returnList.append("ripemd-256")
                returnList.append("ripemd-320")
            elif "haval" == algorithmName:
                returnList.append("haval-128-3")
                returnList.append("haval-128-4")
                returnList.append("haval-128-5")
                returnList.append("haval-160-3")
                returnList.append("haval-160-4")
                returnList.append("haval-160-5")
                returnList.append("haval-192-3")
                returnList.append("haval-192-4")
                returnList.append("haval-192-5")
                returnList.append("haval-224-3")
                returnList.append("haval-224-4")
                returnList.append("haval-224-5")
                returnList.append("haval-256-3")
                returnList.append("haval-256-4")
                returnList.append("haval-256-5")
            elif "tiger" == algorithmName:
                # TODO actually "tiger" should refer to tiger-192; we should
                # provide a different alias for referring to "all tiger algos",
                # for instance "tiger-all"
                returnList.append("tiger-128")
                returnList.append("tiger-160")
                returnList.append("tiger-192")
                returnList.append("tiger2")
            elif "snefru" == algorithmName:
                returnList.append("snefru-128")
                returnList.append("snefru-256")
            elif "chksum" == algorithmName:
                returnList.append("base16")
                returnList.append("base32")
                returnList.append("base64")
                returnList.append("adler32")
                returnList.append("crc32")
                returnList.append("crc32b")
            else:
                returnList.append(algorithmName)
        return returnList

    @staticmethod
    def createAlgorithms(algorithmNames):
        """Creates objects that implement the named algorithms.
        
        algorithmNames is expected to be a list of algorithm names. Each name is
        examined whether it is an alias, and, if it is, the alias is replaced by
        the real algorithm names that it refers to.

        Once all aliases have been resolved, instances of those algorithm
        classes that implement the named algorithms are created. The resulting
        algorithm objects register themselves with the AlgorithmRegistry
        singleton from where they can later be retrieved to perform hashing and
        other operations.

        This method returns a list of algorithm names for which objects were
        created. The list contains no aliases.
        """

        algorithmNames = AlgorithmFactory.resolveAliases(algorithmNames)
        # TODO: Check for names that appear multiple times and raise an
        # appropriate error. The current behaviour is that the registry
        # complains about algorithms registering multiple times, which might
        # confuse the user.
        for algorithmName in algorithmNames:
            if "base16" == algorithmName:
                Base16Algorithm()
            elif "base32" == algorithmName:
                Base32Algorithm()
            elif "base64" == algorithmName:
                Base64Algorithm()
# TODO disabled zlib variant because it returns strange/incorrect results
#            elif "adler32" == algorithmName:
#                Adler32Algorithm()
#            elif "crc32" == algorithmName:
#                CRC32Algorithm()
            elif "md5" == algorithmName:
                MD5Algorithm()
            elif "sha-1" == algorithmName:
                SHA1Algorithm()
            elif "sha-224" == algorithmName:
                SHA224Algorithm()
            elif "sha-256" == algorithmName:
                SHA256Algorithm()
            elif "sha-384" == algorithmName:
                SHA384Algorithm()
            elif "sha-512" == algorithmName:
                SHA512Algorithm()
            elif OpenSSLAlgorithm.supportsAlgorithm(algorithmName):
                OpenSSLAlgorithm(algorithmName)
            elif MHashAlgorithm.supportsAlgorithm(algorithmName):
                MHashAlgorithm(algorithmName)
            elif "windows-lm" == algorithmName:
                WindowsLMAlgorithm()
            elif "windows-nt" == algorithmName:
                WindowsNTAlgorithm()
            elif "crypt" == algorithmName:
                CryptAlgorithm()
            else:
                # TODO: Check for not-yet-implemented algorithms.
                raise MKRoestiError("Unknown algorithm " + algorithmName)
        return algorithmNames
